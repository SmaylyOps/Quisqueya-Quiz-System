# main.py - Point d'entrée principal du Quisqueya Système Quiz
# Ce fichier gère l'interface utilisateur et la navigation dans les menus

from question_bank import QuestionBank
from storage import Storage
from quiz import QuizGame
from utils import clear, safe_input, safe_int, choose_from_list
import os
import time
import threading

# -----------------------------
# Fonctions utilitaires
# -----------------------------

def welcome_and_countdown(seconds: int = 10):
    clear()
    print("\n╔" + "═" * 60 + "╗")
    print("║" + " " * 60 + "║")
    print("║" + "    🎓 BIENVENUE DANS QUISQUEYA SYSTÈME QUIZ 🎓    ".center(57) + "║")
    print("║" + " " * 60 + "║")
    print("╚" + "═" * 60 + "╝")
    print("\n📌 Appuyez sur [ENTRÉE] pour accéder immédiatement au menu")
    print("⏱️  Sinon, le menu apparaîtra après le compte à rebours...\n")

    skip = {"pressed": False}
    def wait_enter():
        try:
            input()
            skip["pressed"] = True
        except:
            skip["pressed"] = False

    t = threading.Thread(target=wait_enter, daemon=True)
    t.start()

    for i in range(seconds, 0, -1):
        if skip["pressed"]:
            break
        print(f"⏳ Démarrage dans {i} seconde(s)...".ljust(40), end="\r")
        time.sleep(1)

    clear()


def select_theme_interactive(qb: QuestionBank):
    themes = qb.list_themes()
    if not themes:
        print("❌ Aucun thème disponible pour le moment.")
        input("\n📌 Appuyez sur [ENTRÉE] pour revenir...")
        return None
    print("\n" + "─" * 60)
    print("📚 THÈMES DISPONIBLES".center(60))
    print("─" * 60 + "\n")
    idx = choose_from_list(
        themes,
        prompt="\n➤ Entrez le numéro du thème choisi (ou 0 pour revenir) : ",
        allow_zero_return=True
    )
    if idx is None:
        return None
    return [themes[idx]]


# -----------------------------
# Modes de jeu
# -----------------------------

def play_quick_mode(qb: QuestionBank, storage: Storage):
    clear()
    print("\n" + "═" * 60)
    print("⚡ MODE RAPIDE - 10 QUESTIONS".center(60))
    print("═" * 60 + "\n")
    player = safe_input("👤 Entrez votre nom ou pseudo : ").strip() or "Joueur"
    timer_val = 15
    print(f"\n⏱️  Minuterie activée : {timer_val} secondes par question")
    qlist = qb.sample_questions(count=10, themes=None)
    if not qlist:
        print("\n❌ Aucune question disponible.")
        input("\n📌 Appuyez sur [ENTRÉE] pour revenir...")
        return
    print(f"\n🎮 Démarrage de la partie avec {len(qlist)} questions aléatoires...")
    time.sleep(1)
    game = QuizGame(qlist, player, storage, timer_per_question=timer_val)
    game.play()


def play_theme_mode(qb: QuestionBank, storage: Storage):
    """
    Permet de jouer un quiz sur un thème choisi par l'utilisateur.
    """
    themes = qb.list_themes()
    if not themes:
        print("❌ Aucun thème disponible.")
        input("Appuyez sur [ENTRÉE] pour revenir...")
        return
    print("\nSélection du thème du quiz")
    idx = choose_from_list(themes, prompt="➤ Choisissez un thème : ", allow_zero_return=True)
    if idx is None:
        return
    player = safe_input("👤 Entrez votre nom ou pseudo : ").strip() or "Joueur"
    timer_val = 15
    print(f"\n⏱️  Minuterie activée : {timer_val} secondes par question")
    qlist = qb.sample_questions(count=10, themes=[themes[idx]])
    if not qlist:
        print("❌ Aucune question disponible pour ce thème.")
        input("Appuyez sur [ENTRÉE] pour revenir...")
        return
    game = QuizGame(qlist, player, storage, timer_per_question=timer_val)
    game.play()


def play_custom_mode(qb: QuestionBank, storage: Storage):
    clear()
    print("\n" + "═" * 60)
    print("⚙️  MODE PERSONNALISÉ".center(60))
    print("═" * 60 + "\n")
    while True:
        print("   1) 🎯 Jouer par thème")
        print("   2) 🔧 Mode personnalisé classique (tous thèmes)")
        print("   0) ← Retour\n")
        sub = safe_int("➤ Votre choix : ", min_val=0, max_val=2, default=0)
        if sub == 0:
            break
        elif sub == 1:
            play_theme_mode(qb, storage)
        elif sub == 2:
            player = safe_input("👤 Entrez votre nom ou pseudo : ").strip() or "Joueur"
            timer_val = 15
            qlist = qb.sample_questions(count=10, themes=None, balanced=False)
            if not qlist:
                print("\n❌ Aucune question disponible.")
                input("\n📌 Appuyez sur [ENTRÉE] pour revenir...")
                return
            print("\nConfiguration terminée !")
            print(f"Joueur : {player}, Questions : {len(qlist)}, Minuterie : {timer_val}s")
            input("\nAppuyez sur [ENTRÉE] pour commencer...")
            game = QuizGame(qlist, player, storage, timer_per_question=timer_val)
            game.play()


# -----------------------------
# Leaderboard
# -----------------------------

