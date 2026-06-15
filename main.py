import subprocess
import os
import sys
import time

# Liste de tes scripts dans l'ordre chronologique exact
PIPELINE = [
    "1_script_gen.py",
    "2_audio.py",
    "3_video.py",
    "4_subtitles.py",
    "5_montage.py"
]

def executer_script(nom_script):
    """Exécute un script Python et vérifie s'il a planté."""
    print(f"\n{'='*50}")
    print(f"🚀 LANCEMENT DE L'ÉTAPE : {nom_script}")
    print(f"{'='*50}\n")
    
    # On lance le script avec la même version de Python que celle qui exécute main.py
    resultat = subprocess.run([sys.executable, nom_script])
    
    # Si le script retourne un code d'erreur (différent de 0)
    if resultat.returncode != 0:
        print(f"\n❌ ERREUR CRITIQUE : Le script {nom_script} a échoué.")
        print("🛑 Arrêt immédiat de l'usine pour éviter de corrompre les données.")
        return False
    
    return True

def demarrer_usine():
    print("🏭 DÉMARRAGE DE L'USINE À CONTENU AUTOMATISÉE 🏭")
    
    # Étape 1 : On vérifie s'il y a un sujet en attente en lançant le générateur
    succes = executer_script(PIPELINE[0])
    if not succes:
        sys.exit(1)
        
    # Vérification de sécurité : le script 1 a-t-il bien créé le fichier pivot ?
    if not os.path.exists("script_output.json"):
        print("\nℹ️ Aucun fichier 'script_output.json' généré.")
        print("✅ Cela signifie probablement que tous les sujets du CSV sont marqués comme 'Publie'.")
        print("Ajoute de nouveaux sujets dans le CSV pour relancer la machine !")
        sys.exit(0)

    # Étape 2 : Si le json existe, on enchaîne le reste de la production
    for script in PIPELINE[1:]:
        # Petite pause pour laisser le processeur respirer entre deux grosses tâches
        time.sleep(2)
        
        succes = executer_script(script)
        if not succes:
            sys.exit(1)

    print("\n✨=============================================✨")
    print(" 🎉 PRODUCTION TERMINÉE AVEC SUCCÈS ! ")
    print(" 📂 Vérifie ton dossier pour voir le fichier final.")
    print("✨=============================================✨\n")

if __name__ == "__main__":
    demarrer_usine()