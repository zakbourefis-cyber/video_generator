import json
import requests
import os
import time

PEXELS_API_KEY = "tPbnx6VXbhQ5oD0JJDxZQhM7dVkjDj4OzHB6zpDgqZrVSnrJssZOvrrX"
FICHIER_SCRIPT = "script_output.json"

# Dictionnaire de secours pour traduire les mots-clés générés par Llama 3.2
DICTIONNAIRE_TRAD = {
    "sphinx": "sphinx egypt",
    "pompes funéraires": "ancient rome ritual",
    "tunnel secret": "dark ancient tunnel",
    "mappe des routes": "ancient map",
    "globes terrestre anciens": "ancient globe"
}

def traduire_mot_cle(mot):
    mot_lower = mot.lower().strip()
    # On regarde si on a une traduction pré-enregistrée, sinon on garde le mot brut
    return DICTIONNAIRE_TRAD.get(mot_lower, mot_lower)

def telecharger_banque_videos():
    try:
        with open(FICHIER_SCRIPT, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Erreur : script_output.json introuvable.")
        return

    scenes = data.get("scenes", [])
    
    for scene in scenes:
        num = scene["num_scene"]
        mot_fr = scene["mot_cle_visuel"]
        mot_en = traduire_mot_cle(mot_fr)
        
        print(f"\n🎬 [Scène {num}/5] Recherche pour : '{mot_fr}' (Traduit en : '{mot_en}')...")
        
        url = f"https://api.pexels.com/videos/search?query={mot_en}&orientation=portrait&per_page=1"
        headers = {"Authorization": PEXELS_API_KEY}
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"⚠️ Erreur API Pexels pour la scène {num}. On passe à la suivante.")
            continue
            
        donnees = response.json()
        if not donnees.get("videos"):
            print(f"⚠️ Aucune vidéo trouvée pour '{mot_en}'. Recherche d'un fallback 'ancient rome'...")
            # Fallback général si l'API ne trouve rien du tout
            url = f"https://api.pexels.com/videos/search?query=ancient+rome&orientation=portrait&per_page=1"
            donnees = requests.get(url, headers=headers).json()

        try:
            fichiers_video = donnees["videos"][0]["video_files"]
            lien_telechargement = None
            
            # Choix de la qualité HD
            for fichier in fichiers_video:
                if fichier["file_type"] == "video/mp4" and fichier["width"] >= 720:
                    lien_telechargement = fichier["link"]
                    break
            if not lien_telechargement and fichiers_video:
                lien_telechargement = fichiers_video[0]["link"]

            # Téléchargement effectif
            print(f"⬇️ Téléchargement du clip de fond pour la scène {num}...")
            video_data = requests.get(lien_telechargement)
            
            nom_fichier = f"scene_{num}.mp4"
            with open(nom_fichier, "wb") as f:
                f.write(video_data.content)
            print(f"✅ Scène {num} sauvegardée sous : {nom_fichier}")
            
            # Petite pause de sécurité entre les requêtes API
            time.sleep(1)
            
        except (IndexError, KeyError):
            print(f"❌ Impossible de récupérer un fichier vidéo valide pour la scène {num}.")

if __name__ == "__main__":
    telecharger_banque_videos()