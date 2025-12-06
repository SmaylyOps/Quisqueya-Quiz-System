# question_bank.py
import json
import glob
import os
import random
from typing import List, Optional
from models import Question

class QuestionBank:
    def __init__(self, folder: str = "questions"):
        """
        Charge les questions depuis tous les fichiers JSON du dossier donné,
        ou depuis 'questions.json' s'il existe.
        """
        self.questions: List[Question] = []
        self.folder = folder
        self._load_questions()

    def _load_questions(self):
        # Si dossier existe, charge tous les json dedans
        if os.path.isdir(self.folder):
            pattern = os.path.join(self.folder, "*.json")
            files = sorted(glob.glob(pattern))
            for f in files:
                self._load_file(f)
        # Fallback: fichier unique questions.json dans le répertoire courant
        elif os.path.isfile("questions.json"):
            self._load_file("questions.json")

    def _load_file(self, path: str):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                print(f"[Warning] {path} ne contient pas une liste de questions — ignoré.")
                return
            for item in data:
                if not all(k in item for k in ("id","theme","niveau","texte","options","bonne_option")):
                    # ignore malformed entries but continue
                    print(f"[Warning] entrée mal formée dans {path}, id approximatif: {item.get('id')}")
                    continue
                try:
                    q = Question(
                        id=int(item["id"]),
                        theme=str(item["theme"]),
                        niveau=str(item["niveau"]),
                        texte=str(item["texte"]),
                        options=list(item["options"]),
                        bonne_option=int(item["bonne_option"])
                    )
                    # Basic validation
                    if not (0 <= q.bonne_option < len(q.options)):
                        print(f"[Warning] mauvaise bonne_option pour id {q.id} dans {path} — ignorée.")
                        continue
                    self.questions.append(q)
                except Exception as e:
                    print(f"[Warning] impossible de créer Question depuis entrée {item.get('id')}: {e}")
        except Exception as e:
            print(f"[Warning] impossible de lire {path}: {e}")

    def list_themes(self) -> List[str]:
        return sorted({q.theme for q in self.questions})

    def filter(self, themes: Optional[List[str]] = None, niveaux: Optional[List[str]] = None) -> List[Question]:
        res = self.questions
        if themes:
            res = [q for q in res if q.theme in themes]
        if niveaux:
            res = [q for q in res if q.niveau in niveaux]
        return res

    def sample_questions(self, count: int = 10, themes: Optional[List[str]] = None, niveaux: Optional[List[str]] = None, balanced: bool = False) -> List[Question]:
        """
        Retourne jusqu'à count questions (max 10). Si balanced True et niveaux None,
        tente une répartition 4 Facile / 4 Moyen / 2 Difficile (si possible).
        """
        # impose la limite globale à 10
        count = min(int(count), 10)

        pool = self.filter(themes, niveaux)
        if not pool:
            return []

        if balanced and not niveaux:
            by_level = {
                "Facile": [q for q in pool if q.niveau.lower() == "facile"],
                "Moyen": [q for q in pool if q.niveau.lower() == "moyen"],
                "Difficile": [q for q in pool if q.niveau.lower() == "difficile"],
            }
            picks = []
            want = {"Facile":4, "Moyen":4, "Difficile":2}
            for lvl, n in want.items():
                candidates = by_level.get(lvl, [])
                take = min(n, len(candidates))
                if take > 0:
                    picks += random.sample(candidates, take)
            if len(picks) < count:
                remaining = [q for q in pool if q not in picks]
                if remaining:
                    picks += random.sample(remaining, min(count - len(picks), len(remaining)))
            random.shuffle(picks)
            return picks[:count]

        # général : échantillonnage simple
        if len(pool) <= count:
            random.shuffle(pool)
            return pool[:count]
        return random.sample(pool, count)
