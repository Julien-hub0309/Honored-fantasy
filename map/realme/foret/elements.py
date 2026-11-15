"""Éléments graphiques de Forêt de Grisvoile : palette « foret », tuiles, décors, ambiance lumineuse."""
from map import moteur

PALETTE = 'foret'
AMBIANCE = (200, 214, 182)     # couleur de la couche d'ombre (blanc = plein jour)
PARAMS = dict(sol='herbe', mur='pierre', arbre='arbre', eau='eau', decors=('buisson', 'rocher', 'rocher'))


def creer_tileset():
    return moteur.construire_tileset(PALETTE, **PARAMS)
