"""Éléments graphiques de Havre des Éclats : palette « void », tuiles, décors, ambiance lumineuse."""
from map import moteur

PALETTE = 'void'
AMBIANCE = (150, 150, 210)     # couleur de la couche d'ombre (blanc = plein jour)
PARAMS = dict(sol='void', mur='void', arbre='arbre', eau='abime', decors=('cristal', 'caisse', 'baleine'))


def creer_tileset():
    return moteur.construire_tileset(PALETTE, **PARAMS)
