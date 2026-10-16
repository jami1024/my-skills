#!/usr/bin/env python3
"""Regression tests for skill validation and safe Go skill synchronization."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "validate_skills", REPO_ROOT / "scripts/validate-skills.py"
)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)
OVERRIDE_SPEC = importlib.util.spec_from_file_location(
    "golang_overrides", REPO_ROOT / "scripts/apply-golang-overrides.py"
)
assert OVERRIDE_SPEC is not None and OVERRIDE_SPEC.loader is not None
OVERRIDES = importlib.util.module_from_spec(OVERRIDE_SPEC)
OVERRIDE_SPEC.loader.exec_module(OVERRIDES)
EVAL_SPEC = importlib.util.spec_from_file_location(
    "run_skill_eval", REPO_ROOT / "scripts/run-skill-eval.py"
)
assert EVAL_SPEC is not None and EVAL_SPEC.loader is not None
EVAL_RUNNER = importlib.util.module_from_spec(EVAL_SPEC)
EVAL_SPEC.loader.exec_module(EVAL_RUNNER)


def write_skill(root: Path, name: str, body: str = "") -> Path:
    path = root / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nname: {name}\ndescription: Test skill\n---\n{body}")
    return path


class ValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def validate(self) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = VALIDATOR.validate(self.root, strict=True)
        return status, output.getvalue()

    def test_missing_documentation_link_fails_with_location(self) -> None:
        write_skill(self.root, "demo", "[Template](references/missing.md)\n")
        status, output = self.validate()
        self.assertEqual(status, 1)
        self.assertIn("demo/SKILL.md:5", output)
        self.assertIn("references/missing.md", output)

    def test_existing_links_titles_and_encoded_paths_pass(self) -> None:
        skill = write_skill(
            self.root, "demo",
            '[Guide](references/guide.md#section)\n'
            '[Space](references/my%20guide.md "Title")\n'
            '[Angle](<references/my guide.md>)\n'
            '![Image](assets/image.svg)\n',
        )
        (skill.parent / "references").mkdir()
        (skill.parent / "references/guide.md").write_text("# Section\n")
        (skill.parent / "references/my guide.md").write_text("Guide\n")
        (skill.parent / "assets").mkdir()
        (skill.parent / "assets/image.svg").write_text("<svg/>\n")
        self.assertEqual(self.validate()[0], 0)

    def test_code_and_remote_links_are_not_local_dependencies(self) -> None:
        write_skill(
            self.root, "demo",
            '```markdown\n[Example](missing.md)\n```\n'
            '~~~markdown\n[Example](missing.md)\n~~~\n'
            '`[Inline](missing.md)`\n'
            '[Web](https://example.com/missing)\n'
            '[Mail](mailto:example@example.com)\n'
            '[Anchor](#section)\n'
            '| signature | func Map[T, R any](collection []T, fn func(T) R) []R |\n',
        )
        self.assertEqual(self.validate()[0], 0)

    def test_generated_templates_and_evals_are_skipped(self) -> None:
        skill = write_skill(self.root, "demo")
        for directory in ("assets/templates", "templates", "evals"):
            path = skill.parent / directory / "example.md"
            path.parent.mkdir(parents=True)
            path.write_text("[Project file](./missing.md)\n")
        self.assertEqual(self.validate()[0], 0)


class SyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.upstream = self.root / "upstream"
        self.target = self.repo / "skills/golang"
        self.bin = self.root / "bin"
        (self.repo / "scripts").mkdir(parents=True)
        self.bin.mkdir()
        for name in (
            "sync-golang-skills.sh", "validate-skills.py",
            "apply-golang-overrides.py", "golang-overrides.json",
        ):
            shutil.copy2(REPO_ROOT / "scripts" / name, self.repo / "scripts" / name)
        write_skill(self.target, "golang-existing", "Original content\n")
        (self.target / "README.md").write_text("Local README\n")
        (self.target / "EVALUATIONS.md").write_text("Local evaluations\n")
        write_skill(self.upstream / "skills", "golang-new")
        (self.upstream / "LICENSE").write_text("Fixture license\n")
        (self.upstream / "rules").mkdir()
        (self.upstream / "rules/golang-always.mdc").write_text("Fixture rule\n")
        git = self.bin / "git"
        git.write_text(
            '#!/usr/bin/env bash\nset -eu\ncase "$1" in\n'
            'clone) [ "${FAIL_CLONE:-0}" = 0 ] || exit 70; cp -R "$4" "$5" ;;\n'
            '-C) printf "%s\\n" fixture-commit ;;\n*) exit 99 ;;\nesac\n'
        )
        git.chmod(0o755)
        mv = self.bin / "mv"
        mv.write_text(
            '#!/usr/bin/env bash\nset -eu\n'
            'if [ "$2" = "$REVIEW_TARGET" ]; then\n'
            '  case "$1" in\n'
            '    */new) [ "${FAIL_INSTALL:-0}" = 0 ] || exit 71 ;;\n'
            '    */backup) [ "${FAIL_RESTORE:-0}" = 0 ] || exit 72 ;;\n'
            '  esac\nfi\nexec "$REAL_MV" "$@"\n'
        )
        mv.chmod(0o755)
        real_mv = shutil.which("mv")
        assert real_mv is not None
        self.env = dict(
            os.environ, PATH=str(self.bin) + os.pathsep + os.environ["PATH"],
            REAL_MV=real_mv, REVIEW_TARGET=str(self.target),
        )
        self.original = self.snapshot()

    def snapshot(self) -> dict[str, bytes]:
        return {
            str(path.relative_to(self.target)): path.read_bytes()
            for path in self.target.rglob("*") if path.is_file()
        }

    def sync(self, **env: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(self.repo / "scripts/sync-golang-skills.sh"), str(self.upstream)],
            cwd=self.repo, env=dict(self.env, **env), capture_output=True,
            text=True, timeout=20,
        )

    def assert_preserved(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), self.original)

    def test_valid_sync_preserves_local_docs_and_removes_old_skills(self) -> None:
        result = self.sync()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.target / "golang-new/SKILL.md").exists())
        self.assertFalse((self.target / "golang-existing").exists())
        for name in ("README.md", "EVALUATIONS.md"):
            self.assertEqual((self.target / name).read_bytes(), self.original[name])
        self.assertFalse(list((self.repo / ".tmp").glob("skills-golang.*")))

    def test_local_docs_keep_links_relative_to_repository_layout(self) -> None:
        readme = "[Sync script](../../scripts/sync-golang-skills.sh)\n"
        (self.target / "README.md").write_text(readme)
        result = self.sync()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.target / "README.md").read_text(), readme)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(VALIDATOR.validate(self.repo / "skills", strict=True), 0)

    def test_invalid_metadata_preserves_old_copy(self) -> None:
        path = self.upstream / "skills/golang-new/SKILL.md"
        path.write_text(path.read_text().replace("name: golang-new", "name: Invalid_Name"))
        self.assert_preserved(self.sync())

    def test_empty_upstream_preserves_old_copy(self) -> None:
        shutil.rmtree(self.upstream / "skills/golang-new")
        self.assert_preserved(self.sync())

    def test_overlong_skill_preserves_old_copy(self) -> None:
        write_skill(self.upstream / "skills", "golang-new", "Example\n" * 501)
        self.assert_preserved(self.sync())

    def test_missing_link_preserves_old_copy(self) -> None:
        write_skill(self.upstream / "skills", "golang-new", "[Missing](missing.md)\n")
        self.assert_preserved(self.sync())

    def test_clone_failure_preserves_old_copy(self) -> None:
        self.assert_preserved(self.sync(FAIL_CLONE="1"))

    def test_missing_license_preserves_old_copy(self) -> None:
        (self.upstream / "LICENSE").unlink()
        self.assert_preserved(self.sync())

    def test_changed_upstream_patch_preserves_old_copy(self) -> None:
        path = write_skill(self.upstream / "skills", "golang-how-to", "Changed upstream route\n")
        self.assertTrue(path.exists())
        result = self.sync()
        self.assert_preserved(result)
        self.assertIn("no longer matches upstream", result.stderr)

    def test_failed_install_restores_old_copy(self) -> None:
        self.assert_preserved(self.sync(FAIL_INSTALL="1"))

    def test_failed_restore_keeps_recoverable_backup(self) -> None:
        result = self.sync(FAIL_INSTALL="1", FAIL_RESTORE="1")
        self.assertNotEqual(result.returncode, 0)
        backups = list((self.repo / ".tmp").glob("skills-golang.*/backup"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(
            (backups[0] / "golang-existing/SKILL.md").read_bytes(),
            self.original["golang-existing/SKILL.md"],
        )
        self.assertIn(str(backups[0]), result.stderr)

    def test_upstream_link_fixes_are_reapplied(self) -> None:
        upstream_skills = self.upstream / "skills"
        for name in ("golang-documentation", "golang-troubleshooting"):
            write_skill(upstream_skills, name)
            (upstream_skills / name / "references").mkdir()
        doc = upstream_skills / "golang-documentation"
        (doc / "assets/templates").mkdir(parents=True)
        for name in ("README.md", "CONTRIBUTING.md", "CHANGELOG.md", "llms.txt"):
            (doc / "assets/templates" / name).write_text("Template\n")
        (doc / "references/project-docs.md").write_text(
            "[README](./templates/README.md)\n"
            "[Contributing](./templates/CONTRIBUTING.md)\n"
            "[Changes](./templates/CHANGELOG.md)\n"
        )
        (doc / "references/library.md").write_text("[LLMs](./templates/llms.txt)\n")
        methodology = upstream_skills / "golang-troubleshooting/references/methodology.md"
        methodology.write_text("[Skill](./SKILL.md)\n")
        result = self.sync()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "../assets/templates/README.md",
            (self.target / "golang-documentation/references/project-docs.md").read_text(),
        )
        self.assertEqual(
            (self.target / "golang-troubleshooting/references/methodology.md").read_text(),
            "[Skill](../SKILL.md)\n",
        )


class OverrideTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = json.loads((REPO_ROOT / "scripts/golang-overrides.json").read_text())

    def test_route_layout_and_testing_overrides_replay_and_are_idempotent(self) -> None:
        names = ("golang-how-to", "golang-testing", "golang-project-layout")
        for name in names:
            patches = self.manifest["replacements"][f"{name}/SKILL.md"]
            path = write_skill(self.root, name, "\n\n".join(patch["old"] for patch in patches))
            self.assertTrue(path.is_file())
        self.assertEqual(OVERRIDES.apply_overrides(self.root), len(names))
        for name in names:
            text = (self.root / name / "SKILL.md").read_text()
            for patch in self.manifest["replacements"][f"{name}/SKILL.md"]:
                self.assertIn(patch["new"], text)
        self.assertEqual(OVERRIDES.apply_overrides(self.root), 0)

    def test_stale_patch_does_not_partially_rewrite_files(self) -> None:
        earlier = write_skill(self.root, "golang-benchmark")
        original = earlier.read_bytes()
        write_skill(self.root, "golang-how-to", "Unrecognized upstream text\n")
        with self.assertRaisesRegex(ValueError, "no longer matches upstream"):
            OVERRIDES.apply_overrides(self.root)
        self.assertEqual(earlier.read_bytes(), original)

    def test_local_eval_assertion_fixes_replay_and_are_idempotent(self) -> None:
        manifest = self.manifest["assertion_fixes"]
        self.assertTrue(manifest, "assertion_fixes must not be empty")
        for relative, patches in manifest.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps({
                    "skill_name": relative.split("/")[0],
                    "evals": [{
                        "id": 1,
                        "assertions": [{"id": p["id"], "text": p["old"]} for p in patches],
                    }],
                }, indent=2),
                encoding="utf-8",
            )
        self.assertEqual(OVERRIDES.apply_overrides(self.root), len(manifest))
        for relative, patches in manifest.items():
            text = (self.root / relative).read_text(encoding="utf-8")
            for patch in patches:
                self.assertIn(patch["new"], text)
        self.assertEqual(OVERRIDES.apply_overrides(self.root), 0)

    def test_assertion_fixes_are_well_formed(self) -> None:
        for relative, patches in self.manifest["assertion_fixes"].items():
            self.assertTrue(relative.endswith("/evals/evals.json"), relative)
            ids = [patch["id"] for patch in patches]
            self.assertEqual(len(ids), len(set(ids)), f"{relative}: duplicate assertion id")
            for patch in patches:
                self.assertTrue(patch["old"].strip() and patch["new"].strip(), patch["id"])
                self.assertNotEqual(patch["old"], patch["new"], patch["id"])

    def manifest_file(self, overrides: dict) -> Path:
        path = self.root / "manifest.json"
        path.write_text(json.dumps(overrides), encoding="utf-8")
        return path

    def seed_eval_files(self) -> None:
        for relative in self.manifest["local_cases"]:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps([{"id": 1, "name": "upstream", "assertions": []}], indent=2) + "\n")

    def test_local_cases_are_appended_once_and_are_idempotent(self) -> None:
        local = self.manifest["local_cases"]
        self.assertTrue(local)
        stripped = {key: {} for key in ("descriptions", "replacements", "assertion_fixes")}
        manifest = self.manifest_file({**stripped, "local_cases": local})
        self.seed_eval_files()
        self.assertEqual(OVERRIDES.apply_overrides(self.root, manifest=manifest), len(local))
        for relative, cases in local.items():
            data = json.loads((self.root / relative).read_text(encoding="utf-8"))
            names = [case["name"] for case in data]
            for case in cases:
                self.assertIn(case["name"], names)
        self.assertEqual(OVERRIDES.apply_overrides(self.root, manifest=manifest), 0)

    def test_local_case_content_change_replaces_the_existing_case(self) -> None:
        local = self.manifest["local_cases"]
        stripped = {key: {} for key in ("descriptions", "replacements", "assertion_fixes")}
        self.seed_eval_files()
        manifest = self.manifest_file({**stripped, "local_cases": local})
        self.assertEqual(OVERRIDES.apply_overrides(self.root, manifest=manifest), len(local))

        relative = next(iter(local))
        edited = json.loads(json.dumps(local))
        edited[relative][0]["assertions"] = [{"id": "L9.9", "text": "edited"}]
        edited_manifest = self.manifest_file({**stripped, "local_cases": edited})
        self.assertEqual(OVERRIDES.apply_overrides(self.root, manifest=edited_manifest), 1)

        data = json.loads((self.root / relative).read_text(encoding="utf-8"))
        self.assertEqual(len(data), 2, "本地用例应被替换而不是重复追加")
        self.assertEqual(data[-1]["assertions"], [{"id": "L9.9", "text": "edited"}])
        self.assertEqual(OVERRIDES.apply_overrides(self.root, manifest=edited_manifest), 0)

    def test_local_case_needs_a_name(self) -> None:
        relative = next(iter(self.manifest["local_cases"]))
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("[]\n", encoding="utf-8")

        stripped = {key: {} for key in ("descriptions", "replacements", "assertion_fixes")}
        unnamed = self.manifest_file(
            {**stripped, "local_cases": {relative: [{"id": 99, "assertions": []}]}}
        )
        with self.assertRaisesRegex(ValueError, "必须有 name"):
            OVERRIDES.apply_overrides(self.root, manifest=unnamed)
        self.assertEqual(target.read_text(encoding="utf-8"), "[]\n")

    def test_missing_local_case_target_is_skipped(self) -> None:
        relative = "golang-nope/evals/evals.json"
        stripped = {key: {} for key in ("descriptions", "replacements", "assertion_fixes")}
        manifest = self.manifest_file(
            {**stripped, "local_cases": {relative: [{"name": "x", "assertions": []}]}}
        )
        self.assertEqual(OVERRIDES.apply_overrides(self.root, manifest=manifest), 0)

    def test_repo_local_cases_carry_fixtures_and_matching_eval_ids(self) -> None:
        root = REPO_ROOT / "skills/golang"
        for relative, cases in self.manifest["local_cases"].items():
            container = json.loads((root / relative).read_text(encoding="utf-8"))
            container = container if isinstance(container, list) else container["evals"]
            by_name = {case.get("name"): case for case in container}
            for case in cases:
                self.assertIn(case["name"], by_name)
                self.assertTrue((REPO_ROOT / case["fixture"]).is_dir(), case["fixture"])
                self.assertTrue(
                    all(assertion["id"].startswith("L") for assertion in case["assertions"]),
                    case["name"],
                )
                self.assertEqual(by_name[case["name"]]["assertions"], case["assertions"])

    def test_local_eval_assertions_match_the_manifest(self) -> None:
        root = REPO_ROOT / "skills/golang"
        for relative, patches in self.manifest["assertion_fixes"].items():
            text = (root / relative).read_text(encoding="utf-8")
            for patch in patches:
                self.assertIn(patch["new"], text, f"{relative}: {patch['id']} not applied")
                self.assertNotIn(patch["old"], text, f"{relative}: {patch['id']} still upstream")

    def test_stale_assertion_patch_does_not_partially_rewrite_files(self) -> None:
        relative, patches = next(iter(self.manifest["assertion_fixes"].items()))
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps([{
                "id": 1,
                "assertions": [{"id": patches[0]["id"], "text": "upstream text changed"}],
            }]),
            encoding="utf-8",
        )
        original = path.read_bytes()
        with self.assertRaisesRegex(ValueError, re.escape(patches[0]["id"]) + " no longer matches upstream"):
            OVERRIDES.apply_overrides(self.root)
        self.assertEqual(path.read_bytes(), original)


class EvalRunnerTests(unittest.TestCase):
    def test_load_cases_accepts_both_upstream_schemas(self) -> None:
        object_schema = EVAL_RUNNER.load_cases(REPO_ROOT / "skills/golang/golang-error-handling")
        array_schema = EVAL_RUNNER.load_cases(REPO_ROOT / "skills/golang/golang-project-layout")
        self.assertTrue(object_schema and array_schema)
        self.assertIn("assertions", object_schema[0])
        self.assertIn("assertions", array_schema[0])

    def test_load_cases_reports_unreadable_or_unknown_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "evals").mkdir()
            (root / "evals/evals.json").write_text("not json")
            with self.assertRaisesRegex(ValueError, "无法读取"):
                EVAL_RUNNER.load_cases(root)
            (root / "evals/evals.json").write_text('{"cases": []}')
            with self.assertRaisesRegex(ValueError, "无法识别的结构"):
                EVAL_RUNNER.load_cases(root)

    def test_select_cases_filters_and_rejects_out_of_range(self) -> None:
        cases = [{"name": "a"}, {"name": "b"}, {"name": "c"}]
        self.assertEqual([index for index, _ in EVAL_RUNNER.select_cases(cases, [1, 3])], [1, 3])
        self.assertEqual(len(EVAL_RUNNER.select_cases(cases, None)), 3)
        with self.assertRaisesRegex(ValueError, "超出范围"):
            EVAL_RUNNER.select_cases(cases, [0, 4])

    def test_parse_skill_argument(self) -> None:
        self.assertEqual(EVAL_RUNNER.parse_skill_argument("golang-testing"), ("golang-testing", None))
        self.assertEqual(
            EVAL_RUNNER.parse_skill_argument("golang-testing:2,12"),
            ("golang-testing", [2, 12]),
        )
        for value in ("golang-testing:x", "golang-testing:"):
            with self.assertRaises(ValueError):
                EVAL_RUNNER.parse_skill_argument(value)

    def test_invoke_prompt_prefixes_only_when_forced(self) -> None:
        self.assertEqual(EVAL_RUNNER.invoke_prompt("golang-testing", "do it", False), "do it")
        self.assertEqual(
            EVAL_RUNNER.invoke_prompt("golang-testing", "do it", True),
            "/skill:golang-testing\ndo it",
        )
        self.assertEqual(EVAL_RUNNER.invoke_prompt(None, "do it", True), "do it")

    def test_case_workdir_prefers_the_case_fixture(self) -> None:
        out = Path("output-dir")
        fixture = "docs/evals/fixtures/existing-service"
        self.assertEqual(
            EVAL_RUNNER.case_workdir({"fixture": fixture}, out, REPO_ROOT),
            REPO_ROOT / fixture,
        )
        self.assertEqual(EVAL_RUNNER.case_workdir({}, out, REPO_ROOT), out)

    def test_skill_file_reads_normalises_paths(self) -> None:
        reads = [
            "/Users/someone/x/my-skills/skills/golang/golang-testing/SKILL.md",
            "skills/golang/golang-testing/references/integration-testing.md",
            "internal/store/store.go",
            "skills/dev/golang-best-practices/SKILL.md",
        ]
        self.assertEqual(
            EVAL_RUNNER.skill_file_reads(reads),
            [
                "skills/golang/golang-testing/SKILL.md",
                "skills/dev/golang-best-practices/SKILL.md",
            ],
        )
        self.assertEqual(
            EVAL_RUNNER.skill_file_reads(reads, "golang-testing"),
            ["skills/golang/golang-testing/SKILL.md"],
        )
        self.assertEqual(EVAL_RUNNER.skill_file_reads(reads, "golang-lint"), [])

    def test_validity_requires_the_treatment_arm_to_load_the_skill(self) -> None:
        own = ["skills/golang/golang-testing/SKILL.md"]
        self.assertTrue(EVAL_RUNNER.evaluate_validity("golang-testing", own, False, 0)["valid"])

        not_read = EVAL_RUNNER.evaluate_validity("golang-testing", ["internal/store.go"], False, 0)
        self.assertFalse(not_read["valid"])
        self.assertEqual(not_read["reason"], "处理组未读目标 skill")

        forced = EVAL_RUNNER.evaluate_validity("golang-testing", ["internal/store.go"], True, 0)
        self.assertTrue(forced["valid"])
        self.assertEqual(forced["reason"], "强制加载")

    def test_validity_flags_contaminated_baseline_and_failed_session(self) -> None:
        contaminated = EVAL_RUNNER.evaluate_validity(
            None, ["skills/dev/golang-best-practices/SKILL.md"], False, 0
        )
        self.assertFalse(contaminated["valid"])
        self.assertEqual(contaminated["reason"], "基线读到了 skill 正文")

        clean = EVAL_RUNNER.evaluate_validity(None, ["internal/store.go"], False, 0)
        self.assertTrue(clean["valid"])

        self.assertFalse(EVAL_RUNNER.evaluate_validity("golang-testing", [], True, 1)["valid"])

    def test_build_report_covers_every_assertion_with_blank_verdicts(self) -> None:
        cases = [(2, {"name": "n", "prompt": "p", "assertions": [
            {"id": "2.1", "text": "first"}, {"id": "2.2", "text": "second"},
        ]})]
        entries = [{"case": "testing-02.skill", "exit": 0, "elapsed": 1.5, "reads": ["x"],
                    "answer_path": ".tmp/a", "reason": "强制加载"}]
        report = EVAL_RUNNER.build_report({"golang-testing": (cases, entries)})
        self.assertIn("## golang-testing", report)
        self.assertIn("### 用例 2：n", report)
        self.assertIn("| 2.1 | first |  |  |", report)
        self.assertIn("| 2.2 | second |  |  |", report)
        self.assertIn("`testing-02.skill` exit=0", report)
        self.assertIn("有效性=强制加载", report)


class GoExampleTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("go"), "Go toolchain is not installed")
    def test_documented_error_mapping_preserves_behavior(self) -> None:
        text = (REPO_ROOT / "skills/dev/golang-best-practices/SKILL.md").read_text()
        section = text.split("## 错误、日志与可观测性", 1)[1]
        match = re.search(r"```go\n(.*?)\n```", section, re.DOTALL)
        assert match is not None
        source = '''package example
import (
    "database/sql"
    "errors"
    "fmt"
    "strings"
    "testing"
)
var ErrNotFound = errors.New("not found")
func mapLookupError(err error) error {
    userID := "user-123"
''' + match[1] + '''
    return nil
}
func TestMapping(t *testing.T) {
    other := errors.New("database unavailable")
    cases := []struct{name string; input, want error}{
        {"success", nil, nil},
        {"not found", sql.ErrNoRows, ErrNotFound},
        {"wrapped not found", fmt.Errorf("query: %w", sql.ErrNoRows), ErrNotFound},
        {"other", other, other},
    }
    for _, tc := range cases {
        t.Run(tc.name, func(t *testing.T) {
            got := mapLookupError(tc.input)
            if !errors.Is(got, tc.want) {
                t.Fatalf("mapLookupError(%v) = %v, want %v", tc.input, got, tc.want)
            }
            if tc.input == other && !strings.Contains(got.Error(), "user-123") {
                t.Fatalf("missing operation context: %v", got)
            }
        })
    }
}
'''
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mapping_test.go"
            path.write_text(source)
            result = subprocess.run(
                ["go", "test", str(path)], capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class MakefileTests(unittest.TestCase):
    def test_pinned_tool_versions_use_matching_module_paths(self) -> None:
        for version, module in (
            ("v2.1.6", "github.com/golangci/golangci-lint/v2"),
            ("v1.64.8", "github.com/golangci/golangci-lint"),
        ):
            with self.subTest(version=version):
                result = subprocess.run(
                    ["make", "-n", "-f", str(REPO_ROOT / "skills/dev/golang-best-practices/Makefile"),
                     "install", "WIRE_VERSION=v0.6.0", f"GOLANGCI_LINT_VERSION={version}",
                     "AIR_VERSION=v1.61.7"],
                    capture_output=True, text=True, timeout=10,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f'go install "{module}/cmd/golangci-lint@{version}"', result.stdout)
                self.assertIn('go install "github.com/air-verse/air@v1.61.7"', result.stdout)


if __name__ == "__main__":
    unittest.main()
