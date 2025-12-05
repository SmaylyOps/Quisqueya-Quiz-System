import os

def clear():
    """Efface l'écran selon l'OS (Windows, Mac, Linux)."""
    os.system('cls' if os.name == 'nt' else 'clear')
