"""Génération de la carte de Havre des Éclats (void/village) : tracé procédural reproductible (graine) + contenu."""
import random

from map import moteur
from map.void.village import elements, loot

BIOME = 'village'
CLE = "void/village"
PNJS = [{'nom': "Colporteur d'Éclats", 'sprite': 'pnj_marchand', 'role': 'marchand', 'slot': 'boutiques', 'lignes': ['Colporteur : Ici, tout est plus cher... et plus rare. Le Void aime les belles choses.', 'Colporteur : Mes pièces sont tordues, mon commerce est honnête.']}, {'nom': 'Veilleuse du Havre', 'sprite': 'pnj_sage', 'role': 'dialogue', 'slot': 'plaza', 'lignes': ['Veilleuse : Le sol flotte, le ciel est dessous. Habituez-vous.', "Veilleuse : L'autel tient encore, il vous soignera."]}, {'nom': 'Âme égarée', 'sprite': 'pnj_civile', 'role': 'dialogue', 'slot': 'rues', 'lignes': ["Âme : Vaerith a rassemblé cinq Runes. Il n'en manque qu'une... la vôtre.", 'Âme : Kael garde la forêt inversée. Il fige le temps pour mieux chasser.']}]


def creer(graine=0):
    rng = random.Random(f"{CLE}:{graine}")
    z = moteur.Zone('Havre des Éclats', 'void', BIOME, elements.PALETTE, 10, 50, 34)
    moteur.gen_village(z, rng)
    return moteur.finaliser(z, rng, dict(cle=CLE, nb_coffres=0, boss=[], verrou=[], prosperite=4,
                                         ambiance=elements.AMBIANCE, musique='void', pnjs=PNJS))
