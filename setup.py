import os
import argparse
import subprocess
import sys


def check_and_install_requirements():
    print("Checking and installing required packages...")
    requirements = [
        "pillow",  # For image processing
        "qrcode",  # For QR code generation
        "names",  # For generating random names
    ]

    try:
        # Optional package
        import importlib.util

        if importlib.util.find_spec("reportlab") is None:
            requirements.append("reportlab")  # For PDF generation
    except:
        requirements.append("reportlab")

    for package in requirements:
        try:
            __import__(package)
            print(f"✓ {package} already installed")
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed")

    print("All required packages are installed.\n")


def setup_database(reset=False):
    from populate_db import populate_database

    populate_database(reset=reset)


def create_directories():
    print("Creating required directories...")
    # Create tickets directory
    os.makedirs("tickets", exist_ok=True)
    print("✓ Created tickets directory")
    print()


def main():
    parser = argparse.ArgumentParser(description="Setup the Theater Ticket System")
    parser.add_argument("--reset", action="store_true", help="Reset the database")
    parser.add_argument(
        "--skip-deps", action="store_true", help="Skip dependency installation"
    )
    args = parser.parse_args()

    print("=== Theater Ticket System Setup ===\n")

    if not args.skip_deps:
        check_and_install_requirements()

    create_directories()
    setup_database(args.reset)

    print("\nSetup complete! You can now run the application with:")
    print("  python main_sql.py")


if __name__ == "__main__":
    main()
