"""Rendu optimisé par lots de la carte de Cathédrale Inversée (couche statique pré-rendue + tuiles animées)."""
from map import moteur
from map.void.donjon import elements


def creer_batch(zone):
    return moteur.Batch(zone, elements.creer_tileset())
