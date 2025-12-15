#!/usr/bin/env python3
"""
LSP Client - Production-grade LSP server manager for Claude Code
Provides direct LSP access via CLI with daemon mode for persistent servers.

Architecture:
- Daemon process keeps language servers warm across invocations
- Unix socket IPC for fast client-daemon communication
- Graceful degradation to direct mode if daemon unavailable
"""
import subprocess
import json
import sys
import os
import socket
import signal
import atexit
import time
import threading
import queue
import logging
from pathlib import Path
from typing import Optional, Any, TypedDict
from dataclasses import dataclass, field
from contextlib import contextmanager
from urllib.parse import unquote as url_unquote

# Configuration
SOCKET_PATH = Path("/tmp/claude-lsp-daemon.sock")
PID_FILE = Path("/tmp/claude-lsp-daemon.pid")
LOG_FILE = Path("/tmp/claude-lsp-daemon.log")
DAEMON_TIMEOUT = 3600  # Auto-shutdown after 1 hour of inactivity
REQUEST_TIMEOUT = 30

# Server configurations by file extension
SERVERS: dict[str, dict[str, Any]] = {
    ".py": {"command": "pylsp", "args": [], "language_id": "python"},
    ".ts": {"command": "typescript-language-server", "args": ["--stdio"], "language_id": "typescript"},
    ".tsx": {"command": "typescript-language-server", "args": ["--stdio"], "language_id": "typescriptreact"},
    ".js": {"command": "typescript-language-server", "args": ["--stdio"], "language_id": "javascript"},
    ".jsx": {"command": "typescript-language-server", "args": ["--stdio"], "language_id": "javascriptreact"},
}

# LSP symbol kinds for pretty output
SYMBOL_KINDS = {
    1: "File", 2: "Module", 3: "Namespace", 4: "Package", 5: "Class",
    6: "Method", 7: "Property", 8: "Field", 9: "Constructor", 10: "Enum",
    11: "Interface", 12: "Function", 13: "Variable", 14: "Constant",
    15: "String", 16: "Number", 17: "Boolean", 18: "Array", 19: "Object",
    20: "Key", 21: "Null", 22: "EnumMember", 23: "Struct", 24: "Event",
    25: "Operator", 26: "TypeParameter"
}

# Configure logging
def setup_logging(daemon_mode: bool = False) -> logging.Logger:
    logger = logging.getLogger("lsp-client")
    logger.setLevel(logging.DEBUG if os.environ.get("LSP_DEBUG") else logging.INFO)

    if daemon_mode:
        handler = logging.FileHandler(LOG_FILE)
    else:
        handler = logging.StreamHandler(sys.stderr)

    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    ))
    logger.addHandler(handler)
    return logger


@dataclass
class LSPMessage:
    """JSON-RPC 2.0 message wrapper for LSP protocol."""
    content: dict

    def encode(self) -> bytes:
        body = json.dumps(self.content)
        header = f"Content-Length: {len(body.encode('utf-8'))}\r\n\r\n"
        return (header + body).encode('utf-8')


