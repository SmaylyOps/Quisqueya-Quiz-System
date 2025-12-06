# quiz.py
import time
import threading
from typing import List, Optional
from models import Question
from storage import Storage
from datetime import datetime

def input_with_timeout(prompt: str, timeout: Optional[float]) -> Optional[str]:
    """
    Lit un input avec timeout en utilisant un thread.
    Limitation : si timeout atteint, le thread input reste bloqué en arrière-plan.
    Retourne None si timeout atteint, sinon la chaîne entrée.
    """
    if timeout is None or timeout <= 0:
        try:
            return input(prompt)
        except (KeyboardInterrupt, EOFError):
            return ""
    result = {"answer": None}
    def target():
        try:
            result["answer"] = input(prompt)
        except Exception:
            result["answer"] = None

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        # Timeout
        return None
    return result["answer"]

class QuizGame:
    def __init__(self, questions: List[Question], player_name: str, storage: Storage, timer_per_question: Optional[int] = None):
        self.questions = questions
        self.player_name = player_name
        self.storage = storage
        self.timer_per_question = timer_per_question
        self.score = 0
        self.bonnes = 0
        self.mauvaises = 0
        self.start_ts = None
        self.end_ts = None

    def ask_question(self, q: Question, index: int, total: int):
        from utils import clear, safe_input
        clear()
        print(q.format_for_display(index, total))
        prompt = "Ta réponse (nombre) : "
        ans = None
        if self.timer_per_question and self.timer_per_question > 0:
            print(f"(Tu as {self.timer_per_question} secondes pour répondre)")
            ans = input_with_timeout(prompt, self.timer_per_question)
            if ans is None:
                print("Temps écoulé ! Question considérée comme non répondue / incorrecte.")
                self.mauvaises += 1
                time.sleep(1.2)
                return
        else:
            ans = safe_input(prompt)
        try:
            choice = int(ans.strip()) - 1
        except Exception:
            print("Réponse invalide — considérée comme incorrecte.")
            self.mauvaises += 1
            time.sleep(1.2)
            return
        if choice == q.bonne_option:
            print("Bonne réponse !")
            self.bonnes += 1
            self.score += 1
        else:
            # protect against index error
            correct = q.options[q.bonne_option] if 0 <= q.bonne_option < len(q.options) else "Inconnue"
            print(f"Mauvaise réponse. La bonne était: {correct}")
            self.mauvaises += 1
        time.sleep(1.1)

    def play(self):
        from utils import clear
        self.start_ts = time.time()
        total = len(self.questions)
        clear()
        print(f"Début de la partie — joueur : {self.player_name} — {total} questions")
        time.sleep(0.8)
        for i, q in enumerate(self.questions, start=1):
            self.ask_question(q, i, total)
        self.end_ts = time.time()
        duration = int(self.end_ts - self.start_ts) if self.start_ts else 0
        # pourcentage de bonnes réponses
        pourcentage = round((self.bonnes / total) * 100, 1) if total > 0 else 0.0
        clear()
        print("=== Résumé de la partie ===")
        print(f"Joueur : {self.player_name}")
        print(f"Bonnes réponses : {self.bonnes}/{total} ({pourcentage}%)")
        print(f"Mauvaises réponses : {self.mauvaises}/{total}")
        print(f"Score total : {self.score}")
        print(f"Durée : {duration} s")
        # sauvegarde
        entry = {
            "id_partie": f"{self.player_name}_{int(time.time())}",
            "joueur_nom": self.player_name,
            "date_heure": datetime.utcnow().isoformat(),
            "theme": self.questions[0].theme if len(set(q.theme for q in self.questions)) == 1 else "mix",
            "niveau": self.questions[0].niveau if len(set(q.niveau for q in self.questions)) == 1 else "mix",
            "nombre_questions": total,
            "bonnes": self.bonnes,
            "mauvaises": self.mauvaises,
            "score_total": self.score,
            "pourcentage": pourcentage,
            "duree_seconds": duration
        }
        try:
            self.storage.save_score(entry)
            print("Score enregistré.")
        except Exception as e:
            print(f"[Error] impossible de sauvegarder le score: {e}")
        input("Appuie sur Entrée pour revenir au menu principal...")
        return entry
