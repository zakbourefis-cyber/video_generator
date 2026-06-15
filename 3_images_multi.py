import json
import requests
import os
import urllib.parse
import time
import random

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
        num = scene.get("num_scene", 1)
        prompt_de_base = scene.get("mot_cle_visuel", "historical mystery")
        prompt_ia = f"{prompt_de_base}, realistic, cinematic lighting, historical, 8k resolution, highly detailed"

        print(f"\n🖼️ [Scène {num}/{len(scenes)}] Création de l'image pour : '{prompt_de_base}'...")

        prompt_encode = urllib.parse.quote(prompt_ia)
        seed = random.randint(1, 99999)

        url = (
            f"https://image.pollinations.ai/prompt/{prompt_encode}"
            f"?width=1080&height=1920&seed={seed}&model=flux"
        )

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://pollinations.ai/',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        }

        try:
            reponse = requests.get(url, headers=headers, timeout=60)

            if reponse.status_code == 200:
                # Vérification que c'est bien une image (pas une page d'erreur HTML)
                content_type = reponse.headers.get('Content-Type', '')
                if 'image' in content_type:
                    nom_fichier = f"scene_{num}.jpg"
                    with open(nom_fichier, "wb") as f:
                        f.write(reponse.content)
                    print(f"✅ Image {num} générée avec succès : {nom_fichier}")
                else:
                    print(f"⚠️ Scène {num} : réponse reçue mais ce n'est pas une image (Content-Type: {content_type}).")
                    _creer_image_fallback(num)
            else:
                print(f"⚠️ Erreur de génération pour la scène {num} (Code API: {reponse.status_code}).")
                _creer_image_fallback(num)

            time.sleep(3)  # Pause plus longue pour éviter le rate limiting

        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout pour la scène {num} — création d'une image de remplacement.")
            _creer_image_fallback(num)
        except Exception as e:
            print(f"❌ Impossible de générer l'image {num} : {e}")
            _creer_image_fallback(num)


def _creer_image_fallback(num):
    """Crée une image noire de remplacement pour ne pas bloquer le montage."""
    try:
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (1080, 1920), color=(20, 20, 20))
        draw = ImageDraw.Draw(img)
        draw.text((540, 960), f"Scène {num}", fill=(120, 120, 120), anchor="mm")
        img.save(f"scene_{num}.jpg")
        print(f"  ↳ Image fallback créée : scene_{num}.jpg")
    except ImportError:
        print("  ↳ Pillow non disponible pour le fallback. Installe-le : pip install Pillow")


if __name__ == "__main__":
    generer_banque_images_ia()