class LSPServer:
    """Manages a single LSP server process with full lifecycle control."""

    def __init__(self, command: str, args: list[str], root_path: str, logger: logging.Logger):
        self.command = command
        self.args = args
        self.root_path = root_path
        self.root_uri = Path(root_path).as_uri()
        self.logger = logger

        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
        self.initialized = False
        self._lock = threading.Lock()
        self._pending: dict[int, queue.Queue] = {}
        self._reader_thread: Optional[threading.Thread] = None
        self._opened_files: set[str] = set()
        self._last_activity = time.time()

    def start(self) -> bool:
        """Start the language server process."""
        try:
            self.logger.info(f"Starting LSP server: {self.command} {' '.join(self.args)}")
            self.process = subprocess.Popen(
                [self.command] + self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.root_path
            )
            self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
            self._reader_thread.start()
            return True
        except FileNotFoundError:
            self.logger.error(f"LSP server not found: {self.command}")
            return False
        except Exception as e:
            self.logger.exception(f"Failed to start LSP server: {e}")
            return False

    def _read_loop(self):
        """Background thread: read responses from server."""
        while self.process and self.process.poll() is None:
            try:
                msg = self._read_message()
                if msg is None:
                    break

                if "id" in msg and msg["id"] in self._pending:
                    self._pending[msg["id"]].put(msg)
                elif "method" in msg:
                    # Handle server notifications (diagnostics, etc.)
                    self.logger.debug(f"Server notification: {msg['method']}")
            except Exception as e:
                self.logger.debug(f"Read loop error: {e}")
                break
        self.logger.info("Reader thread exiting")

    def _read_message(self) -> Optional[dict]:
        """Read a single LSP message from stdout."""
        if not self.process or not self.process.stdout:
            return None

        headers = {}
        while True:
            line = self.process.stdout.readline()
            if not line:
                return None
            line = line.decode('utf-8')
            if line in ('\r\n', '\n'):
                break
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()

        length = int(headers.get('Content-Length', 0))
        if length == 0:
            return None

        content = self.process.stdout.read(length)
        return json.loads(content.decode('utf-8'))

    def _send(self, method: str, params: Any, is_notification: bool = False) -> Optional[dict]:
        """Send request/notification to server."""
        self._last_activity = time.time()

        msg: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }

        if not is_notification:
            with self._lock:
                self.request_id += 1
                req_id = self.request_id
            msg["id"] = req_id
            response_queue: queue.Queue = queue.Queue()
            self._pending[req_id] = response_queue

        encoded = LSPMessage(msg).encode()
        if self.process and self.process.stdin:
            self.process.stdin.write(encoded)
            self.process.stdin.flush()

        if is_notification:
            return None

        try:
            response = response_queue.get(timeout=REQUEST_TIMEOUT)
            del self._pending[req_id]
            return response
        except queue.Empty:
            del self._pending[req_id]
            return {"error": {"code": -32000, "message": "Request timeout"}}

    def initialize(self) -> bool:
        """Initialize LSP handshake."""
        response = self._send("initialize", {
            "processId": os.getpid(),
            "rootUri": self.root_uri,
            "rootPath": self.root_path,
            "capabilities": {
                "textDocument": {
                    "documentSymbol": {"hierarchicalDocumentSymbolSupport": True},
                    "definition": {"linkSupport": True},
                    "references": {},
                    "hover": {"contentFormat": ["markdown", "plaintext"]},
                    "implementation": {},
                },
                "workspace": {
                    "symbol": {"symbolKind": {"valueSet": list(range(1, 27))}}
                }
            },
            "workspaceFolders": [{"uri": self.root_uri, "name": Path(self.root_path).name}]
        })

        if not response or "error" in response:
            self.logger.error(f"Initialize failed: {response}")
            return False

        self._send("initialized", {}, is_notification=True)
        self.initialized = True
        self.logger.info("LSP server initialized")
        return True

    def ensure_file_open(self, file_path: str, language_id: str):
        """Open file in server if not already open."""
        uri = Path(file_path).as_uri()
        if uri in self._opened_files:
            return

        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Failed to read file: {e}")
            return

        self._send("textDocument/didOpen", {
            "textDocument": {
                "uri": uri,
                "languageId": language_id,
                "version": 1,
                "text": content
            }
        }, is_notification=True)
        self._opened_files.add(uri)

    def document_symbol(self, file_path: str, language_id: str) -> dict:
        self.ensure_file_open(file_path, language_id)
        return self._send("textDocument/documentSymbol", {
            "textDocument": {"uri": Path(file_path).as_uri()}
        }) or {}

    def go_to_definition(self, file_path: str, line: int, char: int, language_id: str) -> dict:
        self.ensure_file_open(file_path, language_id)
        return self._send("textDocument/definition", {
            "textDocument": {"uri": Path(file_path).as_uri()},
            "position": {"line": line, "character": char}
        }) or {}

    def find_references(self, file_path: str, line: int, char: int, language_id: str) -> dict:
        self.ensure_file_open(file_path, language_id)
        return self._send("textDocument/references", {
            "textDocument": {"uri": Path(file_path).as_uri()},
            "position": {"line": line, "character": char},
            "context": {"includeDeclaration": True}
        }) or {}

    def hover(self, file_path: str, line: int, char: int, language_id: str) -> dict:
        self.ensure_file_open(file_path, language_id)
        return self._send("textDocument/hover", {
            "textDocument": {"uri": Path(file_path).as_uri()},
            "position": {"line": line, "character": char}
        }) or {}

    def go_to_implementation(self, file_path: str, line: int, char: int, language_id: str) -> dict:
        self.ensure_file_open(file_path, language_id)
        return self._send("textDocument/implementation", {
            "textDocument": {"uri": Path(file_path).as_uri()},
            "position": {"line": line, "character": char}
        }) or {}

    def workspace_symbol(self, query: str) -> dict:
        return self._send("workspace/symbol", {"query": query}) or {}

    def shutdown(self):
        """Gracefully shutdown the server."""
        if not self.process:
            return
        self.logger.info(f"Shutting down {self.command}")
        try:
            self._send("shutdown", None)
            self._send("exit", None, is_notification=True)
            self.process.wait(timeout=5)
        except:
            self.process.kill()
        self.process = None


