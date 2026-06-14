import json
import os
import glob
import sys

# 🔥 MONKEYPATCH : Correctif de compatibilité Pillow 10+ / MoviePy 1.0.3
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    # On rattaché l'ancien nom vers la nouvelle nomenclature de Pillow
    try:
        PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
    except AttributeError:
        PIL.Image.ANTIALIAS = 3 # Valeur entière historique d'ANTIALIAS au cas où

# ==========================================
# 1. DÉTECTION AUTOMATIQUE D'IMAGEMAGICK
# ==========================================
chemins_possibles = glob.glob(r"C:\Program Files\ImageMagick*\magick.exe")

if not chemins_possibles:
    print("❌ Erreur : Impossible de trouver ImageMagick dans C:\\Program Files\\")
    sys.exit(1)

vrai_chemin = chemins_possibles[0]
print(f"🔧 ImageMagick détecté automatiquement : {vrai_chemin}")
os.environ["IMAGEMAGICK_BINARY"] = vrai_chemin

# ==========================================
# 2. IMPORT DE MOVIEPY (Maintenant ça ne crashera plus !)
# ==========================================
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

# --- CONFIGURATION ---
AUDIO_VOIX = "audio_final.mp3"
SOUS_TITRES_JSON = "subtitles.json"
OUTPUT_FINAL = "short_final.mp4"

POLICE_TEXTE = "Impact"
TAILLE_POLICE = 75
COULEUR_TEXTE = "white"

# 🔥 FIX SYNCHRO : Ajoute un petit délai (en secondes) pour attendre que la voix commence.
# Si le texte est en AVANCE sur la voix, augmente cette valeur (ex: 0.3).
# Si le texte est en RETARD, diminue-la ou mets 0.0.
DECALAGE_SOUS_TITRES = 0.25 
# ---------------------

def assembler_video_professionnelle():
    print("🎬 Démarrage du montage multi-scènes optimisé...")

    if not os.path.exists(AUDIO_VOIX) or not os.path.exists(SOUS_TITRES_JSON):
        print("❌ Erreur : Audio ou sous-titres manquants.")
        return

    audio_clip = AudioFileClip(AUDIO_VOIX)
    duree_totale = audio_clip.duration
    print(f"⏱️ Durée totale du Short : {duree_totale:.2f} secondes.")

    print("🎞️ Assemblage et redimensionnement de la séquence de fond...")
    nombre_scenes = 5
    duree_par_scene = duree_totale / nombre_scenes

    clips_fond_ordonnes = []

    for i in range(1, nombre_scenes + 1):
        nom_video = f"scene_{i}.mp4"
        if not os.path.exists(nom_video):
            print(f"❌ Erreur : Le fichier {nom_video} est introuvable.")
            return
            
        clip_scene = VideoFileClip(nom_video)
        
        # 🔥 FIX FOND NOIR : On force la vidéo à se redimensionner exactement en 1080x1920
        # sans déformer l'image (MoviePy va l'ajuster pour remplir l'écran)
        clip_scene = clip_scene.resize(newsize=(1080, 1920))
        
        # Ajustement de la durée
        if clip_scene.duration > duree_par_scene:
            clip_scene = clip_scene.subclip(0, duree_par_scene)
        else:
            clip_scene = clip_scene.loop(duration=duree_par_scene)
            
        temps_depart = (i - 1) * duree_par_scene
        clip_scene = clip_scene.set_start(temps_depart)
        
        clips_fond_ordonnes.append(clip_scene)

    # Création du fond complet sans bordures noires
    fond_complet = CompositeVideoClip(clips_fond_ordonnes, size=(1080, 1920))

    print("✍️ Incrustation des sous-titres avec recalibrage temporel...")
    with open(SOUS_TITRES_JSON, "r", encoding="utf-8") as f:
        mots_chronometres = json.load(f)

    liste_clips_texte = []

    for item in mots_chronometres:
        mot = item["mot"].upper()
        
        # 🔥 FIX SYNCHRO : On applique le décalage aux chonos de Whisper
        debut = item["debut"] + DECALAGE_SOUS_TITRES
        fin = item["fin"] + DECALAGE_SOUS_TITRES
        duree = fin - debut

        if duree <= 0:
            duree = 0.1

        try:
            txt_clip = (TextClip(mot, font=POLICE_TEXTE, fontsize=TAILLE_POLICE, color=COULEUR_TEXTE)
                        .set_start(debut)
                        .set_duration(duree)
                        .set_position(('center', 'center')))
            
            liste_clips_texte.append(txt_clip)
        except Exception as e:
            print(f"⚠️ Erreur sur le mot '{mot}': {e}")
            return

    video_finale = CompositeVideoClip([fond_complet] + liste_clips_texte)
    video_finale.audio = audio_clip

    print("🚀 Lancement du rendu final (Plein écran + Audio synchronisé)...")
    video_finale.write_videofile(
        OUTPUT_FINAL,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        audio_bitrate="192k",
        audio=True,
        temp_audiofile="temp_voice_render.m4a",
        remove_temp=True,
        threads=4,
        logger="bar"
    )

    for c in clips_fond_ordonnes:
        c.close()
    fond_complet.close()
    audio_clip.close()
    video_finale.close()
    
    print(f"🎉 Rendu terminé avec succès sans bandes noires ! Fichier : {OUTPUT_FINAL}")

if __name__ == "__main__":
    assembler_video_professionnelle()