import json
import subprocess
import sys
from pathlib import Path


def run_cli(args, cwd):
    return subprocess.run(
        [sys.executable, "-m", "ashes.cli", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


def test_list_reports_empty_state(tmp_path):
    result = run_cli(["box", "list"], tmp_path)

    assert result.returncode == 0
    assert "No boxes configured" in result.stdout


def test_create_box_persists_box(tmp_path):
    result = run_cli(["box", "create", "banking"], tmp_path)

    assert result.returncode == 0
    state_path = tmp_path / "ashes_state.json"
    assert state_path.exists()

    payload = json.loads(state_path.read_text())
    assert payload["boxes"][0]["name"] == "banking"
    assert payload["boxes"][0]["status"] == "stopped"


def test_device_plan_for_pc_mode(tmp_path):
    result = run_cli(["device", "plan", "--mode", "pc"], tmp_path)

    assert result.returncode == 0
    assert "USB-C cable" in result.stdout
    assert "Pixel device" in result.stdout


def test_device_plan_for_app_mode(tmp_path):
    result = run_cli(["device", "plan", "--mode", "app"], tmp_path)

    assert result.returncode == 0
    assert "Android app" in result.stdout
    assert "rooted" in result.stdout.lower()


def test_installer_report_marks_unsupported_device(tmp_path):
    result = run_cli(["installer", "check", "--device", "pixel-4a"], tmp_path)

    assert result.returncode == 0
    assert "unsupported" in result.stdout.lower()
    assert "warning" in result.stdout.lower()


def test_installer_scan_reports_usb_devices(tmp_path):
    result = run_cli(["installer", "scan"], tmp_path)

    assert result.returncode == 0
    assert "usb" in result.stdout.lower()


def test_box_config_supports_permissions_network_and_storage(tmp_path):
    run_cli(["box", "create", "workbox"], tmp_path)
    result = run_cli(["box", "config", "workbox", "--network", "wifi", "--hardware", "camera", "--storage", "Documents"], tmp_path)

    assert result.returncode == 0
    payload = json.loads((tmp_path / "ashes_state.json").read_text())
    box = payload["boxes"][0]
    assert "wifi" in box["permissions"]["network"]
    assert "camera" in box["permissions"]["hardware"]
    assert "Documents" in box["permissions"]["storage"]


def test_settings_command_updates_global_defaults(tmp_path):
    result = run_cli(["settings", "set", "default_autostart", "true"], tmp_path)

    assert result.returncode == 0
    payload = json.loads((tmp_path / "ashes_state.json").read_text())
    assert payload["settings"]["default_autostart"] is True


def test_box_start_enforces_policy(tmp_path):
    run_cli(["box", "create", "restricted"], tmp_path)
    run_cli(["box", "config", "restricted", "--network", "wifi"], tmp_path)
    result = run_cli(["box", "start", "restricted"], tmp_path)

    assert result.returncode == 0
    payload = json.loads((tmp_path / "ashes_state.json").read_text())
    assert payload["boxes"][0]["status"] == "running"


def test_boot_flow_initializes_environment(tmp_path):
    result = run_cli(["os", "boot"], tmp_path)

    assert result.returncode == 0
    assert "booted" in result.stdout.lower()


def test_box_start_stop_cycle_updates_state(tmp_path):
    run_cli(["box", "create", "devbox"], tmp_path)
    start_result = run_cli(["box", "start", "devbox"], tmp_path)
    stop_result = run_cli(["box", "stop", "devbox"], tmp_path)

    assert start_result.returncode == 0
    assert stop_result.returncode == 0
    state_path = tmp_path / "ashes_state.json"
    payload = json.loads(state_path.read_text())
    box = payload["boxes"][0]
    assert box["status"] == "stopped"


def test_boot_menu_lists_boxes_and_templates(tmp_path):
    run_cli(["box", "create", "banking"], tmp_path)
    result = run_cli(["os", "menu"], tmp_path)

    assert result.returncode == 0
    assert "banking" in result.stdout
    assert "Personal Android" in result.stdout
