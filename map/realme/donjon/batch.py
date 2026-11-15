"""Rendu optimisé par lots de la carte de Catacombes du Guet (couche statique pré-rendue + tuiles animées)."""
from map import moteur
from map.realme.donjon import elements


def creer_batch(zone):
    return moteur.Batch(zone, elements.creer_tileset())
