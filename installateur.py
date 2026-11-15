#!/usr/bin/env python3
"""Installe un venv, télécharge les dépendances et crée un raccourci bureau avec icône."""
import os
import subprocess
import sys
from pathlib import Path

DEPENDANCES = ["pygame>=2.5"]
NOM_VENV = "venv"
NOM_JEU = "honored_fantasy.py"
NOM_RACCOURCI = "Honored Fantasy"


def creer_venv(racine_projet: Path):
    """Crée l'environnement virtuel s'il n'existe pas."""
    dossier_venv = racine_projet / NOM_VENV
    if not dossier_venv.exists():
        print(f"Création de l'environnement virtuel dans '{NOM_VENV}'...")
        subprocess.check_call([sys.executable, "-m", "venv", NOM_VENV])
    else:
        print(f"L'environnement virtuel '{NOM_VENV}' existe déjà.")


def obtenir_python_venv(racine_projet: Path) -> Path:
    """Renvoie le chemin vers l'exécutable Python du venv selon l'OS."""
    if sys.platform == "win32":
        return racine_projet / NOM_VENV / "Scripts" / "python.exe"
    else:
        return racine_projet / NOM_VENV / "bin" / "python"


def installer_dependances(python_venv: Path):
    """Installe les dépendances dans le venv."""
    print("Installation des dépendances :", ", ".join(DEPENDANCES))
    try:
        subprocess.check_call(
            [str(python_venv), "-m", "pip", "install", "--upgrade", "pip"]
        )
        subprocess.check_call([str(python_venv), "-m", "pip", "install", *DEPENDANCES])
    except subprocess.CalledProcessError:
        sys.exit("Échec de l'installation des dépendances.")


def creer_raccourci_bureau(racine_projet: Path, python_venv: Path):
    """Crée un raccourci sur le bureau avec l'icône personnalisée (Windows et Linux)."""
    script_jeu = racine_projet / NOM_JEU
    chemin_icone = racine_projet / "assets" / "icone" / "icone.png"

    if sys.platform == "win32":
        try:
            bureau = Path(os.path.expanduser("~")) / "Desktop"
            chemin_lnk = bureau / f"{NOM_RACCOURCI}.lnk"
            
            # Si le fichier d'icône est un .png, Windows préfère souvent un .ico, 
            # mais PowerShell accepte le .png pour la propriété IconLocation dans de nombreux cas,
            # ou on pointe directement dessus.
            icone_str = str(chemin_icone) if chemin_icone.exists() else ""

            # Script PowerShell pour créer le raccourci avec icône
            commande_ps = (
                f"$WshShell = New-Object -ComObject WScript.Shell; "
                f"$Shortcut = $WshShell.CreateShortcut('{chemin_lnk}'); "
                f"$Shortcut.TargetPath = '{python_venv}'; "
                f"$Shortcut.Arguments = '\"{script_jeu}\"'; "
                f"$Shortcut.WorkingDirectory = '{racine_projet}'; "
            )
            if icone_str:
                commande_ps += f"$Shortcut.IconLocation = '{icone_str},0'; "
            
            commande_ps += "$Shortcut.Save()"

            subprocess.check_call(["powershell", "-Command", commande_ps])
            print(f"Raccourci bureau créé avec succès : {chemin_lnk}")
        except Exception as e:
            print(f"Impossible de créer le raccourci Windows automatiquement : {e}")

    elif sys.platform.startswith("linux"):
        try:
            bureau = Path(os.path.expanduser("~")) / "Desktop"
            if not bureau.exists():
                bureau_fr = Path(os.path.expanduser("~")) / "Bureau"
                if bureau_fr.exists():
                    bureau = bureau_fr

            icone_str = str(chemin_icone) if chemin_icone.exists() else ""

            contenu_desktop = f"""[Desktop Entry]
Type=Application
Name={NOM_RACCOURCI}
Exec="{python_venv}" "{script_jeu}"
Path={racine_projet}
Terminal=false
Categories=Game;
"""
            if icone_str:
                contenu_desktop += f"Icon={icone_str}\n"

            chemin_desktop = bureau / f"{NOM_RACCOURCI.lower().replace(' ', '_')}.desktop"
            chemin_desktop.write_text(contenu_desktop, encoding="utf-8")
            chemin_desktop.chmod(0o755)
            print(f"Raccourci Linux créé avec succès : {chemin_desktop}")
        except Exception as e:
            print(f"Impossible de créer le raccourci Linux : {e}")


def main():
    racine_projet = Path(__file__).resolve().parent

    # 1. Création du venv
    creer_venv(racine_projet)
    python_venv = obtenir_python_venv(racine_projet)

    # 2. Installation des paquets
    installer_dependances(python_venv)

    # 3. Création du raccourci bureau avec l'icône
    creer_raccourci_bureau(racine_projet, python_venv)

    print(f"\n Tout est prêt ! Vous pouvez lancer le jeu via le raccourci ou avec :")
    if sys.platform == "win32":
        print(f"   {NOM_VENV}\\Scripts\\python {NOM_JEU}")
    else:
        print(f"   ./{NOM_VENV}/bin/python {NOM_JEU}")


if __name__ == "__main__":
    main()