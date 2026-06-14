import json
from faster_whisper import WhisperModel

FICHIER_AUDIO = "audio_final.mp3"
FICHIER_SORTIE = "subtitles.json"

# 🔥 LE FIX : Un dictionnaire de clean-up pour corriger les erreurs de Whisper
CORRECTIONS_PHONETIQUES = {
    "autant": "Au temps",
    "lors": "L'or",
    "colisea": "Colisée",
    "changait": "changeait",
    "sacrége": "sacrilège",
    "tunnel": "tunnels"
}

def generer_sous_titres_multi():
    print("🧠 Chargement du modèle Whisper (base)...")
    model = WhisperModel("base", device="cpu", compute_type="int8")

    print("🎧 Transcription brute (Sécurisée contre les boucles)...")
    # On supprime initial_prompt pour retrouver une synchronisation parfaite de A à Z
    segments, info = model.transcribe(
        FICHIER_AUDIO, 
        word_timestamps=True, 
        language="fr"
    )
    
    liste_mots = []
    for segment in segments:
        for word in segment.words:
            mot_propre = word.word.strip()
            if mot_propre:
                liste_mots.append({
                    "mot": mot_propre,
                    "debut": round(word.start, 2),
                    "fin": round(word.end, 2)
                })

    # --- POST-PROCESSING : RECOLLER LES APOSTROPHES & CORRIGER L'ORTHOGRAPHE ---
    mots_nettoyes = []
    i = 0
    while i < len(liste_mots):
        mot_actuel = liste_mots[i]
        
        # 1. Gestion des élisions/apostrophes (d', l', c'...)
        if mot_actuel["mot"].lower() in ['d', 'l', 'c', 'j', 'm', 't', 's', 'n'] and i + 1 < len(liste_mots):
            prochain_mot = liste_mots[i+1]
            if prochain_mot["mot"].startswith("'"):
                mot_actuel["mot"] = mot_actuel["mot"] + prochain_mot["mot"]
                mot_actuel["fin"] = prochain_mot["fin"]
                
                # Check du dictionnaire sur le mot combiné (ex: "lors" -> "L'or")
                mot_lower = mot_actuel["mot"].lower()
                if mot_lower in CORRECTIONS_PHONETIQUES:
                    mot_actuel["mot"] = CORRECTIONS_PHONETIQUES[mot_lower]
                    
                mots_nettoyes.append(mot_actuel)
                i += 2
                continue
        
        # 2. Check du dictionnaire sur les mots simples (ex: "autant" -> "Au temps")
        mot_lower = mot_actuel["mot"].lower()
        if mot_lower in CORRECTIONS_PHONETIQUES:
            mot_actuel["mot"] = CORRECTIONS_PHONETIQUES[mot_lower]
                
        mots_nettoyes.append(mot_actuel)
        i += 1

    with open(FICHIER_SORTIE, "w", encoding="utf-8") as f:
        json.dump(mots_nettoyes, f, indent=4, ensure_ascii=False)
        
    print(f"✅ Terminé ! Fichier '{FICHIER_SORTIE}' parfaitement synchronisé et corrigé.")

if __name__ == "__main__":
    generer_sous_titres_multi()