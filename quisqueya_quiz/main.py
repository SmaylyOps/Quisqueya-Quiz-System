# main.py
from utils import clear
import time
from question_bank import QuestionBank
from storage import Storage
from quiz import QuizGame
from datetime import datetime

def welcome_and_countdown(seconds: int = 10):
    clear()
    print("Bienvenue dans Quisqueya Système Quiz !")
    print("Veux-tu accéder au Menu Principal maintenant ? Appuie sur Entrée pour sauter ou attends le compte à rebours.")
    # start a thread to read Enter key while counting down in main thread
    import threading, sys
    skip = {"pressed": False}
    def wait_enter():
        try:
            input()
            skip["pressed"] = True
        except:
            pass
    t = threading.Thread(target=wait_enter, daemon=True)
    t.start()
    for i in range(seconds, 0, -1):
        if skip["pressed"]:
            break
        print(f"Menu principal dans {i}...", end="\r")
        time.sleep(1)
    print("\n" + ("Accès immédiat demandé." if skip["pressed"] else "Affichage du menu."))

def choose_from_menu(options):
    for idx, opt in enumerate(options, start=1):
        print(f"{idx}) {opt}")
    while True:
        try:
            choice = int(input("Choix: ").strip())
            if 1 <= choice <= len(options):
                return choice
        except Exception:
            pass
        print("Choix invalide, réessaie.")

def main():
    qb = QuestionBank(folder="questions")  # place your theme files into ./questions/
    storage = Storage()
    # fallback: if no questions loaded, try /mnt/data path (if running from the environment used earlier)
    if not qb.questions:
        import os
        alt = "/mnt/data/quisqueya_questions_by_theme"
        if os.path.isdir(alt):
            qb = QuestionBank(folder=alt)

    welcome_and_countdown(10)

    while True:
        clear()
        print("\n=== Menu Principal ===")
        options = ["Jouer", "Classement / Scores", "Ajouter une question (simple)", "Instructions / Aide", "Quitter"]
        choice = choose_from_menu(options)

        if choice == 1:  # Jouer
            clear()
            print("\nModes :")
            mode = choose_from_menu(["Mode rapide (10 questions aléatoires)", "Mode personnalisé"])
            if mode == 1:
                count = 10
                # choose theme
                themes = qb.list_themes()
                print("Choisis un thème ou 0 pour Tous:")
                for i, t in enumerate(themes, start=1):
                    print(f"{i}) {t}")
                print("0) Tous")
                sel = input("Ton choix (numéro ou 0): ").strip()
                themes_sel = None
                try:
                    n = int(sel)
                    if n == 0:
                        themes_sel = None
                    elif 1 <= n <= len(themes):
                        themes_sel = [themes[n-1]]
                except:
                    themes_sel = None
                player = input("Entrez ton nom (ou pseudo) : ").strip() or "Joueur"
                # ask for timer per question?
                use_timer = input("Activer minuterie par question ? (O/N) : ").strip().lower().startswith("o")
                timer_val = None
                if use_timer:
                    try:
                        timer_val = int(input("Durée par question (secondes), ex 15 : ").strip())
                    except:
                        timer_val = 15
                qlist = qb.sample_questions(count=count, themes=themes_sel)
                if not qlist:
                    print("Aucune question disponible pour les critères choisis.")
                    continue
                game = QuizGame(qlist, player, storage, timer_per_question=timer_val)
                game.play()

            else:
                # Mode personnalisé
                try:
                    count = int(input("Nombre de questions (ex 5-20) : ").strip())
                except:
                    count = 10
                # choose themes (multiple allowed)
                themes = qb.list_themes()
                if not themes:
                    print("Aucune question chargée.")
                    continue
                print("Thèmes disponibles (sépare par virgule, ou 0 pour Tous) :")
                for i, t in enumerate(themes, start=1):
                    print(f"{i}) {t}")
                sel = input("Ex : 1,3  ou 0 pour Tous : ").strip()
                themes_sel = None
                if sel != "0":
                    try:
                        idxs = [int(x.strip()) for x in sel.split(",") if x.strip()]
                        themes_sel = [themes[i-1] for i in idxs if 1 <= i <= len(themes)]
                    except:
                        themes_sel = None
                # niveaux?
                use_balanced = input("Souhaites-tu une répartition équilibrée par niveau (4/4/2) si possible ? (O/N) : ").strip().lower().startswith("o")
                player = input("Entrez ton nom (ou pseudo) : ").strip() or "Joueur"
                use_timer = input("Activer minuterie par question ? (O/N) : ").strip().lower().startswith("o")
                timer_val = None
                if use_timer:
                    try:
                        timer_val = int(input("Durée par question (secondes), ex 15 : ").strip())
                    except:
                        timer_val = 15
                qlist = qb.sample_questions(count=count, themes=themes_sel, balanced=use_balanced)
                if not qlist:
                    print("Aucune question disponible pour les critères choisis.")
                    continue
                game = QuizGame(qlist, player, storage, timer_per_question=timer_val)
                game.play()

        elif choice == 2:  # Classement
            n = input("Afficher top N (par défaut 10) : ").strip()
            try:
                n = int(n)
            except:
                n = 10
            theme_filter = input("Filtrer par thème ? (nom du thème ou vide pour tous) : ").strip() or None
            top = storage.top_n(n, theme_filter)
            if not top:
                print("Aucun score enregistré.")
            else:
                print(f"\nTop {len(top)}")
                for i, s in enumerate(top, start=1):
                    print(f"{i}) {s['joueur_nom']} — score {s.get('score_total')} — {s.get('bonnes')}/{s.get('nombre_questions')} — {s.get('date_heure')} — theme: {s.get('theme')}")

        elif choice == 3:  # Ajouter question simple
            print("\nAjouter une question (sera ajoutée au fichier questions_custom.json)")
            theme = input("Thème: ").strip() or "Culture générale"
            niveau = input("Niveau (Facile/Moyen/Difficile) : ").strip() or "Facile"
            texte = input("Texte de la question : ").strip()
            opts = []
            for i in range(4):
                o = input(f"Option {i+1} : ").strip()
                if not o:
                    o = f"Option {i+1}"
                opts.append(o)
            try:
                bonne = int(input("Index de la bonne option (1-4) : ").strip()) - 1
            except:
                bonne = 0
            # append to a custom file
            import json, os
            path = os.path.join("questions", "questions_custom.json")
            os.makedirs("questions", exist_ok=True)
            entry = {
                "id": int(time.time()),
                "theme": theme,
                "niveau": niveau,
                "texte": texte,
                "options": opts,
                "bonne_option": bonne
            }
            if os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        arr = json.load(f)
                except:
                    arr = []
            else:
                arr = []
            arr.append(entry)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(arr, f, ensure_ascii=False, indent=2)
            print("Question ajoutée (questions/questions_custom.json). Relance l'application pour recharger.")

        elif choice == 4:  # Instructions
            print("""
Règles :
- Une partie contient N questions (10 par défaut).
- Chaque bonne réponse = 1 point.
- Minuterie par question : si activée, la question est comptée comme non répondue si le temps expire.
- Les scores sont sauvegardés dans scores.json avec timestamp UTC.
- Tu peux filtrer le classement par thème.
            """)

        elif choice == 5:  # Quitter
            sure = input("Es-tu sûr de vouloir quitter ? (O/N) : ").strip().lower().startswith("o")
            if sure:
                print("Au revoir !")
                break

if __name__ == "__main__":
    main()
