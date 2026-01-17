#!/usr/bin/env bash
#
# clone-repos.sh - Clone Git repositories for codebase analysis
#
# Usage: clone-repos.sh <output-dir> <repo1> [repo2] [repo3] ...
#
# Supports:
#   - Full Git URLs (https://github.com/user/repo, git@github.com:user/repo)
#   - GitHub shorthand (user/repo -> https://github.com/user/repo)
#   - Local directory paths (just copies/links them)
#
# Output:
#   Creates shallow clones in <output-dir>/<repo-name>/
#   Prints JSON summary of cloned repos
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

usage() {
    cat << EOF
Usage: $(basename "$0") <output-dir> <source1> [source2] ...

Clone Git repositories or link local directories for codebase analysis.

Arguments:
  output-dir    Directory where repos will be cloned/linked
  source        One or more of:
                - Git URL: https://github.com/user/repo
                - SSH URL: git@github.com:user/repo
                - GitHub shorthand: user/repo
                - Local path: /path/to/project or ./relative/path

Examples:
  $(basename "$0") /tmp/analysis radix-ui/primitives
  $(basename "$0") /tmp/analysis https://github.com/shadcn-ui/ui ./local-project
  $(basename "$0") /tmp/analysis user/repo1 user/repo2 /path/to/local

Output:
  Prints JSON array with info about each cloned/linked repo.
EOF
    exit 1
}

# Check if a path is a Git URL
is_git_url() {
    local source="$1"
    [[ "$source" =~ ^(https?://|git@|ssh://) ]]
}

# Check if a path is GitHub shorthand (user/repo)
is_github_shorthand() {
    local source="$1"
    # Match user/repo pattern but not absolute paths
    [[ "$source" =~ ^[a-zA-Z0-9_-]+/[a-zA-Z0-9._-]+$ ]] && [[ ! -d "$source" ]]
}

# Check if a path is a local directory
is_local_dir() {
    local source="$1"
    [[ -d "$source" ]]
}

# Extract repo name from URL or path
get_repo_name() {
    local source="$1"
    local name

    if is_git_url "$source"; then
        # Extract from Git URL
        name=$(basename "$source" .git)
    elif is_github_shorthand "$source"; then
        # Extract from shorthand (user/repo -> repo)
        name=$(echo "$source" | cut -d'/' -f2)
    else
        # Extract from local path
        name=$(basename "$source")
    fi

    echo "$name"
}

# Convert source to cloneable URL
get_clone_url() {
    local source="$1"

    if is_git_url "$source"; then
        echo "$source"
    elif is_github_shorthand "$source"; then
        echo "https://github.com/$source"
    else
        # Local path - no URL needed
        echo ""
    fi
}

# Clone a single repo
clone_repo() {
    local source="$1"
    local output_dir="$2"
    local repo_name
    local clone_url
    local target_dir
    local repo_type
    local success=true

    repo_name=$(get_repo_name "$source")
    target_dir="$output_dir/$repo_name"

    # Remove existing directory if present
    if [[ -d "$target_dir" ]]; then
        log_warn "Removing existing directory: $target_dir"
        rm -rf "$target_dir"
    fi

    if is_local_dir "$source"; then
        # For local directories, create a symlink or copy
        repo_type="local"
        log_info "Linking local directory: $source -> $target_dir"

        # Get absolute path
        local abs_source
        abs_source=$(cd "$source" && pwd)

        # Create symlink
        ln -s "$abs_source" "$target_dir" || {
            log_warn "Symlink failed, copying instead..."
            cp -r "$abs_source" "$target_dir" || success=false
        }
    else
        # Clone Git repository
        repo_type="git"
        clone_url=$(get_clone_url "$source")
        log_info "Cloning: $clone_url -> $target_dir"

        # Shallow clone with minimal history
        git clone --depth 1 --single-branch "$clone_url" "$target_dir" 2>/dev/null || {
            log_error "Failed to clone: $clone_url"
            success=false
        }
    fi

    # Output JSON for this repo
    if $success; then
        local file_count
        local lang_stats

        if [[ -d "$target_dir" ]]; then
            file_count=$(find "$target_dir" -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.py" -o -name "*.go" -o -name "*.rs" -o -name "*.cpp" -o -name "*.c" -o -name "*.h" -o -name "*.java" -o -name "*.swift" -o -name "*.kt" \) 2>/dev/null | wc -l | tr -d ' ')

            # Detect primary language
            lang_stats=$(detect_language "$target_dir")
        else
            file_count=0
            lang_stats="unknown"
        fi

        echo "{\"name\": \"$repo_name\", \"source\": \"$source\", \"type\": \"$repo_type\", \"path\": \"$target_dir\", \"files\": $file_count, \"language\": \"$lang_stats\", \"status\": \"success\"}"
    else
        echo "{\"name\": \"$repo_name\", \"source\": \"$source\", \"type\": \"$repo_type\", \"path\": \"$target_dir\", \"status\": \"failed\"}"
    fi
}

# Detect primary language in a directory
detect_language() {
    local dir="$1"
    local ts_count js_count py_count go_count rs_count cpp_count java_count

    ts_count=$(find "$dir" -name "*.ts" -o -name "*.tsx" 2>/dev/null | wc -l | tr -d ' ')
    js_count=$(find "$dir" -name "*.js" -o -name "*.jsx" 2>/dev/null | wc -l | tr -d ' ')
    py_count=$(find "$dir" -name "*.py" 2>/dev/null | wc -l | tr -d ' ')
    go_count=$(find "$dir" -name "*.go" 2>/dev/null | wc -l | tr -d ' ')
    rs_count=$(find "$dir" -name "*.rs" 2>/dev/null | wc -l | tr -d ' ')
    cpp_count=$(find "$dir" -name "*.cpp" -o -name "*.cc" -o -name "*.c" -o -name "*.h" -o -name "*.hpp" 2>/dev/null | wc -l | tr -d ' ')
    java_count=$(find "$dir" -name "*.java" 2>/dev/null | wc -l | tr -d ' ')

    # Find max
    local max_lang="typescript"
    local max_count=$ts_count

    if [[ $js_count -gt $max_count ]]; then max_lang="javascript"; max_count=$js_count; fi
    if [[ $py_count -gt $max_count ]]; then max_lang="python"; max_count=$py_count; fi
    if [[ $go_count -gt $max_count ]]; then max_lang="go"; max_count=$go_count; fi
    if [[ $rs_count -gt $max_count ]]; then max_lang="rust"; max_count=$rs_count; fi
    if [[ $cpp_count -gt $max_count ]]; then max_lang="cpp"; max_count=$cpp_count; fi
    if [[ $java_count -gt $max_count ]]; then max_lang="java"; max_count=$java_count; fi

    if [[ $max_count -eq 0 ]]; then
        echo "unknown"
    else
        echo "$max_lang"
    fi
}

# Main
main() {
    if [[ $# -lt 2 ]]; then
        usage
    fi

    local output_dir="$1"
    shift
    local sources=("$@")

    # Create output directory
    mkdir -p "$output_dir"
    log_info "Output directory: $output_dir"

    # Clone each repo and collect results
    local results=()
    for source in "${sources[@]}"; do
        result=$(clone_repo "$source" "$output_dir")
        results+=("$result")
    done

    # Output JSON array
    echo "["
    local first=true
    for result in "${results[@]}"; do
        if $first; then
            first=false
        else
            echo ","
        fi
        echo "  $result"
    done
    echo "]"
}

main "$@"
