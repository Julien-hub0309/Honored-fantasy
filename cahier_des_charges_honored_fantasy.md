# Cahier des Charges (GDD & Spécifications Techniques) : *Honored Fantasy*

## 1. Présentation Générale & Univers (Lore)
* **Titre du projet :** Honored Fantasy
* **Genre :** RPG tactique au tour par tour, Exploration 2D.
* **Langage & Architecture :** Python (architecture modulaire orientée objet/fonctionnelle).
* **Synopsis :** Sur le continent de **Pendysia**, un groupe d'explorateurs condamnés à mort se voit confier une mission suicide pour obtenir leur rédemption : traquer et éliminer l'Antagoniste principal. Cet ancien porteur de la *Marque de l'Outsider* cherche à rassembler les **Runes Interdites** afin d'usurper la place de l'Outsider dans le **Void** (le Grand Vide). 
* **Objectif du jeu :** Traverser le monde réel (*Realme*) et la dimension parallèle (*Void*), vaincre les **6 Boss** (dont l'Antagoniste final), récupérer les Runes Interdites et sceller définitivement la faille entre le Void et la réalité.

---

## 2. Système de Classes et Statistiques

### 2.1. Les Caractéristiques (Stats)
Chaque entité (allié ou ennemi) est régie par 5 statistiques fondamentales et 2 jauges :
* **PV (Points de Vie) :** Détermine la survie de l'entité (0 PV = mort/KO).
* **Mana (Points de Magie) :** Ressource consommée pour lancer des sorts/compétences.
* **Force (FOR) :** Augmente les dégâts physiques infligés (corps à corps).
* **Résistance (RES) :** Réduit les dégâts subis.
* **Intelligence (INT) :** Réduit le coût en Mana des compétences magiques et/ou augmente leur efficacité.
* **Dextérité (DEX) :** Augmente la précision (chances de toucher) et le taux de coups critiques.
* **Agilité (AGI) :** Augmente l'esquive (chances d'éviter une attaque ou un critique) et les chances de réussite de fuite.

