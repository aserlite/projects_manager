import os
import subprocess
import sys
import urllib.request

def check_and_install(package_name, check_command, install_command, post_install=None):
    try:
        # Vérifier si le package est installé
        subprocess.run(check_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"{package_name} est deja installe.")
    except subprocess.CalledProcessError:
        print(f"{package_name} n'est pas installe. Installation en cours...")
        # Installer le package
        subprocess.run(install_command, check=True, shell=True)
        if post_install:
            subprocess.run(post_install, check=True, shell=True)
        print(f"{package_name} a été installé avec succès.")

def install_docker():
    if sys.platform.startswith("win"):
        check_and_install(
            "Docker Desktop",
            ["docker", "--version"],
            ["winget", "install", "--id", "Docker.DockerDesktop", "--silent"]
        )
    elif sys.platform.startswith("linux"):
        check_and_install(
            "Docker",
            ["docker", "--version"],
            ["sudo", "apt-get", "install", "-y", "docker.io"]
        )

def install_ddev():
    if sys.platform.startswith("win"):
        ddev_install_script = "https://raw.githubusercontent.com/drud/ddev/master/scripts/install_ddev_windows.sh"
        check_and_install(
            "DDEV",
            ["ddev", "--version"],
            ["powershell", "-Command", f"Invoke-WebRequest -Uri {ddev_install_script} -OutFile install_ddev.ps1; powershell -ExecutionPolicy Bypass -File install_ddev.ps1"]
        )
    elif sys.platform.startswith("linux"):
        check_and_install(
            "DDEV",
            ["ddev", "--version"],
            ["sudo", "apt-get", "install", "-y", "ddev"]
        )

def install_git():
    if sys.platform.startswith("win"):
        check_and_install(
            "Git",
            ["git", "--version"],
            ["winget", "install", "--id", "Git.Git", "--silent"]
        )
    elif sys.platform.startswith("linux"):
        check_and_install(
            "Git",
            ["git", "--version"],
            ["sudo", "apt-get", "install", "-y", "git"]
        )

def install_requirements():
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Les dependances Python ont ete installees avec succes.")
    except subprocess.CalledProcessError:
        print("Erreur lors de l'installation des dependances Python.")

def main():
    if sys.platform not in ["win32", "linux"]:
        print("Ce script ne prend en charge que Windows et Linux.")
        return

    install_docker()
    install_ddev()
    install_git()
    install_requirements()

if __name__ == "__main__":
    main()
