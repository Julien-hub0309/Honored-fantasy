"""Chargeur / sauvegarde de la configuration utilisateur (config.json)."""
import copy
import json
import os

CHEMIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAUT = {
    "touches": {
        "haut": ["z", "w", "up"],
        "bas": ["s", "down"],
        "gauche": ["q", "a", "left"],
        "droite": ["d", "right"],
        "valider": ["return", "space", "e"],
        "annuler": ["escape", "backspace", "x"],
        "menu": ["tab", "m"],
        "pouvoir": ["p", "c"],
        "courir": ["left shift", "right shift"],
        "plein_ecran": ["f11"],
    },
    "graphismes": {"plein_ecran": False, "echelle": 2, "fps_max": 60, "ambiance": True, "scanlines": False},
    "audio": {"volume": 0.5, "muet": False},
}


def _fusion(base, ajout):
    for cle, val in ajout.items():
        if isinstance(val, dict) and isinstance(base.get(cle), dict):
            _fusion(base[cle], val)
        else:
            base[cle] = val
    return base


def charger():
    conf = copy.deepcopy(DEFAUT)
    try:
        with open(CHEMIN, "r", encoding="utf-8") as f:
            _fusion(conf, json.load(f))
    except (OSError, ValueError):
        pass
    return conf


def sauvegarder(conf):
    try:
        with open(CHEMIN, "w", encoding="utf-8") as f:
            json.dump(conf, f, indent=2, ensure_ascii=False)
    except OSError:
        pass
