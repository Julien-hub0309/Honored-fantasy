"""Classe Monstre : statistiques de base, croissance, kit d'équipement, sorts et passif."""
from classe import ClasseDef

STATS_BASE = {'PV': 150, 'Mana': 0, 'FOR': 7, 'RES': 7, 'INT': 2, 'DEX': 3, 'AGI': 3}
# Gain moyen par niveau (fractionnaire ; la valeur est arrondie à l'inférieur sur l'ensemble)
CROISSANCE = {'PV': 18, 'Mana': 0, 'FOR': 0.5, 'RES': 0.4, 'INT': 0.1, 'DEX': 0.2, 'AGI': 0.2}
ARME_BASE = {"nom": 'Griffes', "degats_base": 12}
EQUIPEMENT = ['melee']                       # kit de base : melee / pistolet / grenade
SORTS_PAR_NIVEAU = {}              # niveau d'apprentissage -> identifiant de pouvoir (objet/)

CLASSE = ClasseDef(
    id='monstre', nom='Monstre', role='Archétype ennemi (bestiaire)', description='Créatures mutées par la peste du Void.',
    stats_base=STATS_BASE, croissance=CROISSANCE, arme=ARME_BASE, equipement=EQUIPEMENT, sorts_par_niveau=SORTS_PAR_NIVEAU,
    mult_defense=2.5,        # Défendre : RES x mult (2.5 = +150 %, 3.0 = +200 % Garde Urbain)
    reduction_passive=0.0, bonus_fuite=-0.2, bonus_critique=0.0, bonus_grenade=0.0,
    regen_pv=0.0, reduction_mana=0.0, efficacite_potion=1.0,
    passif='Aucun.', sprite='monstre', biomes=['Forêts'], jouable=False,
)
