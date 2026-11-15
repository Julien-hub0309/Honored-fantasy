"""PNJ neutres : dialogues, commerce, quêtes. (Les PNJ hostiles sont les ennemis des rencontres de ville.)"""
from HUD.hud import Dialogue


class PNJ:
    def __init__(self, nom, sprite, role, lignes, x, y):
        self.nom, self.sprite, self.role, self.lignes = nom, sprite, role, lignes
        self.x, self.y = x, y
        self.dir = "bas"

    def dialoguer(self, flags=None):
        """Retourne un Dialogue. Certaines répliques changent selon l'avancement (flags)."""
        out = []
        for l in self.lignes:
            nom, _, txt = l.partition(" : ")
            out.append((nom if txt else self.nom, txt or l))
        if flags and flags.get("boss_vaincus", 0) >= 3 and self.role == "dialogue" and self.nom == "Capitaine Roke":
            out = [("Roke", "Vous avez terrassé l'Abbesse ? Les condamnés valent donc mieux que les saints... Allez, le Void vous attend.")]
        return Dialogue(out)

    def regarder(self, vers):
        dx, dy = vers[0] - self.x, vers[1] - self.y
        self.dir = ("droite" if dx > 0 else "gauche") if abs(dx) > abs(dy) else ("bas" if dy > 0 else "haut")
