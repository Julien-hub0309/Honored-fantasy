"""Classe Sorcière : statistiques de base, croissance, kit d'équipement, sorts et passif."""
from classe import ClasseDef

STATS_BASE = {'PV': 70, 'Mana': 80, 'FOR': 4, 'RES': 5, 'INT': 7, 'DEX': 7, 'AGI': 7}
# Gain moyen par niveau (fractionnaire ; la valeur est arrondie à l'inférieur sur l'ensemble)
CROISSANCE = {'PV': 8, 'Mana': 8, 'FOR': 0.15, 'RES': 0.25, 'INT': 0.6, 'DEX': 0.45, 'AGI': 0.45}
ARME_BASE = {"nom": 'Dague rituelle', "degats_base": 11}
EQUIPEMENT = ['melee']                       # kit de base : melee / pistolet / grenade
SORTS_PAR_NIVEAU = {1: 'blink', 2: 'attriction', 3: 'vision_tenebres', 4: 'reflexion', 5: 'nuee_vorace', 6: 'rafale', 8: 'possession', 9: 'pli_temporel', 10: 'regard_vide', 11: 'envoutement', 12: 'attraction', 13: 'marche_ombre', 14: 'lien_arcanique', 15: 'longue_portee', 16: 'sosie', 18: 'clignement_tueur', 20: 'invocation_assassin', 22: 'stop_time', 24: 'domino'}
PASSIFS_PAR_NIVEAU = {7: 'agilite', 12: 'vitalite', 17: 'soif_de_sang', 21: 'meurtrier_ombre'}   # passifs de l'Outsider (classe/__init__.py : PASSIFS)              # niveau d'apprentissage -> identifiant de pouvoir (objet/)

CLASSE = ClasseDef(
    id='sorciere', nom='Sorcière', role='Mage / Contrôle et dégâts garantis', description='Elle a pactisé avec le Void. Ses sorts ne ratent jamais leur cible.',
    stats_base=STATS_BASE, croissance=CROISSANCE, arme=ARME_BASE, equipement=EQUIPEMENT, sorts_par_niveau=SORTS_PAR_NIVEAU,
    mult_defense=2.5,        # Défendre : RES x mult (2.5 = +150 %, 3.0 = +200 % Garde Urbain)
    reduction_passive=0.0, bonus_fuite=0.05, bonus_critique=0.0, bonus_grenade=0.0,
    regen_pv=0.0, reduction_mana=0.1, efficacite_potion=1.0,
    passifs_par_niveau=PASSIFS_PAR_NIVEAU,
    passif='Affinité arcanique : coûts en mana -10 %.', sprite='sorciere', biomes=['Forêts'], jouable=True,
)
