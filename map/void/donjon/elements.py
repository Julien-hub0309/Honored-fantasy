"""Éléments graphiques de Cathédrale Inversée : palette « void », tuiles, décors, ambiance lumineuse."""
from map import moteur

PALETTE = 'void'
AMBIANCE = (88, 82, 138)     # couleur de la couche d'ombre (blanc = plein jour)
PARAMS = dict(sol='void', mur='void', arbre='arbre', eau='abime', decors=('statue', 'pilier', 'cristal'))


def creer_tileset():
    return moteur.construire_tileset(PALETTE, **PARAMS)
