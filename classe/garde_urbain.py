"""Classe Garde Urbain : statistiques de base, croissance, kit d'équipement, sorts et passif."""
from classe import ClasseDef

STATS_BASE = {'PV': 100, 'Mana': 50, 'FOR': 6, 'RES': 7, 'INT': 4, 'DEX': 5, 'AGI': 3}
# Gain moyen par niveau (fractionnaire ; la valeur est arrondie à l'inférieur sur l'ensemble)
CROISSANCE = {'PV': 13, 'Mana': 3, 'FOR': 0.45, 'RES': 0.55, 'INT': 0.15, 'DEX': 0.25, 'AGI': 0.15}
ARME_BASE = {"nom": 'Lame du Guet', "degats_base": 14}
EQUIPEMENT = ['melee', 'pistolet']                       # kit de base : melee / pistolet / grenade
SORTS_PAR_NIVEAU = {3: 'courage'}              # niveau d'apprentissage -> identifiant de pouvoir (objet/)

CLASSE = ClasseDef(
    id='garde_urbain', nom='Garde Urbain', role='Tank / Ligne de front (Bonus de défense unique)', description='Rempart du Guet de Pendysia. Sa posture défensive est unique : Résistance +200 % en Défense.',
    stats_base=STATS_BASE, croissance=CROISSANCE, arme=ARME_BASE, equipement=EQUIPEMENT, sorts_par_niveau=SORTS_PAR_NIVEAU,
    mult_defense=3.0,        # Défendre : RES x mult (2.5 = +150 %, 3.0 = +200 % Garde Urbain)
    reduction_passive=0.1, bonus_fuite=-0.1, bonus_critique=0.0, bonus_grenade=0.0,
    regen_pv=0.0, reduction_mana=0.0, efficacite_potion=1.0,
    passif='Bastion : -10 % de tous les dégâts subis.', sprite='garde_urbain', biomes=['Villes'], jouable=True,
)
