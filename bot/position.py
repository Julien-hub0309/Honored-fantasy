"""Positions des combattants sur l'écran de combat (formation façon Final Fantasy : ennemis à gauche, groupe à droite).

Les coordonnées sont celles des *pieds* du sprite sur l'écran interne 480x270 (panneaux d'interface à partir de y=200).
"""


def positions_ennemis(n, boss=False):
    if boss or n == 1:
        return [(140, 176)] * n
    return {2: [(165, 150), (120, 186)],
            3: [(175, 132), (130, 160), (175, 188)],
            4: [(185, 128), (140, 150), (185, 172), (130, 194)],
            5: [(195, 126), (150, 146), (195, 166), (110, 168), (150, 192)]}[n]


def positions_allies(n):
    return [(352, 130), (392, 154), (352, 178), (392, 198)][:n]


def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
