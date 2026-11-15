"""Rendu optimisé par lots de la carte de Havre des Éclats (couche statique pré-rendue + tuiles animées)."""
from map import moteur
from map.void.village import elements


def creer_batch(zone):
    return moteur.Batch(zone, elements.creer_tileset())