### 2.2. Les Classes Jouables (et Archétypes)
Le jeu propose 5 classes principales (ainsi qu'un archétype "Monstre" pour les ennemis) :

| Classe | Équipement / Compétences de base | Rôle tactique |
| :--- | :--- | :--- |
| **Garde Urbain** | Arme de corps à corps + Pistolet | Tank / Ligne de front (Bonus de défense unique) |
| **Officier** | Arme de corps à corps + Pistolet + Grenade | Polyvalent / Dégâts de zone |
| **Sorcière** | Arme de corps à corps + *Blink* + *Attriction* | Mage / Contrôle et dégâts garantis |
| **Moine** | Arme de corps à corps + Pistolet + Grenade | Combattant hybride / Soutien offensif |
| **Harponneur** | Arme de corps à corps + *Stop Time* + *Domino* | Contrôle de foule (Crowd Control) / Assassin |

*(Note : Dans l'architecture, le Moine et l'Officier partagent actuellement le même kit d'équipement de base ; il conviendra de les différencier par leurs statistiques de base ou leurs passifs).*

---

## 3. Système de Combat (Tour par Tour)

### 3.1. Déroulement d'un tour
À chaque tour, une entité peut effectuer **deux phases d'action** dans cet ordre :
1. **Phase d'objet (Optionnelle) :** Utilisation d'un seul objet depuis l'inventaire (ex: Potion).
2. **Phase d'action principale (Obligatoire) :** Choix parmi 4 actions :
   * **Attaquer :** Utiliser une arme équipée.
   * **Magie :** Lancer un sort (considéré comme une action offensive/principale au même titre que l'attaque).
   * **Défendre :** Augmente temporairement la caractéristique **Résistance de +150%** pour le tour en cours (**+200%** exclusivement pour la classe *Garde Urbain*).
   * **Fuir :** Tente de quitter le combat. Le taux de réussite est calculé selon un jet de probabilité pondéré par la statistique d'**Agilité** du lanceur face à celle des ennemis.

### 3.2. Arsenal, Objets et Compétences Magiques

#### Armes & Objets Offensifs
* **Arme de corps à corps :** Inflige des dégâts physiques basés sur la *Force* et les dégâts de base de l'arme. Soumis à la *Dextérité* (toucher/critique) et à l'*Agilité* adverse (esquive).
* **Pistolet :** Attaque à distance à haut risque/haute récompense. **Garantit un coup critique** s'il touche, mais possède un taux d'échec élevé (binaire : Critique ou Raté).
* **Grenade :** Inflige des dégâts de zone (AoE) **inévitables** (ignore totalement la statistique d'*Agilité* des ennemis).

#### Sorts & Pouvoirs de l'Outsider
* **Attriction :** Inflige des dégâts magiques et applique un malus qui **réduit l'Agilité de la cible à 0 (ou la diminue fortement) pendant 2 tours**.
* **Stop Time :** Gèle le temps. **Empêche toutes les entités (alliés et ennemis) d'attaquer pendant 2 tours**, à l'exception unique du lanceur du sort.
* **Blink (Clignement) :** Téléportation offensive qui inflige des dégâts bruts garantis (**ne peut ni échouer, ni infliger de coup critique**).
* **Domino :** Lie deux ennemis pendant **3 tours**. Tous les dégâts subis par l'une des cibles sont intégralement répliqués sur l'autre. Si l'un des deux meurt, le second meurt instantanément.

#### Buffs & Consommables
* **Courage :** Augmente la **Force et la Résistance de +2** pendant **3 tours**.
* **Réflexion :** Augmente l'**Intelligence et la Dextérité** (durée à définir, par défaut 3 tours).
* **Potion de Vie / Potion de Vie+ :** Restaure respectivement **50%** ou **100%** des PV maximum.
* **Potion de Mana / Potion de Mana+ :** Restaure respectivement **50%** ou **100%** du Mana maximum.

---

## 4. Bestiaire & Équilibrage des Ennemis (Bots)

Les ennemis apparaissent en escouades selon les biomes explorés :

| Ennemi | Biomes principaux | PV | Mana | FOR | RES | INT | DEX | AGI | Composition de groupe |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Garde Urbain** | Villes | 100 | 50 | 6 | 7 | 4 | 5 | 3 | Groupe de 3 |
| **Officier** | Villes | 80 | 70 | 6 | 6 | 6 | 6 | 6 | Groupe de 2, ou 1 avec des Gardes |
| **Sorcière** | Forêts | 70 | 80 | 4 | 5 | 7 | 7 | 7 | Groupe de 3-4, ou 2 avec des Monstres |
| **Monstre** | Forêts | 150 | 0 | 7 | 7 | 2 | 3 | 3 | Groupe de 4-5 |
| **Moine** | Donjons | 115 | 20 | 7 | 7 | 5 | 4 | 4 | Groupe de 2 |
| **Harponneur** | Donjons | 100 | 100 | 7 | 7 | 7 | 7 | 7 | Groupe de 2 |

*(Note : 6 Boss majeurs répartis entre le Realme et le Void viendront compléter ce bestiaire).*

---

## 5. Exploration, Économie & Progression

### 5.1. Rencontres Aléatoires
Les combats se déclenchent aléatoirement en fonction du nombre de pas effectués par le joueur dans une zone :
* **Forêt :** Forte probabilité de rencontrer des *Monstres* (et *Sorcières*).
* **Ville :** Forte probabilité d'affronter des *PNJ hostiles* (*Gardes Urbains*, *Officiers*).
* **Donjon :** Probabilité équiprobable d'apparition pour tous les types d'ennemis.

### 5.2. Système de Loot et Rareté
Le butin est classé en **6 niveaux de rareté** :
1. *Commun*, 2. *Peu commun*, 3. *Rare* $\rightarrow$ Apparaissent aléatoirement au sol sur la carte. Le taux d'apparition augmente dynamiquement après un certain nombre de combats remportés.
4. *Très rare*, 5. *Épique*, 6. *Légendaire* $\rightarrow$ Exclusifs aux **coffres** et aux récompenses de **Boss**.

### 5.3. PNJ et Économie (Magasins)
* Présence de PNJ neutres pour les dialogues, quêtes et le commerce.
* **Indexation des prix :** Plus une ville est prospère/riche, plus les prix des boutiques sont élevés, mais plus la rareté des objets proposés à la vente est haute.
* **Revente :** Le joueur peut vendre ses objets aux marchands au taux fixe de **80% de leur valeur d'achat** (décote de -20%).

---

## 6. Direction Artistique (DA)

* **Style visuel :** Pixel Art 2D riche en textures, avec des personnages au format **Chibi**.
* **Identité chromatique par biome :**
  * **Villes (*Realme*) :** Atmosphère propre, lumineuse et verdoyante. Palette : *Jaune, Orange, Rouge*.
  * **Forêts (*Realme*) :** Végétation dense, hautes herbes. Palette : *Jaune, Vert clair, Vert foncé, Gris*.
  * **Donjons (*Realme* & *Void*) :** Sombres, étroits et lugubres. Palette : *Vert foncé, Marron, Gris, Noir*.
  * **Le Void (Dimension parallèle) :** Esthétique ésotérique, surréaliste et paradoxale (fragments de réalité flottants, gravité inversée). Palette : *Bleu, Violet, Gris, Noir*.

---

## 7. Architecture Logicielle (Arborescence du Projet)

Le projet est structuré en modules Python distincts séparant les données, la logique de combat, l'exploration, l'interface (HUD) et les cartes :

```text
.
├── assets
│   ├── icone
│   ├── __init__.py
│   ├── map
│   │   ├── realme
│   │   └── void
│   ├── objet
│   └── pnj
├── bot
│   ├── cible.py
│   ├── degats.py
│   ├── etat.py
│   ├── ia_agressive_melee.py
│   ├── ia_protector_defensive.py
│   ├── ia_ranged_skirmisher.py
│   ├── ia_support_healer.py
│   └── position.py
├── cahier_des_charges_honored_fantasy.md
├── classe
│   ├── garde_urbain.py
│   ├── harponneur.py
│   ├── __init__.py
│   ├── moine.py
│   ├── monstre.py
│   ├── officier.py
│   └── sorciere.py
├── combat
│   ├── combat_tour_par_tour.py
│   └── __init__.py
├── exploration
│   ├── loot_systeme.py
│   ├── magasin.py
│   ├── pnj.py
│   ├── rencontre_aleatoire.py
│   └── revente.py
├── honored_fantasy.py
├── HUD
│   ├── hud.py
│   ├── __init__.py
│   └── __pycache__
├── installateur.py
├── map
│   ├── __init__.py
│   ├── __pycache__
│   ├── realme
│   │   ├── donjon
│   │   │   ├── batch.py
│   │   │   ├── elements.py
│   │   │   ├── __init__.py
│   │   │   ├── loot.py
│   │   │   ├── map.py
│   │   │   └── __pycache__
│   │   ├── foret
│   │   │   ├── batch.py
│   │   │   ├── elements.py
│   │   │   ├── __init__.py
│   │   │   ├── loot.py
│   │   │   ├── map.py
│   │   │   └── __pycache__
│   │   └── village
│   │       ├── batch.py
│   │       ├── elements.py
│   │       ├── __init__.py
│   │       ├── loot.py
│   │       ├── map.py
│   │       └── __pycache__
│   └── void
│       ├── donjon
│       │   ├── batch.py
│       │   ├── elements.py
│       │   ├── __init__.py
│       │   ├── loot.py
│       │   ├── map.py
│       │   └── __pycache__
│       ├── foret
│       │   ├── batch.py
│       │   ├── elements.py
│       │   ├── __init__.py
│       │   ├── loot.py
│       │   ├── map.py
│       │   └── __pycache__
│       └── village
│           ├── batch.py
│           ├── elements.py
│           ├── __init__.py
│           ├── loot.py
│           ├── map.py
│           └── __pycache__
├── objet
│   ├── attraction.py
│   ├── blink.py
│   ├── courage.py
│   ├── domino.py
│   ├── epee.py
│   ├── grenade.py
│   ├── pistolet.py
│   ├── potion_mana.py
│   ├── potion_vie.py
│   ├── reflexion.py
│   └── stop_time.py
└── parametre
    ├── clavier.py
    ├── config.json
    ├── config.py
    ├── graphismes.py
    ├── __init__.py
    ├── options.py
    ├── __pycache__
    └── souris.py

33 directories, 77 files

```

---

## 8. Directives Techniques pour l'IA (Règles d'implémentation)

Pour toute génération ou modification de code sur ce projet, l'IA doit respecter les règles suivantes :
1. **Respect strict de l'arborescence :** Ne pas créer de fichiers en dehors des dossiers prévus sans validation. Utiliser les fichiers `__init__.py` pour exposer proprement les modules.
2. **Séparation des responsabilités :** 
   * Les formules mathématiques (dégâts, esquive, fuite) doivent résider dans `classe/<nom_classe>/`.
   * L'orchestration des tours doit rester centralisée dans `combat/system_combat/tour_par_tour.py`.
   * L'affichage (rendu graphique, sprites, UI) doit être découplé de la logique métier (utilisation de `batch.py` pour le rendu optimisé des tuiles/éléments et `hud.py` pour l'interface).
3. **Cohérence des données :** Les états (`pv.py`, `mana.py`, `rang.py`) doivent être synchronisés entre le module `exploration` et le module `combat` lors des transitions de scène.
4. **Points clarifiés (implémentés) :**
   * *Formules exactes :* voir `classe/formules.py` et le README (FOR/RES, DEX/AGI, INT, fuite).
   * *Les 6 Boss :* `bot/boss.py` (boss 1 à 6 : Reine Ronce, Prévôt Hargrave, Abbesse Veyra, Kael, Maréchal Ossian, Lord Vaerith).
   * *Bibliothèque graphique :* **Pygame** (résolution interne 480x270, mise à l'échelle entière).
   * *Moine / Officier :* différenciés par passifs (Moine : régénération 5 %/tour, Courage ; Officier : grenades +30 %, Réflexion).
