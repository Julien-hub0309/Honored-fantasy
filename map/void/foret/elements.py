"""Éléments graphiques de Forêt Inversée : palette « void », tuiles, décors, ambiance lumineuse."""
from map import moteur

PALETTE = 'void'
AMBIANCE = (128, 128, 192)     # couleur de la couche d'ombre (blanc = plein jour)
PARAMS = dict(sol='void', mur='void', arbre='arbre', eau='abime', decors=('cristal', 'stalagmite', 'cristal'))


def creer_tileset():
    return moteur.construire_tileset(PALETTE, **PARAMS)
