"""Gestionnaire de la boucle de combat et de l'ordre des tours (moteur pur, sans affichage).

Un tour = [phase d'objet OPTIONNELLE] puis [action principale OBLIGATOIRE : attaquer / magie / défendre / fuir].
Le moteur renvoie des *événements* (dicts) que la scène (scene_combat.py) anime ; l'état est mis à jour immédiatement.
"""
import random

from combat import actions as A
from combat.combattant import Combattant, STATS
from combat.rang import Alteration
from objet import ev


class Combat:
    def __init__(self, allies, ennemis, sac=None, boss=False, rng=None, fuite_possible=None):
        self.allies = allies
        self.ennemis = ennemis
        self.renforts = []                               # alliés invoqués (assassin, sosie) : n'empêchent pas la défaite
        self.sac = sac if sac is not None else []        # inventaire des alliés (liste partagée avec la sauvegarde)
        self.boss = boss
        self.fuite_possible = (not boss) if fuite_possible is None else fuite_possible
        self.rng = rng or random.Random()
        self.round = 0
        self.file = []
        self.temps_fige = None
        self.etat = "en_cours"      # en_cours | victoire | defaite | fuite

    # ---------------------------------------------------------------- utilitaires
    def vivants(self, camp):
        return [c for c in camp if c.vivant]

    def camp(self, acteur):
        return self.allies + self.renforts if acteur.allie else self.ennemis

    def adversaires(self, acteur):
        """Cibles ennemies de l'acteur. Un acteur possédé attaque son propre camp ; les furtifs ne sont pas ciblés."""
        if acteur.rang.a("possede"):
            autres = [c for c in self.camp(acteur) if c.vivant and c is not acteur]
            if autres:
                return autres
        adv = self.vivants(self.ennemis if acteur.allie else self.allies + self.renforts)
        return [c for c in adv if not c.rang.a("furtif")] or adv

    def amis(self, acteur):
        return self.vivants(self.camp(acteur))

    def cibles_par_defaut(self, acteur, sort):
        if sort.cible in ("allie", "allies"):
            return self.amis(acteur)
        if sort.cible == "soi":
            return [acteur]
        adv = self.adversaires(acteur)
        if sort.cible == "ennemis":
            return adv
        return adv[:2] if sort.cible == "deux_ennemis" else adv[:1]

    def consommer(self, acteur, objet):
        liste = self.sac if acteur.allie else acteur.inventaire
        for i, o in enumerate(liste):
            if o is objet or o.id == objet.id:
                liste.pop(i)
                return

    # ---------------------------------------------------------------- invocations
    def invoquer(self, acteur, modele):
        """Crée un allié temporaire (4 tours), piloté par l'IA. Retourne None s'il y en a déjà 2."""
        if len([r for r in self.renforts if r.vivant]) >= 2:
            return None
        import classe as registre
        from bot import ia_agressive_melee
        if modele == "assassin":
            cl = registre.obtenir("harponneur")
            st = cl.stats(max(1, acteur.niveau))
            st["PV"], st["Mana"] = int(st["PV"] * 0.55), 0
            st["FOR"] += 3; st["DEX"] += 4; st["AGI"] += 2
            r = Combattant("Assassin", "harponneur", acteur.niveau, st, True, arme_base=cl.arme["degats_base"] + 8, sorts=[])
            r.tint = (120, 120, 160)
        else:   # sosie : copie spectrale de l'invocateur
            st = {k: acteur.base[k] for k in STATS}
            st["PV"], st["Mana"] = max(1, acteur.pv.maximum // 2), 0
            r = Combattant(f"Sosie de {acteur.nom}"[:22], acteur.classe.id, acteur.niveau, st, True, arme_base=acteur.arme_base, sorts=[])
            r.sprite, r.espece, r.tint = acteur.sprite, acteur.espece, (170, 170, 255)
        r.auto = True
        r.ia = ia_agressive_melee.decider
        r.rang.ajouter(Alteration("invoque", "Invoqué", 4))
        self.renforts.append(r)
        return r

    # ---------------------------------------------------------------- dégâts
    def _mourir(self, c):
        c.rang.vider()
        if c.lien is not None:
            c.lien.lien, c.lien.lien_duree = None, 0
            c.lien, c.lien_duree = None, 0
        if self.temps_fige and self.temps_fige["lanceur"] is c:
            self.temps_fige = None

    def infliger(self, source, cible, n, nature="phys", crit=False, propage=False):
        """Applique des dégâts (passifs, réduction, réplication Domino, mort liée). `source` peut être None (dégâts sur la durée)."""
        if not cible.vivant:
            return []
        if source is not None and not propage:
            if source.rang.a("furtif") and nature in ("phys", "brut"):       # assassinat : +50 % puis on est repéré
                n = int(n * 1.5)
                source.rang.retirer("furtif")
            if source.a_passif("meurtrier_ombre") and (cible.lien is not None or cible.rang.malus() or self.temps_fige):
                n = int(n * 1.15)
        if nature != "brut":
            n = max(1, int(round(n * (1 - cible.classe.reduction_passive))))
        reel = cible.pv.perdre(n)
        e = [ev("degats", cible=cible, n=reel, crit=crit, nature=nature, source=source)]
        partenaire = cible.lien
        if not cible.vivant:
            e.append(ev("mort", cible=cible))
        elif reel > 0 and cible.rang.a("hypnotise"):                         # l'hypnose se brise sous les coups
            cible.rang.retirer("hypnotise")
        if source is not None and not propage and source.vivant and source.a_passif("soif_de_sang"):
            gain = max(1, int(reel * 0.06)) + (int(source.pv.maximum * 0.12) if not cible.vivant else 0)
            g = source.pv.gagner(gain)
            if g:
                e.append(ev("soin", cible=source, n=g, stat="PV"))
        if partenaire is not None and partenaire.vivant and not propage:
            e += self.infliger(source, partenaire, reel, "brut", False, propage=True)
            if not cible.vivant and partenaire.vivant and not partenaire.boss:   # mort liée (les boss y résistent)
                partenaire.pv.perdre(partenaire.pv.valeur)
                e.append(ev("mort", cible=partenaire))
            if not partenaire.vivant and cible.vivant and not cible.boss:
                cible.pv.perdre(cible.pv.valeur)
                e.append(ev("mort", cible=cible))
        for c in (cible, partenaire):
            if c is not None and not c.vivant:
                self._mourir(c)
        return e

    # ---------------------------------------------------------------- rounds & tours
    def nouveau_round(self):
        self.round += 1
        vivants = [c for c in self.allies + self.renforts + self.ennemis if c.vivant]
        self.file = sorted(vivants, key=lambda c: c.stat("AGI") + self.rng.uniform(0, 4), reverse=True)

    def suivant(self):
        """Prochain acteur (ou None si le combat est terminé) + événements intermédiaires (figés...)."""
        e = []
        while self.verifier_fin() == "en_cours":
            if not self.file:
                self.nouveau_round()
            while self.file:
                a = self.file.pop(0)
                if not a.vivant:
                    continue
                tf = self.temps_fige
                if tf and a is not tf["lanceur"] and not (a.boss and tf["restant"] < 2):
                    e.append(ev("fige", cible=a))
                    continue
                if a.rang.a("etourdi") or a.rang.a("hypnotise"):      # tour perdu
                    a.rang.tick()
                    e.append(ev("fige", cible=a))
                    continue
                self.debut_tour(a, e)
                return a, e
        return None, e

    def debut_tour(self, a, e):
        a.en_defense = False
        a.objet_utilise = False
        for k in list(a.cd):
            a.cd[k] = max(0, a.cd[k] - 1)
        if a.classe.regen_pv and a.vivant:
            n = a.pv.gagner(int(a.pv.maximum * a.classe.regen_pv))
            if n:
                e.append(ev("soin", cible=a, n=n, stat="PV"))

    def fin_tour(self, a):
        e = []
        for alt in list(a.rang.liste):                      # dégâts sur la durée (nuée vorace)
            if alt.dot and a.vivant:
                e += self.infliger(None, a, alt.dot, "brut")
        if a.vivant:
            for alt in a.rang.tick():
                if alt.id == "invoque":                      # l'invocation s'évanouit
                    a.pv.perdre(a.pv.valeur)
                    e.append(ev("mort", cible=a))
                    self._mourir(a)
                    break
                e.append(ev("statut", cible=a, texte=f"{alt.nom} se dissipe", positif=False, discret=True))
            if a.vivant and a.lien_duree > 0:
                a.lien_duree -= 1
                if a.lien_duree <= 0 and a.lien is not None:
                    a.lien.lien, a.lien.lien_duree = None, 0
                    a.lien = None
                    e.append(ev("statut", cible=a, texte="Domino se brise", positif=False, discret=True))
        tf = self.temps_fige
        if tf and tf["lanceur"] is a:
            if tf["ce_tour"]:
                tf["ce_tour"] = False
            else:
                tf["restant"] -= 1
                if tf["restant"] <= 0:
                    self.temps_fige = None
                    e.append(ev("texte", texte="Le temps reprend son cours."))
        return e

    def utiliser_objet(self, acteur, objet, cible):
        if acteur.objet_utilise:
            return []
        return A.utiliser(self, acteur, objet, cible)

    def executer(self, acteur, action):
        """Exécute l'action principale, termine le tour et vérifie la fin du combat."""
        t = action["type"]
        if t == "attaquer":
            e = A.attaquer(self, acteur, action["arme"], action.get("cible"))
        elif t == "magie":
            e = A.lancer(self, acteur, action["sort"], action.get("cibles"))
        elif t == "defendre":
            e = A.defendre(self, acteur)
        elif t == "fuir":
            e = A.fuir(self, acteur)
        elif t == "special":            # attaque signature d'un boss : fonction(combat, acteur) -> événements
            e = action["fn"](self, acteur)
        else:
            e = []
        e += self.fin_tour(acteur)
        self.verifier_fin()
        return e

    def verifier_fin(self):
        if self.etat in ("victoire", "defaite", "fuite"):
            return self.etat
        if not self.vivants(self.ennemis):
            self.etat = "victoire"
        elif not self.vivants(self.allies):
            self.etat = "defaite"
        return self.etat

    def recompenses(self):
        xp = sum(c.xp for c in self.ennemis)
        gold = sum(c.gain_or for c in self.ennemis)
        butin = [o for c in self.ennemis for o in c.butin]
        return xp, gold, butin
