"""Classe Officier : statistiques de base, croissance, kit d'équipement, sorts et passif."""
from classe import ClasseDef

STATS_BASE = {'PV': 80, 'Mana': 70, 'FOR': 6, 'RES': 6, 'INT': 6, 'DEX': 6, 'AGI': 6}
# Gain moyen par niveau (fractionnaire ; la valeur est arrondie à l'inférieur sur l'ensemble)
CROISSANCE = {'PV': 10, 'Mana': 5, 'FOR': 0.4, 'RES': 0.35, 'INT': 0.4, 'DEX': 0.4, 'AGI': 0.4}
ARME_BASE = {"nom": "Sabre d'apparat", "degats_base": 13}
EQUIPEMENT = ['melee', 'pistolet', 'grenade']                       # kit de base : melee / pistolet / grenade
SORTS_PAR_NIVEAU = {1: 'reflexion', 6: 'courage'}              # niveau d'apprentissage -> identifiant de pouvoir (objet/)

CLASSE = ClasseDef(
    id='officier', nom='Officier', role='Polyvalent / Dégâts de zone', description="Stratège du Guet. Ses grenades à l'huile de baleine ravagent les escouades.",
    stats_base=STATS_BASE, croissance=CROISSANCE, arme=ARME_BASE, equipement=EQUIPEMENT, sorts_par_niveau=SORTS_PAR_NIVEAU,
    mult_defense=2.5,        # Défendre : RES x mult (2.5 = +150 %, 3.0 = +200 % Garde Urbain)
    reduction_passive=0.0, bonus_fuite=0.0, bonus_critique=0.03, bonus_grenade=0.3,
    regen_pv=0.0, reduction_mana=0.0, efficacite_potion=1.0,
    passif='Commandement : grenades +30 % de dégâts, +3 % de critique.', sprite='officier', biomes=['Villes'], jouable=True,
)
