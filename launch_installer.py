import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    repo = Path(__file__).resolve().parent
    try:
        subprocess.run([sys.executable, "-m", "ashes.gui_installer"], cwd=str(repo), check=True)
    except subprocess.CalledProcessError as exc:
        print(f"Installer exited with status {exc.returncode}")
        raise


if __name__ == "__main__":
    main()