def show_leaderboard(storage: Storage):
    clear()
    print("\n" + "═" * 60)
    print("🏆 CLASSEMENT DES MEILLEURS SCORES".center(60))
    print("═" * 60 + "\n")
    n = safe_int(
        "📊 Combien de scores voulez-vous voir ? (1-50, défaut: 10) : ",
        min_val=1, max_val=50, default=10
    )
    theme = safe_input("   Filtrer par thème ? (nom exact ou vide pour tous) : ").strip() or None
    top = storage.top_n(n, theme)
    if not top:
        print("\n❌ Aucun score enregistré pour le moment.")
        print("   Jouez une partie pour apparaître dans le classement !")
    else:
        print("\n" + "─" * 60)
        print(f"📚 Thème : {theme}" if theme else "📚 Tous les thèmes")
        print("─" * 60 + "\n")
        for i, s in enumerate(top, start=1):
            pourc_str = f"{s.get('pourcentage','N/A')}%"
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            print(f"{medal} {s.get('joueur_nom')}")
            print(f"   Score : {s.get('score_total')} points")
            print(f"   Réussite : {s.get('bonnes')}/{s.get('nombre_questions')} ({pourc_str})")
            print(f"   Date : {s.get('date_heure')[:10]}")
            print(f"   Thème : {s.get('theme')}\n")
    print("─" * 60)
    input("\n📌 Appuyez sur [ENTRÉE] pour revenir au menu principal...")


# -----------------------------
# Instructions / Aide
# -----------------------------

def instructions():
    clear()
    print("\n" + "═" * 60)
    print("📖 INSTRUCTIONS & AIDE".center(60))
    print("═" * 60 + "\n")
    print("🎮 COMMENT JOUER ?\n")
    print("   • Une partie contient jusqu'à 10 questions")
    print("   • Chaque bonne réponse vaut 1 point")
    print("   • Choisissez votre réponse en tapant le numéro correspondant\n")
    print("⏱️  MINUTERIE\n")
    print("   • Si activée, vous avez un temps limité par question")
    print("   • Pas de réponse avant la fin = réponse incorrecte\n")
    print("🏆 SCORES\n")
    print("   • Vos scores sont sauvegardés automatiquement")
    print("   • Consultez le classement dans le menu principal\n")
    print("📚 MODES DE JEU\n")
    print("   • Mode Rapide : 10 questions, configuration simple")
    print("   • Mode Personnalisé : choisissez tout en détail\n")
    print("⚙️  NAVIGATION\n")
    print("   • Tapez le numéro de l'option souhaitée")
    print("   • '0' permet généralement de revenir en arrière\n")
    print("💡 ASTUCES\n")
    print("   • Lisez bien chaque question avant de répondre")
    print("   • Vos statistiques sont suivies dans le classement\n")
    print("═" * 60)
    input("\n📌 Appuyez sur [ENTRÉE] pour revenir au menu...")


# -----------------------------
# Boucle principale
# -----------------------------

def main():
    qb = QuestionBank(folder="questions")
    if not qb.questions:
        alt = "/mnt/data/quisqueya_questions_by_theme"
        if os.path.isdir(alt):
            qb = QuestionBank(folder=alt)
    storage = Storage()
    welcome_and_countdown(10)

    while True:
        try:
            clear()
            print("\n" + "╔" + "═" * 58 + "╗")
            print("║" + "🎓 QUISQUEYA SYSTÈME QUIZ - MENU PRINCIPAL 🎓".center(58) + "║")
            print("╚" + "═" * 58 + "╝\n")

            options = [
                "🎮 Jouer",
                "🏆 Classement / Scores",
                "📖 Instructions / Aide",
                "🚪 Quitter"
            ]

            for i, opt in enumerate(options, start=1):
                print(f"   {i}) {opt}")
            print("\n" + "─" * 60)

            choice = safe_int("➤ Votre choix (1-4) : ", min_val=1, max_val=4)

            if choice == 1:
                while True:
                    clear()
                    print("\n" + "╔" + "═" * 58 + "╗")
                    print("║" + "🎮 MENU JOUER".center(58) + "║")
                    print("╚" + "═" * 58 + "╝\n")
                    print("   1) ⚡ Mode rapide (10 questions)")
                    print("   2) ⚙️  Mode personnalisé")
                    print("   0) ← Retour au menu principal\n")
                    print("─" * 60)

                    sub = safe_int("➤ Votre choix : ", min_val=0, max_val=2, default=0)
                    if sub == 0:
                        break
                    elif sub == 1:
                        play_quick_mode(qb, storage)
                    elif sub == 2:
                        play_custom_mode(qb, storage)

            elif choice == 2:
                show_leaderboard(storage)
            elif choice == 3:
                instructions()
            elif choice == 4:
                sure = safe_input("❓ Êtes-vous sûr de vouloir quitter ? (O/N) : ").strip().lower().startswith("o")
                if sure:
                    clear()
                    print("\n" + "═" * 60)
                    print("👋 Merci d'avoir joué à Quisqueya Système Quiz !".center(60))
                    print("À bientôt ! 🎓".center(60))
                    print("═" * 60 + "\n")
                    break

        except Exception as e:
            print("\n" + "─" * 60)
            print(f"❌ [Erreur inattendue] {e}")
            print("─" * 60)
            input("\n📌 Appuyez sur [ENTRÉE] pour revenir au menu principal...")


if __name__ == "__main__":
    main()