class LSPDaemon:
    """
    Daemon process that keeps LSP servers alive across invocations.
    Communicates with clients via Unix socket.
    """

    def __init__(self, root_path: str):
        self.root_path = root_path
        self.logger = setup_logging(daemon_mode=True)
        self.servers: dict[str, LSPServer] = {}
        self.socket: Optional[socket.socket] = None
        self.running = False
        self._last_activity = time.time()

    def get_server(self, ext: str) -> Optional[LSPServer]:
        """Get or create server for file extension."""
        if ext not in SERVERS:
            return None

        if ext not in self.servers:
            config = SERVERS[ext]
            server = LSPServer(
                config["command"],
                config["args"],
                self.root_path,
                self.logger
            )
            if not server.start() or not server.initialize():
                return None
            self.servers[ext] = server

        return self.servers[ext]

    def handle_request(self, request: dict) -> dict:
        """Handle a client request."""
        self._last_activity = time.time()

        op = request.get("operation")
        file_path = request.get("file_path")
        line = request.get("line", 0)
        char = request.get("character", 0)
        query = request.get("query", "")

        if not file_path and op != "workspaceSymbol":
            return {"error": "file_path required"}

        ext = Path(file_path).suffix.lower() if file_path else ".py"
        server = self.get_server(ext)

        if not server:
            return {"error": f"No LSP server for {ext} files"}

        config = SERVERS.get(ext, {})
        lang_id = config.get("language_id", "plaintext")

        if op == "documentSymbol":
            return server.document_symbol(file_path, lang_id)
        elif op == "goToDefinition":
            return server.go_to_definition(file_path, line, char, lang_id)
        elif op == "findReferences":
            return server.find_references(file_path, line, char, lang_id)
        elif op == "hover":
            return server.hover(file_path, line, char, lang_id)
        elif op == "goToImplementation":
            return server.go_to_implementation(file_path, line, char, lang_id)
        elif op == "workspaceSymbol":
            return server.workspace_symbol(query)
        else:
            return {"error": f"Unknown operation: {op}"}

    def run(self):
        """Main daemon loop."""
        self.logger.info(f"Starting LSP daemon for {self.root_path}")

        # Clean up old socket
        if SOCKET_PATH.exists():
            SOCKET_PATH.unlink()

        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(str(SOCKET_PATH))
        self.socket.listen(5)
        self.socket.settimeout(60)  # Check for timeout every minute

        # Write PID file
        PID_FILE.write_text(str(os.getpid()))

        self.running = True

        def handle_signal(sig, frame):
            self.running = False

        signal.signal(signal.SIGTERM, handle_signal)
        signal.signal(signal.SIGINT, handle_signal)

        self.logger.info("Daemon listening on socket")

        while self.running:
            try:
                conn, _ = self.socket.accept()
                threading.Thread(
                    target=self._handle_connection,
                    args=(conn,),
                    daemon=True
                ).start()
            except socket.timeout:
                # Check for inactivity timeout
                if time.time() - self._last_activity > DAEMON_TIMEOUT:
                    self.logger.info("Inactivity timeout, shutting down")
                    break
            except Exception as e:
                if self.running:
                    self.logger.exception(f"Accept error: {e}")

        self.shutdown()

    def _handle_connection(self, conn: socket.socket):
        """Handle a single client connection."""
        try:
            data = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"\n" in data:
                    break

            if data:
                request = json.loads(data.decode('utf-8'))
                response = self.handle_request(request)
                conn.sendall(json.dumps(response).encode('utf-8') + b"\n")
        except Exception as e:
            self.logger.exception(f"Connection error: {e}")
            try:
                conn.sendall(json.dumps({"error": str(e)}).encode('utf-8') + b"\n")
            except:
                pass
        finally:
            conn.close()

    def shutdown(self):
        """Clean shutdown of daemon and all servers."""
        self.logger.info("Shutting down daemon")
        self.running = False

        for server in self.servers.values():
            server.shutdown()
        self.servers.clear()

        if self.socket:
            self.socket.close()

        if SOCKET_PATH.exists():
            SOCKET_PATH.unlink()
        if PID_FILE.exists():
            PID_FILE.unlink()


