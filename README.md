# Honored Fantasy — édition Animaux

Variante où les quatre héros sont, respectivement, un **capybara**, un **panda**, un **renard** et un **loup** (chibi animal portant le costume de la classe). Par défaut : Capy (Garde Urbain), Bao (Moine), Roux (Sorcière), Fenris (Harponneur). Noms et classes restent modifiables à la création ; l'espèce est liée à l'emplacement (1 à 4).

RPG tactique au tour par tour + exploration 2D (Python / Pygame), pixel art chibi généré par code.
Direction artistique : Dishonored (ville baleinière, brume, Outsider, Void) × Final Fantasy (menus à fenêtres bleues, chibi, formation de combat).

## Lancer
```
python installateur.py      # installe pygame
python honored_fantasy.py
```

## Commandes
| Action | Touches |
|---|---|
| Déplacer | ZQSD / WASD / flèches (Maj = courir) |
| Valider / parler / ouvrir | Entrée, Espace ou E |
| Retour | Échap, Retour arrière, X |
| Menu (équipe, objets, équipement, sauvegarde) | Tab ou M |
| Pouvoirs de l'Outsider (exploration) | P ou C |
| Plein écran | F11 |

La souris fonctionne dans les menus et pour cibler en combat.

## Le jeu
- Groupe de 4 entièrement libre : pour chaque emplacement, un nom au choix (12 caractères) et n'importe quelle classe parmi Garde Urbain, Officier, Sorcière, Moine, Harponneur. Les doublons de classe sont permis (ex. 4 Sorcières).
- 6 zones : Port-Brume, Forêt de Grisvoile, Catacombes du Guet (Realme) puis Havre des Éclats, Forêt Inversée, Cathédrale Inversée (Void).
- 6 boss, chacun lâche une Rune Interdite ; vaincre Lord Vaerith scelle la faille.
- Autels de l'Outsider : soin complet + sauvegarde. Sauvegarde : `~/.honored_fantasy/sauvegarde.json`.

## Formules (cahier §8.4) — `classe/formules.py`
- Dégâts physiques = (arme + FOR×3) × (1 − RES/(RES+12)) × variance ; critique ×1,8
- Toucher = 0,85 + (DEX − AGI cible)×0,04 (pistolet : base 0,45, critique garanti) ; l'AGI réduit aussi les critiques
- Dégâts magiques = (base + INT×3), ignorent la moitié de la RES ; Blink = brut garanti
- Coût de sort = base × (1 − INT×0,03), plancher 40 %
- Fuite = 0,5 × (AGI + 2)/(AGI ennemie moyenne + 2) + bonus de classe, bornée 10–95 %
- Défendre : RES ×2,5 (+150 %), ×3 pour le Garde Urbain (+200 %)

## Architecture
Arborescence du cahier respectée (aucun nouveau dossier). Fichiers ajoutés *dans* les dossiers existants :
- `assets/pixelart.py`, `assets/audio.py` : art et sons procéduraux (aucun fichier externe)
- `classe/formules.py` ; `classe/<nom>.py` : un fichier par classe
- `combat/` : `combat_tour_par_tour.py` (moteur), `actions.py`, `combattant.py`, `pv.py`, `mana.py`, `rang.py`, `scene_combat.py`
- `bot/` : `cible.py`, `degats.py`, `etat.py` (état global + sauvegarde), `position.py`, 4 `ia_*.py`, `bestiaire.py`, `boss.py` (boss 1 à 6), `equipe.py`
- `exploration/` : `exploration.py` (scène), `objets.py` (catalogue 6 raretés + sac)
- `map/moteur.py` (générateurs + rendu par lots) ; chaque zone : `batch.py`, `elements.py`, `loot.py`, `map.py`
- `HUD/ecrans.py` : titre, équipe, pause, boutique, fin

## Pouvoirs de l'Outsider (Sorcière et Harponneur uniquement)
Débloqués par niveau (menu Équipe, Entrée sur un héros : détail et prochain déblocage).

- **Corvo** : Clignement (Blink), Vision des ténèbres, Possession (Monstres puis humains), Pli temporel (ralentit ; Stop Time l'arrête), Nuée vorace, Rafale.
- **DLC Daud** : Clignement du Tueur, Regard du Vide, Invocation d'assassin, Attraction, Lien arcanique.
- **Dishonored 2 (Emily)** : Longue portée, Domino, Envoûtement, Marche d'ombre, Sosie.
- **Passifs** : Agilité (AGI +2), Vitalité (PV max +15 %), Soif de sang (vol de vie), Meurtrier de l'ombre (+15 % dégâts sur cibles affaiblies, +5 % critique).

Utilisables aussi en exploration (touche P) : Clignement (4 cases), Longue portée (8 cases), Vision des ténèbres (voir à travers les murs),
Regard du Vide (détecte Runes et coffres), Attraction (ramasse les objets proches), Marche d'ombre (rencontres rares).

## Queue de Phénix
Réanime un allié KO avec 50 % de ses PV (en combat et dans le menu Objets). Rare : coffres, boss et boutiques des villes prospères.
