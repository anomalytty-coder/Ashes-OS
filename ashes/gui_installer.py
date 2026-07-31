import sys
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:  # pragma: no cover
    tk = None
    messagebox = None


SUPPORTED_DEVICES = {"pixel-8", "pixel-8-pro", "pixel-9", "pixel-fold"}


def check_device(device_name: str) -> tuple[bool, str]:
    normalized = device_name.strip().lower()
    if normalized in SUPPORTED_DEVICES:
        return True, "This device appears to be supported."
    return False, "Warning: this device is not fully supported and may require manual steps."


def launch_gui() -> None:
    if tk is None:
        print("Tkinter is not available in this environment.")
        sys.exit(1)

    root = tk.Tk()
    root.title("Ashes Device Installer")
    root.geometry("560x320")

    tk.Label(root, text="Ashes Device Installer", font=("Segoe UI", 16, "bold")).pack(pady=(14, 8))
    tk.Label(root, text="Connect your Android phone over USB-C and select the device model.", wraplength=520).pack(pady=(0, 12))

    device_var = tk.StringVar(value="pixel-8")
    tk.Label(root, text="Device model:").pack()
    tk.Entry(root, textvariable=device_var, width=30).pack(pady=(4, 8))

    def run_check() -> None:
        supported, message = check_device(device_var.get())
        if supported:
            messagebox.showinfo("Compatibility", message)
        else:
            messagebox.showwarning("Compatibility warning", message)

    tk.Button(root, text="Check compatibility", command=run_check).pack(pady=8)
    tk.Button(root, text="Launch flashing workflow", command=lambda: messagebox.showinfo("Coming soon", "This GUI will launch the flash workflow in a future release.")).pack(pady=6)

    root.mainloop()


if __name__ == "__main__":
    launch_gui()
