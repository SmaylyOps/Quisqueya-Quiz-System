# models.py
from dataclasses import dataclass
from typing import List

@dataclass
class Question:
    id: int
    theme: str
    niveau: str
    texte: str
    options: List[str]
    bonne_option: int

    def format_for_display(self, index: int, total: int) -> str:
        """
        Retourne une chaîne formatée pour affichage
        """
        s = f"Question {index}/{total} [{self.theme} - {self.niveau}]\n"
        s += f"{self.texte}\n"
        for i, opt in enumerate(self.options, start=1):
            s += f"  {i}) {opt}\n"
        return s
