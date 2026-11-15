"""Rendu optimisé par lots de la carte de Forêt Inversée (couche statique pré-rendue + tuiles animées)."""
from map import moteur
from map.void.foret import elements


def creer_batch(zone):
    return moteur.Batch(zone, elements.creer_tileset())
