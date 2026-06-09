import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class DevCleanupScriptTests(unittest.TestCase):
    def test_cleanup_entrypoints_exist(self) -> None:
        for relative_path in (
            "stop.bat",
            "cleanup-dev.bat",
            "scripts/cleanup_dev.ps1",
        ):
            self.assertTrue((PROJECT_ROOT / relative_path).is_file(), relative_path)

    def test_cleanup_script_uses_project_scoped_command_line_filtering(self) -> None:
        script = (PROJECT_ROOT / "scripts" / "cleanup_dev.ps1").read_text(encoding="utf-8")
        self.assertIn("Win32_Process", script)
        self.assertIn("Test-CommandLineReferencesProject", script)
        self.assertIn("CommandLine", script)
        self.assertIn("Stop-Process", script)
        self.assertIn("$ProjectRootLower", script)
        self.assertNotIn("taskkill /IM python.exe", script)

    def test_git_lock_cleanup_checks_related_processes(self) -> None:
        script = (PROJECT_ROOT / "scripts" / "cleanup_dev.ps1").read_text(encoding="utf-8")
        self.assertIn(".git\\index.lock", script)
        for process_name in ("git.exe", "ssh.exe", "gpg.exe", "codex.exe"):
            self.assertIn(process_name, script)

        stop_bat = (PROJECT_ROOT / "stop.bat").read_text(encoding="utf-8")
        cleanup_bat = (PROJECT_ROOT / "cleanup-dev.bat").read_text(encoding="utf-8")
        self.assertIn("-StopOnly", stop_bat)
        self.assertIn("scripts\\cleanup_dev.ps1", cleanup_bat)


if __name__ == "__main__":
    unittest.main()
