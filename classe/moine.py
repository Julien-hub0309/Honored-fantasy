"""Classe Moine : statistiques de base, croissance, kit d'équipement, sorts et passif."""
from classe import ClasseDef

STATS_BASE = {'PV': 115, 'Mana': 20, 'FOR': 7, 'RES': 7, 'INT': 5, 'DEX': 4, 'AGI': 4}
# Gain moyen par niveau (fractionnaire ; la valeur est arrondie à l'inférieur sur l'ensemble)
CROISSANCE = {'PV': 12, 'Mana': 4, 'FOR': 0.5, 'RES': 0.45, 'INT': 0.3, 'DEX': 0.3, 'AGI': 0.3}
ARME_BASE = {"nom": 'Bâton bénit', "degats_base": 14}
EQUIPEMENT = ['melee', 'pistolet', 'grenade']                       # kit de base : melee / pistolet / grenade
SORTS_PAR_NIVEAU = {1: 'courage', 6: 'reflexion'}              # niveau d'apprentissage -> identifiant de pouvoir (objet/)

CLASSE = ClasseDef(
    id='moine', nom='Moine', role='Combattant hybride / Soutien offensif', description="Ancien Surveillant de l'Abbaye. Sa foi le régénère et galvanise ses compagnons.",
    stats_base=STATS_BASE, croissance=CROISSANCE, arme=ARME_BASE, equipement=EQUIPEMENT, sorts_par_niveau=SORTS_PAR_NIVEAU,
    mult_defense=2.5,        # Défendre : RES x mult (2.5 = +150 %, 3.0 = +200 % Garde Urbain)
    reduction_passive=0.0, bonus_fuite=-0.05, bonus_critique=0.0, bonus_grenade=0.0,
    regen_pv=0.05, reduction_mana=0.0, efficacite_potion=1.2,
    passif='Ferveur : régénère 5 % des PV max à chaque tour, potions +20 %.', sprite='moine', biomes=['Donjons'], jouable=True,
)
