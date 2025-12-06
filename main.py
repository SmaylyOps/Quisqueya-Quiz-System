# main.py - Point d'entrée principal du Quisqueya Système Quiz
# Ce fichier gère l'interface utilisateur et la navigation dans les menus

from question_bank import QuestionBank
from storage import Storage
from quiz import QuizGame
from utils import clear, safe_input, safe_int, choose_from_list
import os
import json
import time
import threading


def welcome_and_countdown(seconds: int = 10):
    """
    Affiche l'écran de bienvenue avec un compte à rebours
    L'utilisateur peut appuyer sur Entrée pour passer immédiatement au menu

    Args:
        seconds: Durée du compte à rebours en secondes (par défaut 10)
    """
    clear()
    # Affichage du titre avec des bordures décoratives
    print("\n╔" + "═" * 60 + "╗")
    print("║" + " " * 60 + "║")
    print("║" + "    🎓 BIENVENUE DANS QUISQUEYA SYSTÈME QUIZ 🎓    ".center(57) + "║")
    print("║" + " " * 60 + "║")
    print("╚" + "═" * 60 + "╝")
    print()
    print("📌 Appuyez sur [ENTRÉE] pour accéder immédiatement au menu")
    print("⏱️  Sinon, le menu apparaîtra après le compte à rebours...\n")

    # Dictionnaire pour suivre si l'utilisateur a appuyé sur Entrée
    skip = {"pressed": False}

    def wait_enter():
        """Fonction qui attend que l'utilisateur appuie sur Entrée"""
        try:
            input()
            skip["pressed"] = True
        except:
            skip["pressed"] = False

    # Démarrage d'un thread pour écouter l'entrée utilisateur
    t = threading.Thread(target=wait_enter, daemon=True)
    t.start()

    # Compte à rebours
    for i in range(seconds, 0, -1):
        if skip["pressed"]:
            break
        print(f"⏳ Démarrage dans {i} seconde(s)...".ljust(40), end="\r")
        time.sleep(1)

    clear()


def select_theme_interactive(qb: QuestionBank):
    """
    Permet à l'utilisateur de sélectionner un thème parmi ceux disponibles

    Args:
        qb: Instance de QuestionBank contenant toutes les questions

    Returns:
        Liste contenant le thème sélectionné, ou None si l'utilisateur choisit de revenir
    """
    themes = qb.list_themes()

    # Vérification qu'il y a des thèmes disponibles
    if not themes:
        print("❌ Aucun thème disponible pour le moment.")
        input("\n📌 Appuyez sur [ENTRÉE] pour revenir au menu...")
        return None

    # Affichage de l'en-tête
    print("\n" + "─" * 60)
    print("📚 THÈMES DISPONIBLES".center(60))
    print("─" * 60 + "\n")

    # Sélection du thème via la fonction utilitaire
    idx = choose_from_list(
        themes,
        prompt="\n➤ Entrez le numéro du thème choisi (ou 0 pour revenir) : ",
        allow_zero_return=True
    )

    # Si l'utilisateur choisit de revenir
    if idx is None:
        return None

    # Retourne le thème sélectionné dans une liste
    return [themes[idx]]


def play_quick_mode(qb: QuestionBank, storage: Storage):
    """
    Lance une partie en mode rapide (10 questions maximum)
    Mode simplifié pour commencer rapidement
    Timer activé automatiquement à 15 secondes par question

    Args:
        qb: Banque de questions
        storage: Gestionnaire de sauvegarde des scores
    """
    clear()
    print("\n" + "═" * 60)
    print("⚡ MODE RAPIDE - 10 QUESTIONS".center(60))
    print("═" * 60 + "\n")

    # Demande du nom du joueur
    print("─" * 60)
    player = safe_input("👤 Entrez votre nom ou pseudo : ").strip() or "Joueur"

    # Timer activé automatiquement à 15 secondes
    timer_val = 15
    print(f"\n⏱️  Minuterie activée : {timer_val} secondes par question")

    # Échantillonnage de 10 questions aléatoires (tous thèmes confondus)
    qlist = qb.sample_questions(count=10, themes=None)

    if not qlist:
        print("\n❌ Aucune question disponible.")
        input("\n📌 Appuyez sur [ENTRÉE] pour revenir...")
        return

    # Affichage d'un message de démarrage
    print(f"\n🎮 Démarrage de la partie avec {len(qlist)} questions aléatoires...")
    time.sleep(1)

    # Lancement du jeu avec timer
    game = QuizGame(qlist, player, storage, timer_per_question=timer_val)
    game.play()


