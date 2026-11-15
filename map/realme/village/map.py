"""Génération de la carte de Port-Brume (realme/village) : tracé procédural reproductible (graine) + contenu."""
import random

from map import moteur
from map.realme.village import elements, loot

BIOME = 'village'
CLE = "realme/village"
PNJS = [{'nom': 'Capitaine Roke', 'sprite': 'garde_urbain', 'role': 'dialogue', 'slot': 'plaza', 'lignes': ["Roke : Condamnés, écoutez. L'Antagoniste porte la Marque de l'Outsider et rassemble les Runes Interdites.", 'Roke : Traquez-le, tuez-le, et vos têtes resteront sur vos épaules. Sinon... la corde.', 'Roke : Passez par la Forêt de Grisvoile, puis les Catacombes. Le Void vous attend au-delà.']}, {'nom': 'Orvel le Marchand', 'sprite': 'pnj_marchand', 'role': 'marchand', 'slot': 'boutiques', 'lignes': ['Orvel : Des condamnés qui font du commerce ? Voyons vos pièces.', 'Orvel : Je rachète au quatre cinquièmes de la valeur. Un homme doit vivre.']}, {'nom': 'Sœur Alma', 'sprite': 'pnj_sage', 'role': 'dialogue', 'slot': 'plaza', 'lignes': ["Alma : L'autel de l'Outsider vous soignera et gardera trace de votre passage.", 'Alma : Il observe ceux qui portent la Marque. Ne le fixez pas trop longtemps.']}, {'nom': 'Mousse du Port', 'sprite': 'pnj_civil', 'role': 'dialogue', 'slot': 'rues', 'lignes': ["Un gamin : On dit que la brume pue l'huile de baleine et la mort."]}, {'nom': 'Veuve Corvane', 'sprite': 'pnj_civile', 'role': 'dialogue', 'slot': 'rues', 'lignes': ["Veuve : Mon mari a suivi le Prévôt dans les Catacombes. Il n'est jamais revenu."]}, {'nom': 'Vieux Garde', 'sprite': 'pnj_civil', 'role': 'dialogue', 'slot': 'rues', 'lignes': ['Vieux garde : Les Gardes Urbains ont ordre de vous arrêter si vous traînez dans les ruelles. Restez sur la place !']}]


def creer(graine=0):
    rng = random.Random(f"{CLE}:{graine}")
    z = moteur.Zone('Port-Brume', 'realme', BIOME, elements.PALETTE, 1, 52, 34)
    moteur.gen_village(z, rng)
    return moteur.finaliser(z, rng, dict(cle=CLE, nb_coffres=0, boss=[], verrou=[], prosperite=2,
                                         ambiance=elements.AMBIANCE, musique='ville', pnjs=PNJS))
