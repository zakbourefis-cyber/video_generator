import json
import os
import glob
import sys
import time

# --- FIX PILLOW / MOVIEPY ---
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    try:
        PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
    except AttributeError:
        PIL.Image.ANTIALIAS = 3

# --- DÉTECTION IMAGEMAGICK ---
chemins_possibles = glob.glob(r"C:\Program Files\ImageMagick*\magick.exe")
if not chemins_possibles:
    print("❌ Erreur : ImageMagick introuvable.")
    sys.exit(1)
os.environ["IMAGEMAGICK_BINARY"] = chemins_possibles[0]

from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

# --- CONFIGURATION ---
AUDIO_VOIX = "audio_final.mp3"
SOUS_TITRES_JSON = "subtitles.json"
FICHIER_SCRIPT = "script_output.json"

POLICE_TEXTE = "Impact"
TAILLE_POLICE = 75
COULEUR_TEXTE = "white"
DECALAGE_SOUS_TITRES = 0.25 
# ---------------------

def nettoyer_fichiers_temporaires(nombre_scenes):
    print("🧹 Nettoyage de l'espace de travail...")
    fichiers_a_supprimer = [AUDIO_VOIX, SOUS_TITRES_JSON, FICHIER_SCRIPT]
    for i in range(1, nombre_scenes + 1):
        fichiers_a_supprimer.append(f"scene_{i}.jpg")
        
    for fichier in fichiers_a_supprimer:
        if os.path.exists(fichier):
            try:
                os.remove(fichier)
                print(f"  🗑️ Supprimé : {fichier}")
            except Exception as e:
                print(f"  ⚠️ Impossible de supprimer {fichier} (Peut-être encore ouvert) : {e}")

def assembler_video_professionnelle():
    print("🎬 Démarrage du montage multi-scènes dynamique...")

    if not os.path.exists(AUDIO_VOIX) or not os.path.exists(SOUS_TITRES_JSON) or not os.path.exists(FICHIER_SCRIPT):
        print("❌ Erreur : Fichiers de base manquants.")
        return

    # 1. On lit le JSON pour savoir l'ID de la vidéo et le nombre de scènes
    with open(FICHIER_SCRIPT, "r", encoding="utf-8") as f:
        data_script = json.load(f)
        
    # On récupère le nom du fichier de sortie depuis le titre généré (en le nettoyant)
    titre_brut = data_script.get("titre", "short_final")
    nom_fichier_sortie = "".join(c for c in titre_brut if c.isalnum() or c in [' ']).strip().replace(' ', '_') + ".mp4"
    
    nombre_scenes = len(data_script.get("scenes", []))
    print(f"📊 Détection dynamique : La vidéo contient {nombre_scenes} scènes.")

    audio_clip = AudioFileClip(AUDIO_VOIX)
    duree_totale = audio_clip.duration
    duree_par_scene = duree_totale / nombre_scenes

    clips_fond_ordonnes = []

    # ... (Le début du fichier avec la détection ImageMagick reste pareil) ...

    audio_clip = AudioFileClip(AUDIO_VOIX)
    duree_totale = audio_clip.duration
    duree_par_scene = duree_totale / nombre_scenes
    print(f"⏱️ L'audio fait {duree_totale:.2f}s. Chaque image restera à l'écran {duree_par_scene:.2f}s.")

    clips_fond_ordonnes = []

    for i in range(1, nombre_scenes + 1):
        nom_image = f"scene_{i}.jpg"
        if not os.path.exists(nom_image):
            print(f"❌ Erreur : {nom_image} introuvable.")
            return
            
        # On charge l'image générée par l'IA
        clip_scene = ImageClip(nom_image).set_duration(duree_par_scene)
        
        # On définit son moment d'apparition
        temps_depart = (i - 1) * duree_par_scene
        clip_scene = clip_scene.set_start(temps_depart)
        
        # On ajoute un fondu enchaîné d'une demi-seconde pour une transition douce
        if i > 1:
            clip_scene = clip_scene.crossfadein(0.5)
            
        clips_fond_ordonnes.append(clip_scene)

    # Fusion des images avec le fond
    fond_complet = CompositeVideoClip(clips_fond_ordonnes, size=(1080, 1920))

    # ... (La suite avec les sous-titres reste exactement la même !) ...

    with open(SOUS_TITRES_JSON, "r", encoding="utf-8") as f:
        mots_chronometres = json.load(f)

    liste_clips_texte = []
    for item in mots_chronometres:
        mot = item["mot"].upper()
        debut = item["debut"] + DECALAGE_SOUS_TITRES
        fin = item["fin"] + DECALAGE_SOUS_TITRES
        duree = max(0.1, fin - debut)

        try:
            txt_clip = (TextClip(mot, font=POLICE_TEXTE, fontsize=TAILLE_POLICE, color=COULEUR_TEXTE)
                        .set_start(debut)
                        .set_duration(duree)
                        .set_position(('center', 'center')))
            liste_clips_texte.append(txt_clip)
        except Exception:
            pass

    video_finale = CompositeVideoClip([fond_complet] + liste_clips_texte)
    video_finale.audio = audio_clip

    print(f"🚀 Lancement du rendu : {nom_fichier_sortie}...")
    video_finale.write_videofile(
        nom_fichier_sortie,
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

    # Sécurité : Fermeture de TOUS les clips pour débloquer les fichiers sous Windows
    for c in clips_fond_ordonnes:
        c.close()
    fond_complet.close()
    audio_clip.close()
    video_finale.close()
    
    # Pause technique pour laisser le temps à Windows de libérer les fichiers
    time.sleep(2)
    
    # Le fameux nettoyage post-rendu
    nettoyer_fichiers_temporaires(nombre_scenes)
    
    print(f"🎉 VIDÉO CRÉÉE ET DOSSIER NETTOYÉ : {nom_fichier_sortie}")

if __name__ == "__main__":
    assembler_video_professionnelle()