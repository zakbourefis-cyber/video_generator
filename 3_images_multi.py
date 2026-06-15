import json
import requests
import os
import urllib.parse
import time

FICHIER_SCRIPT = "script_output.json"

def generer_banque_images_ia():
    try:
        with open(FICHIER_SCRIPT, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Erreur : script_output.json introuvable.")
        return

    scenes = data.get("scenes", [])
    print("🎨 Lancement de la génération d'images IA (Haute qualité)...")
    
    for scene in scenes:
        num = scene["num_scene"]
        # On récupère le mot clé de Llama et on ajoute des tags de qualité de rendu
        prompt_de_base = scene["mot_cle_visuel"]
        prompt_ia = f"{prompt_de_base}, realistic, cinematic lighting, historical, 8k resolution, highly detailed"
        
        print(f"\n🖼️ [Scène {num}/{len(scenes)}] Création de l'image pour : '{prompt_de_base}'...")
        
        # Encodage du prompt pour l'URL
        prompt_encode = urllib.parse.quote(prompt_ia)
        # Appel à l'API ouverte de Pollinations (Image au format Short 1080x1920)
        url = f"https://image.pollinations.ai/prompt/{prompt_encode}?width=1080&height=1920&nologo=true"
        
        try:
            reponse = requests.get(url)
            if reponse.status_code == 200:
                nom_fichier = f"scene_{num}.jpg"
                with open(nom_fichier, "wb") as f:
                    f.write(reponse.content)
                print(f"✅ Image {num} générée avec succès : {nom_fichier}")
            else:
                print(f"⚠️ Erreur de génération pour la scène {num}.")
                
            # Petite pause pour ne pas surcharger le serveur
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Impossible de générer l'image {num} : {e}")

if __name__ == "__main__":
    generer_banque_images_ia()