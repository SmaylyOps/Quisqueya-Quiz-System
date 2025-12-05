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
        """Retourne un texte à afficher pour la question."""
        lines = []
        header = f"Question {index}/{total} — {self.theme} ({self.niveau})"
        lines.append(header)
        lines.append(self.texte)
        for i, opt in enumerate(self.options):
            lines.append(f"  {i+1}) {opt}")
        return "\n".join(lines)
