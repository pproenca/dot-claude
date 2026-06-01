#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
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

    def test_capability_demotion_must_be_reearned_after_miss(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "maturity", CAIRN / "skills" / "capability-ledger" / "scripts" / "maturity.py",
        )
        self.assertIsNotNone(spec)
        maturity = importlib.util.module_from_spec(spec)
        self.assertIsNotNone(spec.loader)
        spec.loader.exec_module(maturity)

        entry = {
            "solves": [
                {"benchmark_ref": "a", "floor_ratio": 1.0, "domain": "ui", "date": "2026-01-01"},
                {"benchmark_ref": "b", "floor_ratio": 1.0, "domain": "api", "date": "2026-01-02"},
                {"benchmark_ref": "c", "floor_ratio": 1.0, "domain": "api", "date": "2026-01-03"},
                {"benchmark_ref": "d", "floor_ratio": 1.0, "domain": "ui", "date": "2026-01-05"},
            ],
            "last_demotion": {"date": "2026-01-04", "to": "practiced"},
        }

        self.assertEqual(maturity.effective_maturity(entry), "practiced")

    def test_boundary_scan_uses_repo_config_for_subtree_and_excludes_root_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "boundary.config.json").write_text(
                json.dumps({"include_ext": [".py"], "_substrate": "python"}),
                encoding="utf-8",
            )
            (repo / "src").mkdir()
            (repo / "src" / "service.py").write_text(
                "value = store.get(key)\nstore.update(key, value)\n",
                encoding="utf-8",
            )
            (repo / "node_modules" / "pkg").mkdir(parents=True)
            (repo / "node_modules" / "pkg" / "bad.py").write_text(
                "subprocess.run(['x'])\n",
                encoding="utf-8",
            )

            proc = self.run_script("skills/boundary-discipline/scripts/scan.py", str(repo / "src"), "--json")

            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            body = json.loads(proc.stdout)
            files = {f["file"] for f in body["findings"]}
            self.assertIn("src/service.py", files)
            self.assertNotIn("node_modules/pkg/bad.py", files)
            self.assertTrue(any(f["label"] == "read-before-write" for f in body["findings"]))

    def test_plan_check_validates_table_data_rows_not_template_prose(self) -> None:
        plan = """# PLAN: x

## 0. Feature
done
## 1. Boundary decomposition
done
## 2. Bill of materials
done
## 3. Shelf check (REUSE / EXTEND / BUILD)
Use one of REUSE, EXTEND, VENDOR, BUILD.
| Item | Layer | Exists? (where) | Decision | Note |
|---|---|---|---|---|
## 4. Build items: local vs shared
none
## 5. Fit check
yes
## 6. Seam & blast-radius check
| Touched code | Contact type | Why / mitigation |
|---|---|---|
| a.py | COMPOSITION | ok |
| b.py |  | missing |
"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "PLAN.md"
            path.write_text(plan, encoding="utf-8")

            proc = self.run_script("skills/feature-workflow/scripts/plan_check.py", str(path))

            self.assertEqual(proc.returncode, 1, proc.stderr + proc.stdout)
            self.assertIn("section 3", proc.stdout)
            self.assertIn("section 6", proc.stdout)

    def test_design_system_catalog_includes_configured_ts_primitives(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "src" / "ui" / "components").mkdir(parents=True)
            (repo / "boundary.config.json").write_text(
                json.dumps({
                    "include_ext": [".ts", ".tsx"],
                    "layers": {"primitive": ["src/ui/components/**/*"]},
                }),
                encoding="utf-8",
            )
            (repo / "src" / "ui" / "components" / "button.ts").write_text(
                "export interface ButtonProps { label: string };\nexport function Button() { return null }\n",
                encoding="utf-8",
            )

            proc = self.run_script("skills/feature-workflow/scripts/design_system.py", "--repo", str(repo))

            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertIn("Button", (repo / "docs" / "design-system.md").read_text(encoding="utf-8"))

    def test_schema_recorders_reject_wrong_shaped_objects(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            bad_model = repo / "bad-model.json"
            bad_model.write_text(json.dumps({"reframe": "x", "solution_classes": [1], "taught_by_gap": "gap"}), encoding="utf-8")
            bad_profile = repo / "bad-profile.json"
            bad_profile.write_text(json.dumps({"principles": "x", "pinned_libs": ["expo"]}), encoding="utf-8")

            model = self.run_script(
                "skills/mental-models/scripts/models_record.py",
                "--repo", str(repo), "--smell", "shape", "--from-json", str(bad_model),
            )
            profile = self.run_script(
                "skills/specialist-knowledge/scripts/specialist_refresh.py",
                "--repo", str(repo), "--set", "ios", "--from-json", str(bad_profile),
            )

            self.assertEqual(model.returncode, 2, model.stderr + model.stdout)
            self.assertEqual(profile.returncode, 2, profile.stderr + profile.stdout)
            self.assertFalse((repo / "mental-models.jsonl").exists())
            self.assertFalse((repo / "specialist-profiles.jsonl").exists())

    def test_config_check_validates_repo_relative_script_paths(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "boundary.config.json").write_text(
                json.dumps({
                    "include_ext": [".py"],
                    "verify": [{"name": "missing", "cmd": "python .harness/x/missing.py --repo ."}],
                }),
                encoding="utf-8",
            )

            proc = self.run_script("skills/harness-setup/scripts/config_check.py", "--repo", str(repo))

            self.assertEqual(proc.returncode, 1, proc.stderr + proc.stdout)
            self.assertIn(".harness/x/missing.py", proc.stdout)

    def test_ratchet_ignores_wrong_shaped_records_and_counts_repeated_observations(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "ratchet.jsonl").write_text("[]\n\"x\"\nnot json\n", encoding="utf-8")

            status = self.run_script("skills/knowledge-ratchet/scripts/ratchet.py", "--repo", str(repo), "--status")
            self.assertEqual(status.returncode, 0, status.stderr + status.stdout)
            self.assertNotIn("Traceback", status.stderr + status.stdout)

            for _ in range(3):
                observe = self.run_script(
                    "skills/knowledge-ratchet/scripts/ratchet.py",
                    "--repo", str(repo), "--observe", "extract helper", "--key", "extract-helper",
                )
                self.assertEqual(observe.returncode, 0, observe.stderr + observe.stdout)
            ripe = self.run_script("skills/knowledge-ratchet/scripts/ratchet.py", "--repo", str(repo), "--ripe")
            self.assertEqual(ripe.returncode, 1, ripe.stderr + ripe.stdout)
            self.assertIn("extract-helper", ripe.stdout)

            promote = self.run_script(
                "skills/knowledge-ratchet/scripts/ratchet.py",
                "--repo", str(repo), "--promote", "extract-helper", "--as", "skill",
            )
            self.assertEqual(promote.returncode, 2, promote.stderr + promote.stdout)
            self.assertIn("--landed", promote.stdout)

    def test_entity_boot_ignores_malformed_capability_records(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "capability-ledger.jsonl").write_text("[]\n{\"maturity\":\"proven\"}\nnot json\n", encoding="utf-8")

            orient = self.run_script("skills/entity-boot/scripts/orient.py", "--repo", str(repo))
            reflect = self.run_script("skills/entity-boot/scripts/reflect.py", "--repo", str(repo))

            self.assertEqual(orient.returncode, 0, orient.stderr + orient.stdout)
            self.assertEqual(reflect.returncode, 0, reflect.stderr + reflect.stdout)
            self.assertNotIn("Traceback", orient.stderr + orient.stdout + reflect.stderr + reflect.stdout)

    def test_lib_outcome_does_not_execute_repo_controlled_models_record(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            marker = repo / "owned"
            (repo / "models_record.py").write_text(
                f"from pathlib import Path\nPath({str(marker)!r}).write_text('owned')\n",
                encoding="utf-8",
            )
            (repo / "lib-knowledge.jsonl").write_text(
                json.dumps({"name": "volatile", "uses": 2, "stale_hits": 2}) + "\n",
                encoding="utf-8",
            )

            proc = self.run_script(
                "skills/library-knowledge/scripts/lib_outcome.py",
                "--repo", str(repo), "--name", "volatile", "--stale", "--reframe", "derive it",
            )

            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertFalse(marker.exists())

    def test_inquiry_observe_surfaces_recorder_failure_and_cleans_tempfile(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            harness = repo / ".harness" / "mental-models"
            harness.mkdir(parents=True)
            (harness / "models_record.py").write_text("import sys\nprint('bad', file=sys.stderr)\nsys.exit(2)\n", encoding="utf-8")
            predict = self.run_script(
                "skills/inquiry/scripts/predict.py",
                "--repo", str(repo), "--claim", "terrain", "--confidence", "0.9",
            )
            self.assertEqual(predict.returncode, 0, predict.stderr + predict.stdout)
            pid = predict.stdout.split()[1]

            before = {p.name for p in Path(tempfile.gettempdir()).glob("*.json")}
            observe = self.run_script(
                "skills/inquiry/scripts/observe.py",
                "--repo", str(repo), "--id", pid, "--outcome", "wrong", "--reframe", "check first",
            )
            after = {p.name for p in Path(tempfile.gettempdir()).glob("*.json")}

            self.assertEqual(observe.returncode, 2, observe.stderr + observe.stdout)
            self.assertIn("mental-model teaching FAILED", observe.stderr)
            self.assertSetEqual(before, after)


if __name__ == "__main__":
    unittest.main()
