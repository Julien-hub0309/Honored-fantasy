"""Rendu optimisé par lots de la carte de Forêt de Grisvoile (couche statique pré-rendue + tuiles animées)."""
from map import moteur
from map.realme.foret import elements


def creer_batch(zone):
    return moteur.Batch(zone, elements.creer_tileset())
