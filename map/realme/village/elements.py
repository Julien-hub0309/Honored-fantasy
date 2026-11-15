"""Éléments graphiques de Port-Brume : palette « ville », tuiles, décors, ambiance lumineuse."""
from map import moteur

PALETTE = 'ville'
AMBIANCE = (255, 246, 232)     # couleur de la couche d'ombre (blanc = plein jour)
PARAMS = dict(sol='pave', mur='brique', arbre='arbre', eau='eau', decors=('tonneau', 'caisse', 'baleine'))


def creer_tileset():
    return moteur.construire_tileset(PALETTE, **PARAMS)
