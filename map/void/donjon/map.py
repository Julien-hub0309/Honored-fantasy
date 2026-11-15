"""Génération de la carte de Cathédrale Inversée (void/donjon) : tracé procédural reproductible (graine) + contenu."""
import random

from map import moteur
from map.void.donjon import elements, loot

BIOME = 'donjon'
CLE = "void/donjon"
PNJS = [{'nom': 'Fragment de Maëlys', 'sprite': 'pnj_sage', 'role': 'dialogue', 'slot': 'proche_entree', 'lignes': ["Voix : Le Maréchal Ossian garde la nef. Vaerith attend sur l'autel renversé.", "Voix : Ne le laissez pas prendre la place de l'Outsider."]}]


def creer(graine=0):
    rng = random.Random(f"{CLE}:{graine}")
    z = moteur.Zone('Cathédrale Inversée', 'void', BIOME, elements.PALETTE, 15, 60, 42)
    moteur.gen_donjon(z, rng, mid_boss=True)
    return moteur.finaliser(z, rng, dict(cle=CLE, nb_coffres=5, boss=[5, 6], verrou=[5, 6], prosperite=1,
                                         ambiance=elements.AMBIANCE, musique='void', pnjs=PNJS))
