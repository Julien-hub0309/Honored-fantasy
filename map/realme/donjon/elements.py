"""Éléments graphiques de Catacombes du Guet : palette « donjon », tuiles, décors, ambiance lumineuse."""
from map import moteur

PALETTE = 'donjon'
AMBIANCE = (96, 100, 112)     # couleur de la couche d'ombre (blanc = plein jour)
PARAMS = dict(sol='dalle', mur='pierre', arbre='arbre', eau='eau', decors=('tonneau', 'caisse', 'statue'))


def creer_tileset():
    return moteur.construire_tileset(PALETTE, **PARAMS)
