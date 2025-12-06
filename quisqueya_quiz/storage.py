# storage.py
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

SCORES_FILE = "scores.json"

class Storage:
    def __init__(self, path: str = SCORES_FILE):
        self.path = path
        if not os.path.isfile(self.path):
            try:
                with open(self.path, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[Error] impossible de créer {self.path}: {e}")

    def load_all(self) -> List[Dict[str, Any]]:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_score(self, entry: Dict[str, Any]):
        all_scores = self.load_all()
        all_scores.append(entry)
        # write atomically: write to temp then rename
        tmp = f"{self.path}.tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(all_scores, f, ensure_ascii=False, indent=2)
            os.replace(tmp, self.path)
        except Exception as e:
            print(f"[Error] impossible de sauvegarder le score: {e}")

    def top_n(self, n: int = 10, theme: Optional[str] = None) -> List[Dict[str, Any]]:
        all_scores = self.load_all()
        if theme:
            all_scores = [s for s in all_scores if s.get("theme") == theme]
        # sort primarily by score_total desc, secondarily by pourcentage desc then date
        def keyfn(s):
            return (-s.get("score_total", 0), -s.get("pourcentage", 0), s.get("date_heure", ""))
        all_scores.sort(key=keyfn)
        return all_scores[:n]
