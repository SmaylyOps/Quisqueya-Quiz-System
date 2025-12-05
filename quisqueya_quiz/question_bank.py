# question_bank.py
import json
import os
import glob
import random
from typing import List, Optional
from models import Question

class QuestionBank:
    def __init__(self, folder: str = "questions"):
        """
        Charge toutes les questions JSON du dossier fourni (ou questions.json unique).
        Chaque fichier doit contenir une liste d'objets question.
        """
        self.questions: List[Question] = []
        self.folder = folder
        self._load_questions()

    def _load_questions(self):
        # Priorité : dossier 'questions' contenant fichiers json
        if os.path.isdir(self.folder):
            pattern = os.path.join(self.folder, "*.json")
            files = glob.glob(pattern)
            for f in files:
                self._load_file(f)
        # fallback : single file 'questions.json'
        elif os.path.isfile("questions.json"):
            self._load_file("questions.json")

    def _load_file(self, path: str):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                # validation minimale
                if {"id","theme","niveau","texte","options","bonne_option"} <= set(item.keys()):
                    q = Question(
                        id=int(item["id"]),
                        theme=str(item["theme"]),
                        niveau=str(item["niveau"]),
                        texte=str(item["texte"]),
                        options=list(item["options"]),
                        bonne_option=int(item["bonne_option"])
                    )
                    self.questions.append(q)
        except Exception as e:
            print(f"[Warning] impossible de lire {path}: {e}")

    def list_themes(self) -> List[str]:
        themes = sorted({q.theme for q in self.questions})
        return themes

    def filter(self, themes: Optional[List[str]] = None, niveaux: Optional[List[str]] = None) -> List[Question]:
        res = self.questions
        if themes:
            res = [q for q in res if q.theme in themes]
        if niveaux:
            res = [q for q in res if q.niveau in niveaux]
        return res

    def sample_questions(self, count: int = 10, themes: Optional[List[str]] = None, niveaux: Optional[List[str]] = None, balanced: bool = False) -> List[Question]:
        """
        Retourne une liste de questions aléatoires selon critères.
        Si balanced True et niveaux None -> tente une répartition 4 fac /4 moy /2 diff si possible.
        """
        pool = self.filter(themes, niveaux)
        if not pool:
            return []

        if balanced and not niveaux:
            # try to pick 4 fac, 4 moy, 2 diff
            by_level = {lvl: [q for q in pool if q.niveau.lower() == lvl.lower()] for lvl in ("Facile","Moyen","Difficile")}
            picks = []
            want = {"Facile":4, "Moyen":4, "Difficile":2}
            for lvl, n in want.items():
                candidates = by_level.get(lvl, [])
                if len(candidates) >= n:
                    picks += random.sample(candidates, n)
                else:
                    picks += candidates[:]  # take all available
            # if less than requested, fill from remaining
            if len(picks) < count:
                remaining = [q for q in pool if q not in picks]
                need = count - len(picks)
                if remaining:
                    picks += random.sample(remaining, min(need, len(remaining)))
            random.shuffle(picks)
            return picks[:count]

        # general case
        if len(pool) <= count:
            random.shuffle(pool)
            return pool[:count]
        return random.sample(pool, count)