class LSPClient:
    """
    Client that connects to daemon or falls back to direct mode.
    Provides clean API for LSP operations.
    """

    def __init__(self, root_path: str):
        self.root_path = root_path
        self.logger = setup_logging()

    def _send_to_daemon(self, request: dict) -> Optional[dict]:
        """Send request to daemon via socket."""
        if not SOCKET_PATH.exists():
            return None

        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(REQUEST_TIMEOUT + 5)
            sock.connect(str(SOCKET_PATH))
            sock.sendall(json.dumps(request).encode('utf-8') + b"\n")

            data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"\n" in data:
                    break

            sock.close()
            return json.loads(data.decode('utf-8')) if data else None
        except Exception as e:
            self.logger.debug(f"Daemon connection failed: {e}")
            return None

    def _direct_request(self, request: dict) -> dict:
        """Fall back to direct LSP server connection."""
        file_path = request.get("file_path")
        ext = Path(file_path).suffix.lower() if file_path else ".py"

        if ext not in SERVERS:
            return {"error": f"No LSP server for {ext} files"}

        config = SERVERS[ext]
        server = LSPServer(
            config["command"],
            config["args"],
            self.root_path,
            self.logger
        )

        if not server.start() or not server.initialize():
            return {"error": f"Failed to start {config['command']}"}

        try:
            lang_id = config.get("language_id", "plaintext")
            op = request.get("operation")
            line = request.get("line", 0)
            char = request.get("character", 0)

            if op == "documentSymbol":
                return server.document_symbol(file_path, lang_id)
            elif op == "goToDefinition":
                return server.go_to_definition(file_path, line, char, lang_id)
            elif op == "findReferences":
                return server.find_references(file_path, line, char, lang_id)
            elif op == "hover":
                return server.hover(file_path, line, char, lang_id)
            elif op == "goToImplementation":
                return server.go_to_implementation(file_path, line, char, lang_id)
            elif op == "workspaceSymbol":
                return server.workspace_symbol(request.get("query", ""))
            else:
                return {"error": f"Unknown operation: {op}"}
        finally:
            server.shutdown()

    def request(self, operation: str, file_path: Optional[str] = None,
                line: int = 0, character: int = 0, query: str = "") -> dict:
        """Execute LSP operation, using daemon if available."""
        req = {
            "operation": operation,
            "file_path": os.path.abspath(file_path) if file_path else None,
            "line": line,
            "character": character,
            "query": query
        }

        # Try daemon first
        result = self._send_to_daemon(req)
        if result is not None:
            return result

        # Fall back to direct mode
        self.logger.debug("Using direct mode (daemon not available)")
        return self._direct_request(req)


