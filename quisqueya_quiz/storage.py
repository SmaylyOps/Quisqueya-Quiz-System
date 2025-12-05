# storage.py
import json
from datetime import datetime
from typing import Dict, Any, List
import os

SCORES_FILE = "scores.json"

class Storage:
    def __init__(self, path: str = SCORES_FILE):
        self.path = path
        # create file if not exists
        if not os.path.isfile(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def save_score(self, entry: Dict[str, Any]):
        all_scores = self.load_all()
        all_scores.append(entry)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(all_scores, f, ensure_ascii=False, indent=2)

    def load_all(self) -> List[Dict[str, Any]]:
        with open(self.path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []

    def top_n(self, n: int = 10, theme: str = None) -> List[Dict[str, Any]]:
        all_scores = self.load_all()
        if theme:
            all_scores = [s for s in all_scores if s.get("theme") == theme]
        # sort by score_total desc, then time asc
        def keyfn(s):
            return (-s.get("score_total", 0), s.get("date_heure", ""))
        all_scores.sort(key=keyfn)
        return all_scores[:n]
