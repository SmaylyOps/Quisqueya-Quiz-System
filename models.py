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
        header = f"Question {index}/{total} — {self.theme} ({self.niveau})"
        lines = [header, "-" * len(header), self.texte]
        for i, opt in enumerate(self.options):
            lines.append(f"  {i+1}) {opt}")
        return "\n".join(lines)
