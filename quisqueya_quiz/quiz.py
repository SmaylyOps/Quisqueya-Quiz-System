# quiz.py
import time
import threading
from typing import List, Optional
from models import Question
from storage import Storage
from datetime import datetime

def input_with_timeout(prompt: str, timeout: Optional[float]) -> Optional[str]:
    """
    Lit l'input avec timeout en lançant input() dans un thread.
    Retourne la chaîne, ou None si timeout atteint.
    Limitation : le thread bloqué sur input() n'est pas tuable, il reste jusqu'à ce que l'utilisateur tape.
    """
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
        self.start_time = None
        self.end_time = None

    def ask_question(self, q: Question, index: int, total: int):
        print("\n" + q.format_for_display(index, total))
        prompt = "Ta réponse (nombre) : "
        ans = None
        if self.timer_per_question and self.timer_per_question > 0:
            print(f"(Tu as {self.timer_per_question} secondes pour répondre)")
            ans = input_with_timeout(prompt, self.timer_per_question)
            if ans is None:
                print("Temps écoulé ! Question comptée comme non répondue.")
                self.mauvaises += 1
                return
        else:
            ans = input(prompt)
        # validate
        try:
            choice = int(ans.strip()) - 1
        except Exception:
            print("Réponse invalide — considérée comme incorrecte.")
            self.mauvaises += 1
            return
        if choice == q.bonne_option:
            print("Bonne réponse !")
            self.bonnes += 1
            # scoring simple : 1 point / bonne réponse
            self.score += 1
        else:
            print(f"Mauvaise réponse. La bonne était: {q.options[q.bonne_option]}")
            self.mauvaises += 1

    def play(self):
        self.start_time = datetime.utcnow().isoformat()
        total = len(self.questions)
        print(f"\nDébut de la partie — joueur : {self.player_name} — {total} questions")
        for i, q in enumerate(self.questions, start=1):
            self.ask_question(q, i, total)
        self.end_time = datetime.utcnow().isoformat()
        duration_seconds = None  # you could compute elapsed if you used time.time timestamps
        print("\n=== Résumé ===")
        print(f"Joueur : {self.player_name}")
        print(f"Bonnes réponses : {self.bonnes}/{total}")
        print(f"Score total : {self.score}")
        # Save score
        entry = {
            "id_partie": f"{self.player_name}_{int(time.time())}",
            "joueur_nom": self.player_name,
            "date_heure": datetime.utcnow().isoformat(),
            "theme": self.questions[0].theme if len(set(q.theme for q in self.questions)) == 1 else "mix",
            "niveau": "mix" if len(set(q.niveau for q in self.questions)) > 1 else self.questions[0].niveau,
            "nombre_questions": total,
            "bonnes": self.bonnes,
            "mauvaises": self.mauvaises,
            "score_total": self.score
        }
        self.storage.save_score(entry)
        print("Score enregistré.")
        return entry
