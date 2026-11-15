"""Mondes : Realme (monde réel) et Void (dimension parallèle). Chaque zone : batch.py, elements.py, loot.py, map.py.

Campagne : village -> forêt -> donjon (Realme), puis village -> forêt -> donjon (Void).
"""
import importlib

ORDRE = [("realme", "village"), ("realme", "foret"), ("realme", "donjon"),
         ("void", "village"), ("void", "foret"), ("void", "donjon")]


def module(index, nom):
    monde, biome = ORDRE[index]
    return importlib.import_module(f"map.{monde}.{biome}.{nom}")


def creer_zone(index, graine):
    """Génère la zone en vérifiant que sortie et boss sont atteignables (sinon nouvelle variante de la graine)."""
    from map.moteur import accessibles
    for essai in range(30):
        z = module(index, "map").creer(graine + essai * 7919)
        acces = accessibles(z, z.entree_prev)
        if z.entree_next in acces and all((b["x"], b["y"]) in acces for b in z.boss):
            break
    z.index = index
    return z


def creer_batch(index, zone):
    return module(index, "batch").creer_batch(zone)


def table_loot(index):
    return module(index, "loot")
