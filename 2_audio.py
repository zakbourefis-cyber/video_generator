import json
import asyncio
import edge_tts

FICHIER_SCRIPT = "script_output.json"
FICHIER_AUDIO = "audio_final.mp3"
VOIX_CHOISIE = "fr-FR-VivienneMultilingualNeural"

async def generer_audio_global():
    print("📖 Lecture du script multi-scènes...")
    try:
        with open(FICHIER_SCRIPT, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Erreur : {FICHIER_SCRIPT} introuvable.")
        return

    scenes = data.get("scenes", [])
    if not scenes:
        print("❌ Erreur : Aucune scène trouvée dans le fichier.")
        return

    # On fusionne les textes en insérant une ponctuation forte (période/virgule) 
    # pour que l'IA marque un temps d'arrêt naturel entre les scènes.
    texte_complet = ""
    for scene in scenes:
        texte_complet += scene["texte_voix_off"] + " ... "

    print(f"🎙️ Génération de la voix off globale ({len(texte_complet.split())} mots)...")
    
    communicate = edge_tts.Communicate(texte_complet, VOIX_CHOISIE)
    await communicate.save(FICHIER_AUDIO)
    
    print(f"✅ Audio global sauvegardé : {FICHIER_AUDIO}")

if __name__ == "__main__":
    asyncio.run(generer_audio_global())