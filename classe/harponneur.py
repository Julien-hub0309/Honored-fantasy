"""Classe Harponneur : statistiques de base, croissance, kit d'équipement, sorts et passif."""
from classe import ClasseDef

STATS_BASE = {'PV': 100, 'Mana': 100, 'FOR': 7, 'RES': 7, 'INT': 7, 'DEX': 7, 'AGI': 7}
# Gain moyen par niveau (fractionnaire ; la valeur est arrondie à l'inférieur sur l'ensemble)
CROISSANCE = {'PV': 10, 'Mana': 7, 'FOR': 0.4, 'RES': 0.3, 'INT': 0.45, 'DEX': 0.45, 'AGI': 0.5}
ARME_BASE = {"nom": 'Harpon vicieux', "degats_base": 15}
EQUIPEMENT = ['melee']                       # kit de base : melee / pistolet / grenade
SORTS_PAR_NIVEAU = {1: 'stop_time', 2: 'domino', 3: 'blink', 4: 'vision_tenebres', 5: 'reflexion', 6: 'nuee_vorace', 7: 'pli_temporel', 8: 'marche_ombre', 9: 'possession', 10: 'clignement_tueur', 11: 'attraction', 12: 'regard_vide', 13: 'longue_portee', 14: 'invocation_assassin', 15: 'envoutement', 16: 'lien_arcanique', 17: 'sosie', 18: 'rafale', 20: 'attriction'}
PASSIFS_PAR_NIVEAU = {6: 'agilite', 9: 'meurtrier_ombre', 13: 'soif_de_sang', 18: 'vitalite'}   # passifs de l'Outsider (classe/__init__.py : PASSIFS)              # niveau d'apprentissage -> identifiant de pouvoir (objet/)

CLASSE = ClasseDef(
    id='harponneur', nom='Harponneur', role='Contrôle de foule / Assassin', description="Chasseur de baleines et d'âmes. Il fige le temps et lie les destins.",
    stats_base=STATS_BASE, croissance=CROISSANCE, arme=ARME_BASE, equipement=EQUIPEMENT, sorts_par_niveau=SORTS_PAR_NIVEAU,
    mult_defense=2.5,        # Défendre : RES x mult (2.5 = +150 %, 3.0 = +200 % Garde Urbain)
    reduction_passive=0.0, bonus_fuite=0.15, bonus_critique=0.1, bonus_grenade=0.0,
    regen_pv=0.0, reduction_mana=0.0, efficacite_potion=1.0,
    passifs_par_niveau=PASSIFS_PAR_NIVEAU,
    passif='Chasseur : +10 % de critique, fuite facilitée.', sprite='harponneur', biomes=['Donjons'], jouable=True,
)
