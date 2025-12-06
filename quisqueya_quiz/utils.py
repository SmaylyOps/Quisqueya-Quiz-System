# utils.py
import os
from typing import Optional

def clear():
    """Efface la console (cls sous Windows, clear sous Unix)."""
    os.system("cls" if os.name == "nt" else "clear")

def safe_input(prompt: str = "") -> str:
    """Input simple, protège contre KeyboardInterrupt et retourne chaîne (vide si interruption)."""
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print("")  # newline for neatness
        return ""

def safe_int(prompt: str, min_val: Optional[int] = None, max_val: Optional[int] = None, default: Optional[int] = None) -> int:
    """
    Demande un entier à l'utilisateur, boucle jusqu'à obtention d'une valeur valide.
    Retourne default si fournie et l'utilisateur appuie sur entrée.
    """
    while True:
        s = safe_input(prompt).strip()
        if s == "" and default is not None:
            return default
        try:
            v = int(s)
            if (min_val is not None and v < min_val) or (max_val is not None and v > max_val):
                rng = []
                if min_val is not None:
                    rng.append(f">= {min_val}")
                if max_val is not None:
                    rng.append(f"<= {max_val}")
                print(f"Valeur invalide — entrez un entier {' et '.join(rng)}.")
                continue
            return v
        except ValueError:
            print("Entrée invalide — merci d'entrer un nombre entier.")

def choose_from_list(items: list, prompt: str = "Choix (numéro) : ", allow_zero_return: bool = False) -> Optional[int]:
    """
    Affiche items numérotés (1..n) et demande un choix. Retourne:
      - int index (0-based) si valide
      - None si l'utilisateur choisit 0 (si allow_zero_return True)
    Boucle tant que l'entrée est invalide.
    """
    if not items:
        print("[Aucun élément disponible]")
        return None
    for idx, it in enumerate(items, start=1):
        print(f"{idx}) {it}")
    if allow_zero_return:
        print("0) Retour")
    while True:
        choice = safe_input(prompt).strip()
        if choice == "" and allow_zero_return:
            return None
        try:
            n = int(choice)
            if allow_zero_return and n == 0:
                return None
            if 1 <= n <= len(items):
                return n - 1
            print("Choix hors limites. Réessaie.")
        except ValueError:
            print("Choix invalide — entrez le numéro correspondant.")
