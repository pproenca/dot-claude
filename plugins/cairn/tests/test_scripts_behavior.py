#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CAIRN = ROOT / "plugins" / "cairn"


def script(rel: str) -> str:
    return str(CAIRN / rel)


class CairnScriptBehaviorTests(unittest.TestCase):
    def run_script(self, rel: str, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, script(rel), *args],
            cwd=str(cwd or ROOT),
            text=True,
            capture_output=True,
            timeout=20,
        )

    def test_skeleton_generates_python_feature_skeleton(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "boundary.config.json").write_text(
                json.dumps({"include_ext": [".py"], "layers": {"pipeline": ["src/features/**/*"]}}),
                encoding="utf-8",
            )
            feature = repo / "src" / "features" / "booking"
            feature.mkdir(parents=True)
            (feature / "service.py").write_text(
                "async def reserve_room(room_id: str) -> bool:\n    return True\n",
                encoding="utf-8",
            )

            proc = self.run_script(
                "skills/feature-workflow/scripts/skeleton.py",
                "--repo", str(repo),
                "--feature", "src/features/booking",
            )

            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertIn("reserve_room", proc.stdout)
            self.assertNotIn("Traceback", proc.stderr + proc.stdout)

    def test_verify_rejects_malformed_config_without_running_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            cfg = repo / "boundary.config.json"
            cfg.write_text("{bad json", encoding="utf-8")

            proc = self.run_script(
                "skills/feature-workflow/scripts/verify.py",
                "--repo", str(repo),
                "--config", str(cfg),
                "--json",
            )

            self.assertEqual(proc.returncode, 2, proc.stderr + proc.stdout)
            body = json.loads(proc.stdout)
            self.assertFalse(body["passed"])
            self.assertEqual(body["results"], [])
            self.assertIn("cannot read config", body["error"])

    def test_recorders_reject_bad_json_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            bad = repo / "bad.json"
            bad.write_text("{bad json", encoding="utf-8")

            cases = [
                ("skills/mental-models/scripts/models_record.py",
                 ("--repo", str(repo), "--smell", "shape", "--from-json", str(bad))),
                ("skills/specialist-knowledge/scripts/specialist_refresh.py",
                 ("--repo", str(repo), "--set", "ios", "--from-json", str(bad))),
            ]
            for rel, args in cases:
                with self.subTest(script=rel):
                    proc = self.run_script(rel, *args)
                    self.assertEqual(proc.returncode, 2, proc.stderr + proc.stdout)
                    self.assertIn("error:", proc.stderr)
                    self.assertNotIn("Traceback", proc.stderr + proc.stdout)

    def test_wrong_shaped_jsonl_records_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "mental-models.jsonl").write_text("[]\n\"x\"\nnot json\n", encoding="utf-8")

            proc = self.run_script("skills/mental-models/scripts/models_lookup.py", "--repo", str(repo), "--all")

            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertIn("no mental models yet", proc.stdout)
            self.assertNotIn("Traceback", proc.stderr + proc.stdout)

    def test_capability_floor_ratio_must_be_positive(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            proc = self.run_script(
                "skills/capability-ledger/scripts/cap_record.py",
                "--repo", str(repo),
                "--class", "render-perf",
                "--floor-ratio", "-1",
                "--benchmark", "bench.json",
            )

            self.assertEqual(proc.returncode, 2, proc.stderr + proc.stdout)
            self.assertIn("must be positive", proc.stderr)
            self.assertFalse((repo / "capability-ledger.jsonl").exists())

    def test_close_loop_propagates_ledger_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            proc = self.run_script(
                "skills/capability-ledger/scripts/close_loop.py",
                "--repo", str(repo),
                "--class", "render-perf",
                "--domain", "renderer",
                "--floor-ratio", "1.5",
            )

            self.assertNotEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertIn("REFUSED", proc.stdout)
            self.assertIn("circuit incomplete", proc.stdout)

    def test_ratchet_refuses_unripe_abstraction_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            observe = self.run_script(
                "skills/knowledge-ratchet/scripts/ratchet.py",
                "--repo", str(repo),
                "--observe", "extract helper",
                "--key", "extract-helper",
                "--kind", "abstraction",
                "--where", "case-1",
            )
            self.assertEqual(observe.returncode, 0, observe.stderr + observe.stdout)

            promote = self.run_script(
                "skills/knowledge-ratchet/scripts/ratchet.py",
                "--repo", str(repo),
                "--promote", "extract-helper",
                "--as", "skill",
                "--landed", "skills/x",
            )

            self.assertEqual(promote.returncode, 2, promote.stderr + promote.stdout)
            self.assertIn("not ripe", promote.stdout)

    def test_tool_forge_refuses_paths_outside_workshop(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            motion = "manual scan"
            for _ in range(3):
                proc = self.run_script(
                    "skills/toolsmith/scripts/motion_observe.py",
                    "--repo", str(repo),
                    "--motion", motion,
                    "--steps", "2",
                )
                self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            key = "motion:" + hashlib.sha1(motion.lower().encode()).hexdigest()[:8]

            forge = self.run_script(
                "skills/toolsmith/scripts/tool_forge.py",
                "--repo", str(repo),
                "--motion-key", key,
                "--path", "scripts/tool.py",
                "--build-steps", "4",
            )

            self.assertEqual(forge.returncode, 2, forge.stderr + forge.stdout)
            self.assertIn(".cairn/tools", forge.stderr)

    def test_config_init_mirrors_skill_scripts_when_skills_root_is_given(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            skills = Path(td) / "skills"
            repo.mkdir()
            (skills / "sample-skill" / "scripts").mkdir(parents=True)
            (skills / "sample-skill" / "scripts" / "sample.py").write_text("print('ok')\n", encoding="utf-8")

            proc = self.run_script(
                "skills/harness-setup/scripts/config_init.py",
                "--repo", str(repo),
                "--skills-root", str(skills),
            )

            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertTrue((repo / ".harness" / "sample-skill" / "sample.py").exists())


if __name__ == "__main__":
    unittest.main()