# ============================================================================
# Output Formatting
# ============================================================================

def format_symbol(symbol: dict, indent: int = 0) -> str:
    """Format document symbol for display."""
    name = symbol.get("name", "?")
    kind = SYMBOL_KINDS.get(symbol.get("kind", 0), "Unknown")

    if "range" in symbol:
        line = symbol["range"]["start"].get("line", 0) + 1
    elif "location" in symbol:
        line = symbol["location"]["range"]["start"].get("line", 0) + 1
    else:
        line = 0

    prefix = "  " * indent
    result = f"{prefix}{kind}: {name}" + (f":{line}" if line else "")

    for child in symbol.get("children", []):
        result += "\n" + format_symbol(child, indent + 1)

    return result


def format_location(loc: dict | list) -> str:
    """Format location(s) for display."""
    if isinstance(loc, list):
        return "\n".join(format_location(l) for l in loc)

    uri = loc.get("uri", loc.get("targetUri", ""))
    path = url_unquote(uri[7:]) if uri.startswith("file://") else uri

    range_info = loc.get("range", loc.get("targetRange", {}))
    start = range_info.get("start", {})
    line = start.get("line", 0) + 1
    char = start.get("character", 0) + 1

    return f"{path}:{line}:{char}"


def format_hover(hover: dict) -> str:
    """Format hover info for display."""
    contents = hover.get("contents", {})

    if isinstance(contents, str):
        return contents
    elif isinstance(contents, dict):
        return contents.get("value", str(contents))
    elif isinstance(contents, list):
        parts = []
        for item in contents:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(item.get("value", str(item)))
        return "\n".join(parts)

    return str(contents)


def format_result(operation: str, result: dict, as_json: bool = False) -> str:
    """Format operation result for display."""
    if as_json:
        return json.dumps(result, indent=2)

    if "error" in result:
        err = result['error']
        if isinstance(err, dict):
            return f"Error: {err.get('message', str(err))}"
        return f"Error: {err}"

    res = result.get("result")
    if res is None:
        return "No results"

    if operation == "documentSymbol":
        if isinstance(res, list) and res:
            return "\n".join(format_symbol(s) for s in res)
        return "No symbols found"

    elif operation in ("goToDefinition", "findReferences", "goToImplementation"):
        if isinstance(res, list) and res:
            return "\n".join(format_location(l) for l in res)
        elif res:
            return format_location(res)
        return "No results"

    elif operation == "hover":
        return format_hover(res)

    elif operation == "workspaceSymbol":
        if isinstance(res, list) and res:
            lines = []
            for sym in res:
                loc = sym.get("location", {})
                uri = loc.get("uri", "")
                path = url_unquote(uri[7:]) if uri.startswith("file://") else uri
                line = loc.get("range", {}).get("start", {}).get("line", 0) + 1
                kind = SYMBOL_KINDS.get(sym.get("kind", 0), "Unknown")
                lines.append(f"{kind}: {sym.get('name', '?')} @ {path}:{line}")
            return "\n".join(lines)
        return "No symbols found"

    return json.dumps(result, indent=2)


# ============================================================================
# CLI Interface
# ============================================================================

def is_daemon_running() -> bool:
    """Check if daemon is already running."""
    if not PID_FILE.exists():
        return False
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, 0)  # Check if process exists
        return True
    except (ProcessLookupError, ValueError):
        # Stale PID file
        PID_FILE.unlink(missing_ok=True)
        return False


