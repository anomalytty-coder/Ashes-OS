import argparse
import json
from pathlib import Path
from typing import List


TEMPLATES = {
    "personal": "Personal Android",
    "banking": "Banking Android",
    "work": "Work Android",
    "dev": "Dev Linux",
    "disposable": "Disposable",
}


class BoxManager:
    def __init__(self, state_path: Path):
        self.state_path = state_path
        self.state = self._load_state()

    def _load_state(self) -> dict:
        if not self.state_path.exists():
            return {"boxes": [], "settings": {"default_autostart": False, "ui_theme": "dark"}}
        try:
            data = json.loads(self.state_path.read_text())
            data.setdefault("settings", {"default_autostart": False, "ui_theme": "dark"})
            return data
        except json.JSONDecodeError:
            return {"boxes": [], "settings": {"default_autostart": False, "ui_theme": "dark"}}

    def _save_state(self) -> None:
        self.state_path.write_text(json.dumps(self.state, indent=2))

    def create_box(self, name: str, template: str = "personal") -> dict:
        box = {
            "name": name,
            "template": template,
            "os_type": "android" if template != "dev" else "linux",
            "status": "stopped",
            "permissions": {"network": ["internet"], "hardware": [], "storage": []},
            "network_profile": "home",
            "storage_mounts": [],
        }
        self.state.setdefault("boxes", []).append(box)
        self._save_state()
        return box

    def list_boxes(self) -> List[dict]:
        return self.state.get("boxes", [])

    def configure_box(self, name: str, network: List[str], hardware: List[str], storage: List[str]) -> dict:
        for box in self.list_boxes():
            if box["name"] == name:
                box["permissions"]["network"] = network or box["permissions"]["network"]
                box["permissions"]["hardware"] = hardware or box["permissions"]["hardware"]
                box["permissions"]["storage"] = storage or box["permissions"]["storage"]
                box.setdefault("storage_mounts", [])
                box.setdefault("policy", {"allow_network": True, "allow_camera": False})
                self._save_state()
                return box
        raise KeyError(name)

    def set_setting(self, key: str, value: str) -> None:
        settings = self.state.setdefault("settings", {})
        if key == "default_autostart":
            settings[key] = value.lower() in {"1", "true", "yes", "on"}
        else:
            settings[key] = value
        self._save_state()

    def get_policy_status(self, box: dict) -> str:
        if box.get("permissions", {}).get("network") == ["wifi"]:
            return "allowed"
        return "default"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ashes")
    subparsers = parser.add_subparsers(dest="command", required=True)

    box_parser = subparsers.add_parser("box")
    box_subparsers = box_parser.add_subparsers(dest="box_command", required=True)

    box_subparsers.add_parser("list")

    create_parser = box_subparsers.add_parser("create")
    create_parser.add_argument("name")
    create_parser.add_argument("--template", choices=list(TEMPLATES.keys()), default="personal")

    start_parser = box_subparsers.add_parser("start")
    start_parser.add_argument("name")

    stop_parser = box_subparsers.add_parser("stop")
    stop_parser.add_argument("name")

    config_parser = box_subparsers.add_parser("config")
    config_parser.add_argument("name")
    config_parser.add_argument("--network", nargs="*", default=[])
    config_parser.add_argument("--hardware", nargs="*", default=[])
    config_parser.add_argument("--storage", nargs="*", default=[])

    os_parser = subparsers.add_parser("os")
    os_subparsers = os_parser.add_subparsers(dest="os_command", required=True)
    os_subparsers.add_parser("boot")
    os_subparsers.add_parser("menu")

    device_parser = subparsers.add_parser("device")
    device_subparsers = device_parser.add_subparsers(dest="device_command", required=True)
    plan_parser = device_subparsers.add_parser("plan")
    plan_parser.add_argument("--mode", choices=["pc", "app"], default="pc")

    settings_parser = subparsers.add_parser("settings")
    settings_subparsers = settings_parser.add_subparsers(dest="settings_command", required=True)
    settings_set = settings_subparsers.add_parser("set")
    settings_set.add_argument("key")
    settings_set.add_argument("value")

    installer_parser = subparsers.add_parser("installer")
    installer_subparsers = installer_parser.add_subparsers(dest="installer_command", required=True)
    check_parser = installer_subparsers.add_parser("check")
    check_parser.add_argument("--device")
    scan_parser = installer_subparsers.add_parser("scan")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    state_path = Path.cwd() / "ashes_state.json"
    manager = BoxManager(state_path)

    if args.command == "box" and args.box_command == "list":
        boxes = manager.list_boxes()
        if not boxes:
            print("No boxes configured")
        else:
            for box in boxes:
                print(f"{box['name']} [{box['status']}]")
        return

    if args.command == "box" and args.box_command == "create":
        box = manager.create_box(args.name, getattr(args, "template", "personal"))
        print(f"Created box '{box['name']}' using template '{box['template']}'")
        return

    if args.command == "box" and args.box_command == "config":
        try:
            box = manager.configure_box(args.name, args.network, args.hardware, args.storage)
        except KeyError:
            print(f"Box '{args.name}' not found")
            return
        print(f"Configured box '{box['name']}'")
        return

    if args.command == "box" and args.box_command == "start":
        for box in manager.list_boxes():
            if box["name"] == args.name:
                box["status"] = "running"
                box.setdefault("policy", {"allow_network": True, "allow_camera": False})
                policy_status = manager.get_policy_status(box)
                if policy_status == "allowed":
                    box["policy"]["allow_network"] = True
                if manager.state.get("settings", {}).get("default_autostart", False):
                    box["autostart"] = True
                manager._save_state()
                print(f"Started box '{args.name}' with policy {policy_status}")
                return
        print(f"Box '{args.name}' not found")
        return

    if args.command == "box" and args.box_command == "stop":
        for box in manager.list_boxes():
            if box["name"] == args.name:
                box["status"] = "stopped"
                manager._save_state()
                print(f"Stopped box '{args.name}'")
                return
        print(f"Box '{args.name}' not found")
        return

    if args.command == "os" and args.os_command == "boot":
        manager.state.setdefault("environment", {"boot_state": "booted", "boxes": []})
        manager.state["environment"]["boot_state"] = "booted"
        manager.state["environment"]["boot_menu"] = [
            {"name": box["name"], "template": box["template"], "status": box["status"]}
            for box in manager.list_boxes()
        ]
        manager._save_state()
        print("Ashes OS booted successfully")
        return

    if args.command == "os" and args.os_command == "menu":
        manager.state.setdefault("environment", {"boot_state": "booted", "boxes": []})
        manager.state["environment"]["boot_state"] = "booted"
        manager.state["environment"]["boot_menu"] = [
            {"name": box["name"], "template": box["template"], "status": box["status"]}
            for box in manager.list_boxes()
        ]
        manager._save_state()
        print("Ashes Boot Menu")
        print("Templates:")
        for key, label in TEMPLATES.items():
            print(f"- {label} ({key})")
        print("Boxes:")
        if not manager.list_boxes():
            print("- No boxes configured")
        else:
            for item in manager.state["environment"]["boot_menu"]:
                print(f"- {item['name']} [{item['status']}] ({item['template']})")
        return

    if args.command == "settings" and args.settings_command == "set":
        manager.set_setting(args.key, args.value)
        print(f"Set setting '{args.key}' to '{args.value}'")
        return

    if args.command == "device" and args.device_command == "plan":
        if args.mode == "pc":
            print("Ashes Device setup via PC:")
            print("- Connect the target Pixel device over a USB-C cable")
            print("- Use a host PC to flash a recovery image and install the Ashes hypervisor")
            print("- Reboot into the new Ashes boot flow and configure the initial Box menu")
            print("- Recommended for early adopters and developers")
        else:
            print("Ashes Device setup via Android app:")
            print("- Install an Android app on a supported device")
            print("- The app prepares the device and may request rooted or privileged access to reconfigure boot paths")
            print("- Use the app to transform the phone into an Ashes Device with a guided setup wizard")
            print("- Best for users who want a simpler, phone-first experience")
        return

    if args.command == "installer" and args.installer_command == "check":
        device_name = args.device or "unknown"
        supported = device_name.lower() in {"pixel-8", "pixel-8-pro", "pixel-9", "pixel-fold"}
        if supported:
            print(f"Device '{device_name}' looks supported for Ashes flashing.")
        else:
            print(f"Warning: device '{device_name}' is currently unsupported or only partially supported.")
            print("The installer can still launch, but flashing and booting may fail or require manual steps.")
        return

    if args.command == "installer" and args.installer_command == "scan":
        try:
            import usb.core
            import usb.util
        except ImportError:
            print("USB scan unavailable: pyusb is not installed.")
            return

        try:
            devices = []
            for dev in usb.core.find(find_all=True):
                devices.append({
                    "vendor_id": hex(dev.idVendor),
                    "product_id": hex(dev.idProduct),
                    "manufacturer": usb.util.get_string(dev, dev.iManufacturer) if dev.iManufacturer else "unknown",
                    "product": usb.util.get_string(dev, dev.iProduct) if dev.iProduct else "unknown",
                })
        except usb.core.NoBackendError:
            print("USB scan unavailable: no USB backend is available on this host.")
            return

        if not devices:
            print("No USB devices detected.")
            return

        print("USB devices detected:")
        for device in devices:
            print(
                f"- {device['manufacturer']} / {device['product']} "
                f"({device['vendor_id']}:{device['product_id']})"
            )
        return

    parser.error("unsupported command")


if __name__ == "__main__":
    main()
