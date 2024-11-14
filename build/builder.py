import subprocess
import os
import sys
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../log/builder.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('builder.py')


def install_pyinstaller():
    """Automatically installs PyInstaller if it is not already installed."""
    logger.info("PyInstaller is not installed. Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def check_python_installed():
    """Check if Python is installed by trying to run the 'python --version' command."""
    try:
        logger.info("Checking if Python is installed...")
        subprocess.check_call(["python", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def install_python():
    """Installs Python silently using a pre-downloaded installer."""
    installer_path = "python-3.10.7-amd64.exe"  # Make sure the installer is in the project folder
    logger.info("Python is not installed. Installing Python...")

    # Run the Python installer silently
    subprocess.check_call([installer_path, "/quiet", "InstallAllUsers=1", "PrependPath=1"], shell=True)

    logger.info("Python installed successfully. Please restart your terminal and run the script again.")
    sys.exit(1)  # After installation, exit to allow Python to be added to the system PATH


def build_executable():
    """Builds the executable from the specified Python script."""
    script_to_compile = os.path.abspath("../raw code/scheduler.py")
    output_folder = os.path.abspath("builder-EXE")  # Output folder for the executable
    icon_path = os.path.abspath("wolf_code.ico")  # Path to the .ico file

    # Check if Python is installed
    if not check_python_installed():
        install_python()

        # Try importing PyInstaller to check if it's installed
    try:
        import PyInstaller
    except ImportError:
        install_pyinstaller()

    # Remove the output directory if it exists (to avoid accumulating old files)
    if os.path.exists(output_folder):
        logger.info(f"Cleaning up the existing '{output_folder}' directory...")
        shutil.rmtree(output_folder)

    # Recreate the output directory
    os.makedirs(output_folder)

    # Use PyInstaller to compile the script
    try:
        pyinstaller_path = os.path.join(sys.exec_prefix, 'Scripts', 'pyinstaller.exe')
        logger.info(f"Building executable from {script_to_compile} into {output_folder}")

        # Compile with PyInstaller and direct all output to the 'builder-EXE' folder
        subprocess.check_call([
            pyinstaller_path,
            "--onefile",
            "--distpath", output_folder,  # Where the executable will be saved
            "--workpath", os.path.join(output_folder, "build"),  # Where the build folder will be saved
            "--specpath", output_folder,  # Where the .spec file will be saved
            "--icon", icon_path,  # Set the icon for the executable
            script_to_compile
        ])

        logger.info(f"Build completed. Check the '{output_folder}' folder for the new executable.")
    except subprocess.CalledProcessError as e:
        logger.info(f"Error during the build process: {e}")


if __name__ == "__main__":
    build_executable()