def start_daemon(root_path: str):
    """Start daemon in background."""
    if is_daemon_running():
        print("Daemon already running", file=sys.stderr)
        return

    pid = os.fork()
    if pid > 0:
        # Parent - wait briefly for daemon to start
        time.sleep(0.5)
        if is_daemon_running():
            print(f"Daemon started (PID: {PID_FILE.read_text().strip()})")
        else:
            print("Failed to start daemon", file=sys.stderr)
        return

    # Child - become daemon
    os.setsid()
    pid = os.fork()
    if pid > 0:
        os._exit(0)

    # Redirect stdio
    sys.stdin.close()
    sys.stdout = open('/dev/null', 'w')
    sys.stderr = open(LOG_FILE, 'a')

    daemon = LSPDaemon(root_path)
    daemon.run()
    os._exit(0)


def stop_daemon():
    """Stop running daemon."""
    if not PID_FILE.exists():
        print("Daemon not running", file=sys.stderr)
        return

    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        print(f"Stopped daemon (PID: {pid})")
    except (ProcessLookupError, ValueError) as e:
        print(f"Failed to stop daemon: {e}", file=sys.stderr)
    finally:
        PID_FILE.unlink(missing_ok=True)
        SOCKET_PATH.unlink(missing_ok=True)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="LSP Client for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Operations:
  documentSymbol     List all symbols in a file
  goToDefinition     Jump to symbol definition
  findReferences     Find all references to symbol
  hover              Get documentation/type info
  goToImplementation Find implementations
  workspaceSymbol    Search symbols across workspace

Daemon commands:
  daemon start       Start background daemon (faster subsequent calls)
  daemon stop        Stop background daemon
  daemon status      Check daemon status

Examples:
  %(prog)s documentSymbol myfile.py
  %(prog)s goToDefinition myfile.py --line 10 --character 5
  %(prog)s workspaceSymbol --query "MyClass"
  %(prog)s daemon start
"""
    )

    parser.add_argument("operation", nargs="?", choices=[
        "documentSymbol", "goToDefinition", "findReferences",
        "hover", "goToImplementation", "workspaceSymbol",
        "daemon"
    ])
    parser.add_argument("file_path", nargs="?", help="Path to file (or daemon subcommand)")
    parser.add_argument("--line", type=int, default=1, help="Line number (1-based)")
    parser.add_argument("--character", type=int, default=1, help="Character offset (1-based)")
    parser.add_argument("--query", default="", help="Search query for workspaceSymbol")
    parser.add_argument("--root", help="Project root (default: cwd)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    root_path = args.root or os.getcwd()

    # Handle daemon commands
    if args.operation == "daemon":
        subcmd = args.file_path or "status"
        if subcmd == "start":
            start_daemon(root_path)
        elif subcmd == "stop":
            stop_daemon()
        elif subcmd == "status":
            if is_daemon_running():
                pid = PID_FILE.read_text().strip()
                print(f"Daemon running (PID: {pid})")
            else:
                print("Daemon not running")
        else:
            print(f"Unknown daemon command: {subcmd}", file=sys.stderr)
            sys.exit(1)
        return

    if not args.operation:
        parser.print_help()
        sys.exit(1)

    # Validate file path for operations that need it
    if args.operation != "workspaceSymbol":
        if not args.file_path:
            print("Error: file_path required", file=sys.stderr)
            sys.exit(1)
        file_path = os.path.abspath(args.file_path)
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
    else:
        file_path = None

    # Execute operation
    client = LSPClient(root_path)
    result = client.request(
        operation=args.operation,
        file_path=file_path,
        line=args.line - 1,  # Convert to 0-based
        character=args.character - 1,
        query=args.query
    )

    print(format_result(args.operation, result, args.json))


if __name__ == "__main__":
    main()