def play_custom_mode(qb: QuestionBank, storage: Storage):
    """
    Lance une partie en mode personnalisé
    Timer activé automatiquement à 15 secondes par question
    10 questions aléatoires de tous les thèmes

    Args:
        qb: Banque de questions
        storage: Gestionnaire de sauvegarde des scores
    """
    clear()
    print("\n" + "═" * 60)
    print("⚙️  MODE PERSONNALISÉ".center(60))
    print("═" * 60 + "\n")

    # Nom du joueur
    print("👤 Identification")
    player = safe_input("   Entrez votre nom ou pseudo : ").strip() or "Joueur"

    # Timer activé automatiquement à 15 secondes
    timer_val = 15
    print(f"\n⏱️  Minuterie activée : {timer_val} secondes par question")

    # Échantillonnage de 10 questions aléatoires (tous thèmes)
    qlist = qb.sample_questions(count=10, themes=None, balanced=False)

    if not qlist:
        print("\n❌ Aucune question disponible.")
        input("\n📌 Appuyez sur [ENTRÉE] pour revenir...")
        return

    # Récapitulatif avant de commencer
    print("\n" + "─" * 60)
    print("✅ Configuration terminée !")
    print(f"   • Joueur : {player}")
    print(f"   • Questions : {len(qlist)} questions aléatoires")
    print(f"   • Thèmes : Tous")
    print(f"   • Minuterie : {timer_val} secondes par question")
    print("─" * 60)

    input("\n📌 Appuyez sur [ENTRÉE] pour commencer...")

    # Lancement du jeu avec timer
    game = QuizGame(qlist, player, storage, timer_per_question=timer_val)
    game.play()


def show_leaderboard(storage: Storage):
    """
    Affiche le classement des meilleurs scores

    Args:
        storage: Gestionnaire de stockage des scores
    """
    clear()
    print("\n" + "═" * 60)
    print("🏆 CLASSEMENT DES MEILLEURS SCORES".center(60))
    print("═" * 60 + "\n")

    # Nombre de scores à afficher
    n = safe_int(
        "📊 Combien de scores voulez-vous voir ? (1-50, défaut: 10) : ",
        min_val=1,
        max_val=50,
        default=10
    )

    # Filtre par thème (optionnel)
    print("\n🔍 Filtrage")
    theme = safe_input(
        "   Filtrer par thème ? (tapez le nom exact ou laissez vide pour tous) : "
    ).strip() or None

    # Récupération des meilleurs scores
    top = storage.top_n(n, theme)

    if not top:
        print("\n❌ Aucun score enregistré pour le moment.")
        print("   Jouez une partie pour apparaître dans le classement !")
    else:
        # En-tête du tableau
        print("\n" + "─" * 60)
        if theme:
            print(f"📚 Thème : {theme}".center(60))
        else:
            print("📚 Tous les thèmes".center(60))
        print("─" * 60 + "\n")

        # Affichage de chaque score
        for i, s in enumerate(top, start=1):
            # Calcul du pourcentage
            pourc = s.get("pourcentage", None)
            pourc_str = f"{pourc}%" if pourc is not None else "N/A"

            # Emoji selon le rang
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            else:
                medal = f"{i}."

            # Affichage formaté
            print(f"{medal} {s.get('joueur_nom')}")
            print(f"   Score : {s.get('score_total')} points")
            print(f"   Réussite : {s.get('bonnes')}/{s.get('nombre_questions')} ({pourc_str})")
            print(f"   Date : {s.get('date_heure')[:10]}")
            print(f"   Thème : {s.get('theme')}")
            print()

    print("─" * 60)
    input("\n📌 Appuyez sur [ENTRÉE] pour revenir au menu principal...")


