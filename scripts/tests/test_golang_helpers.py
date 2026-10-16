"""Execution-level regressions for the optional Go project helper examples."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = REPO_ROOT / "skills/dev/golang-best-practices"


class HelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.log = self.root / "commands.jsonl"
        self.env = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ["PATH"],
                        COMMAND_LOG=str(self.log))
        self.env.pop("DATABASE_URL", None)
        for name in ("go", "wire", "migrate", "docker", "air"):
            path = self.bin / name
            path.write_text(
                f"#!{sys.executable}\n"
                "import json, os, sys\n"
                "from pathlib import Path\n"
                "name = Path(sys.argv[0]).name\n"
                "with open(os.environ['COMMAND_LOG'], 'a') as log:\n"
                "    log.write(json.dumps([name, *sys.argv[1:]]) + '\\n')\n"
                "sys.exit(23 if os.environ.get('FAIL_TOOL') == name else 0)\n"
            )
            path.chmod(0o755)

    def calls(self) -> list[list[str]]:
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def make(self, *args: str, **env: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["make", "-f", str(SKILL_ROOT / "Makefile"), *args], cwd=self.root,
            env=dict(self.env, **env), text=True, capture_output=True, timeout=15,
        )

    def script(self, name: str, *args: str, **env: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(SKILL_ROOT / "scripts" / name), *args], cwd=self.root,
            env=dict(self.env, **env), text=True, capture_output=True, timeout=15,
        )

    def test_default_install_only_downloads_project_dependencies(self) -> None:
        result = self.make("install")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.calls(), [["go", "mod", "download"]])

    def test_install_selects_only_explicit_tool(self) -> None:
        result = self.make("install", "WIRE_VERSION=v0.6.0")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.calls(), [
            ["go", "mod", "download"],
            ["go", "install", "github.com/google/wire/cmd/wire@v0.6.0"],
        ])

    def test_unpinned_tool_version_fails_before_downloading(self) -> None:
        result = self.make("install", "WIRE_VERSION=latest")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_tool_install_failure_stops_later_installations(self) -> None:
        result = self.make("install", "WIRE_VERSION=v0.6.0", "AIR_VERSION=v1.61.7",
                           FAIL_TOOL="go")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.calls(), [["go", "mod", "download"]])

    def test_compose_commands_share_file_and_environment_selection(self) -> None:
        operations = {"docker": ["up", "-d"], "docker-build": ["build"],
                      "docker-logs": ["logs", "-f"], "docker-down": ["down"]}
        for target, operation in operations.items():
            with self.subTest(target=target):
                self.log.unlink(missing_ok=True)
                result = self.make(target, "COMPOSE_FILE=./deploy config/compose.yml",
                                   "ENV_FILE=./environment files/dev.env")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(self.calls(), [[
                    "docker", "compose", "-f", "./deploy config/compose.yml",
                    "--env-file", "./environment files/dev.env", *operation,
                ]])

    def test_default_dev_does_not_switch_to_installed_air(self) -> None:
        result = self.make("dev")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.calls(), [["go", "run", "."]])

    def test_clean_only_removes_local_artifacts(self) -> None:
        build = self.root / "build output"
        build.mkdir()
        (build / "app").write_text("artifact")
        result = self.make("clean", f"BUILD_DIR={build}")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(build.exists())
        self.assertEqual(self.calls(), [])

    def test_make_wire_propagates_generator_failure(self) -> None:
        result = self.make("wire", FAIL_TOOL="wire")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.calls(), [["wire", "gen", "."]])
        self.assertNotIn("generated successfully", result.stdout.lower())

    def test_wire_script_accepts_project_package_patterns(self) -> None:
        result = self.script("wire-gen.sh", "./orders/...", "./inventory/...")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.calls(), [["wire", "gen", "./orders/...", "./inventory/..."]])

    def test_wire_script_propagates_failure(self) -> None:
        result = self.script("wire-gen.sh", FAIL_TOOL="wire")
        self.assertEqual(result.returncode, 23)
        self.assertNotIn("generated successfully", result.stdout.lower())

    def test_migration_requires_action_and_explicit_connection(self) -> None:
        for args in ((), ("up",), ("down",), ("version",)):
            with self.subTest(args=args):
                result = self.script("db-migrate.sh", *args)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.calls(), [])
        self.assertIn("DATABASE_URL", result.stderr)

    def test_migration_create_does_not_require_a_database(self) -> None:
        result = self.script("db-migrate.sh", "create", "add_orders", MIGRATIONS_DIR="./db changes")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.calls(), [[
            "migrate", "create", "-ext", "sql", "-dir", "./db changes", "-seq", "add_orders",
        ]])

    def test_migration_rejects_missing_name_or_force_version(self) -> None:
        for action in ("create", "force"):
            with self.subTest(action=action):
                result = self.script("db-migrate.sh", action)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.calls(), [])

    def test_migration_preserves_connection_and_zero_version(self) -> None:
        url = "postgres://example.invalid/test?application_name=local example"
        result = self.script("db-migrate.sh", "force", "0", DATABASE_URL=url)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.calls(), [[
            "migrate", "-path", "./migrations", "-database", url, "force", "0",
        ]])
        self.assertNotIn(url, result.stdout + result.stderr)

    def test_migration_failure_does_not_report_success(self) -> None:
        result = self.script("db-migrate.sh", "up", DATABASE_URL="postgres://example.invalid/test",
                             FAIL_TOOL="migrate")
        self.assertEqual(result.returncode, 23)
        self.assertNotIn("Done", result.stdout)

    def test_image_build_passes_through_selected_arguments(self) -> None:
        result = self.script("docker-build.sh", "example/app", "dev", "--build-arg",
                             "MAIN_PACKAGE=./cmd/server", "--build-arg", "GO_IMAGE=golang:example-alpine")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.calls(), [[
            "docker", "build", "-t", "example/app:dev", "--build-arg",
            "MAIN_PACKAGE=./cmd/server", "--build-arg", "GO_IMAGE=golang:example-alpine", ".",
        ]])


class RealGoProjectTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("go"), "Go toolchain is not installed")
    def test_multi_file_project_builds_tests_and_runs_with_default_makefile(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "go.mod").write_text("module example.invalid/helper-test\n\ngo 1.22\n")
            (root / "main.go").write_text('package main\nimport "fmt"\nfunc main() { fmt.Println(message()) }\n')
            (root / "message.go").write_text('package main\nfunc message() string { return "ready" }\n')
            (root / "message_test.go").write_text(
                'package main\nimport "testing"\n'
                'func TestMessage(t *testing.T) { if message() != "ready" { t.Fatal("unexpected message") } }\n'
            )
            result = subprocess.run(
                ["make", "-f", str(SKILL_ROOT / "Makefile"), "install", "test", "run"],
                cwd=root, env=dict(os.environ, GOWORK="off", GOTOOLCHAIN="local"),
                capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("ready", result.stdout)
            self.assertTrue((root / "bin/app").is_file())
            entry = root / "cmd/server"
            entry.mkdir(parents=True)
            (entry / "main.go").write_text('package main\nimport "fmt"\nfunc main() { fmt.Println("selected-entry") }\n')
            selected = subprocess.run(
                ["make", "-f", str(SKILL_ROOT / "Makefile"), "run", "MAIN_PACKAGE=./cmd/server",
                 "APP_NAME=selected", "BUILD_DIR=./build output"],
                cwd=root, env=dict(os.environ, GOWORK="off", GOTOOLCHAIN="local"),
                capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(selected.returncode, 0, selected.stdout + selected.stderr)
            self.assertIn("selected-entry", selected.stdout)
            self.assertTrue((root / "build output/selected").is_file())


class ComposeConfigTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("docker"), "Docker CLI is not installed")
    def test_default_application_and_optional_dependency_profiles(self) -> None:
        docker = shutil.which("docker")
        assert docker is not None
        version = subprocess.run([docker, "compose", "version"], capture_output=True, timeout=15)
        if version.returncode != 0:
            self.skipTest("Compose plugin is not installed")
        compose = SKILL_ROOT / "templates/docker/docker-compose.yml"
        for profile, services in ((None, {"app"}), ("database", {"app", "db"}),
                                  ("cache", {"app", "redis"})):
            with self.subTest(profile=profile):
                command = [docker, "compose", "-f", str(compose)]
                if profile:
                    command.extend(["--profile", profile])
                result = subprocess.run(
                    [*command, "config", "--format", "json"],
                    env=dict(os.environ, GO_IMAGE="golang:1.26.0-alpine"),
                    capture_output=True, text=True, timeout=15,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                data = json.loads(result.stdout)
                self.assertEqual(set(data["services"]), services)
                self.assertNotIn("depends_on", data["services"]["app"])
                self.assertEqual(data["services"]["app"]["build"]["args"]["MAIN_PACKAGE"], ".")


if __name__ == "__main__":
    unittest.main()