def instructions():
    """
    Affiche les instructions et l'aide du jeu
    """
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
    print("   • Le fichier 'scores.json' contient l'historique")
    print("   • Consultez le classement dans le menu principal\n")

    print("📚 MODES DE JEU\n")
    print("   • Mode Rapide : 10 questions, configuration simple")
    print("   • Mode Personnalisé : choisissez tout en détail\n")

    print("⚙️  NAVIGATION\n")
    print("   • Tapez le numéro de l'option souhaitée")
    print("   • '0' permet généralement de revenir en arrière")
    print("   • En cas d'erreur, le jeu vous guidera\n")

    print("💡 ASTUCES\n")
    print("   • Lisez bien chaque question avant de répondre")
    print("   • En mode équilibré, les questions sont variées")
    print("   • Vos statistiques sont suivies dans le classement\n")

    print("═" * 60)
    input("\n📌 Appuyez sur [ENTRÉE] pour revenir au menu...")


def main():
    """
    Fonction principale qui lance l'application
    Gère la boucle du menu principal et la navigation
    """
    # Chargement de la banque de questions depuis le dossier "questions"
    qb = QuestionBank(folder="questions")

    # Chemin alternatif si le dossier principal n'existe pas
    if not qb.questions:
        alt = "/mnt/data/quisqueya_questions_by_theme"
        if os.path.isdir(alt):
            qb = QuestionBank(folder=alt)

    # Initialisation du système de stockage des scores
    storage = Storage()

    # Affichage de l'écran de bienvenue avec compte à rebours
    welcome_and_countdown(10)

    # Boucle principale du menu
    while True:
        try:
            clear()
            # Affichage du menu principal avec bordures
            print("\n" + "╔" + "═" * 58 + "╗")
            print("║" + "🎓 QUISQUEYA SYSTÈME QUIZ - MENU PRINCIPAL 🎓".center(58) + "║")
            print("╚" + "═" * 58 + "╝\n")

            # Options du menu
            options = [
                "🎮 Jouer",
                "🏆 Classement / Scores",
                "📖 Instructions / Aide",
                "🚪 Quitter"
            ]

            # Affichage des options numérotées
            for i, opt in enumerate(options, start=1):
                print(f"   {i}) {opt}")

            print("\n" + "─" * 60)

            # Demande du choix utilisateur
            choice = safe_int("➤ Votre choix (1-4) : ", min_val=1, max_val=4)

            # Option 1 : Jouer (sous-menu)
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
                        break  # Retour au menu principal
                    elif sub == 1:
                        play_quick_mode(qb, storage)
                    elif sub == 2:
                        play_custom_mode(qb, storage)

            # Option 2 : Afficher le classement
            elif choice == 2:
                show_leaderboard(storage)

            # Option 3 : Afficher les instructions
            elif choice == 3:
                instructions()

            # Option 4 : Quitter l'application
            elif choice == 4:
                print("\n" + "─" * 60)
                sure = safe_input("❓ Êtes-vous sûr de vouloir quitter ? (O/N) : ").strip().lower().startswith("o")
                if sure:
                    clear()
                    print("\n" + "═" * 60)
                    print("👋 Merci d'avoir joué à Quisqueya Système Quiz !".center(60))
                    print("À bientôt ! 🎓".center(60))
                    print("═" * 60 + "\n")
                    break  # Sortie de la boucle principale

        except Exception as e:
            # Gestion des erreurs pour éviter un crash complet
            print("\n" + "─" * 60)
            print(f"❌ [Erreur inattendue] {e}")
            print("─" * 60)
            input("\n📌 Appuyez sur [ENTRÉE] pour revenir au menu principal...")


# Point d'entrée du programme
if __name__ == "__main__":
    main()