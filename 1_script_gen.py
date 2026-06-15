import json
import csv
import os
from openai import OpenAI

# Configuration du client Odysseus local
client = OpenAI(
    base_url="http://localhost:11434/v1", 
    api_key="local-machine"
)

# On pointe bien vers le fichier préparé
FICHIER_SUJETS = "50_Sujets_Viraux.csv"

def charger_prochain_sujet():
    """Lit le CSV et retourne la première ligne avec le statut 'En attente'"""
    if not os.path.exists(FICHIER_SUJETS):
        print(f"❌ Erreur : Le fichier {FICHIER_SUJETS} est introuvable.")
        return None, None

    lignes = []
    sujet_selectionne = None
    index_selectionne = -1

    # 🔥 FIX DU BOM (Caractère invisible d'Excel) avec utf-8-sig
    with open(FICHIER_SUJETS, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        lignes = list(reader)

    # Recherche du premier sujet en attente
    for idx, ligne in enumerate(lignes):
        statut = ligne.get("Statut", "En attente").strip()
        if statut == "En attente" or statut == "":
            sujet_selectionne = ligne
            index_selectionne = idx
            break

    return sujet_selectionne, index_selectionne

def mettre_a_jour_statut(index_ligne, nouveau_statut):
    """Met à jour le statut de la ligne traitée dans le CSV"""
    lignes = []
    with open(FICHIER_SUJETS, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        champs = reader.fieldnames
        lignes = list(reader)

    if "Statut" not in champs: champs.append("Statut")
    if "Duree_Cible" not in champs: champs.append("Duree_Cible")
    if "Id_Video" not in champs: champs.append("Id_Video")

    lignes[index_ligne]["Statut"] = nouveau_statut

    with open(FICHIER_SUJETS, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=champs)
        writer.writeheader()
        writer.writerows(lignes)

def calculer_contraintes_video(duree_cible):
    """Calcule le nombre de mots et de scènes optimal selon la durée"""
    try:
        duree = int(duree_cible)
    except (ValueError, TypeError):
        duree = 45 

    total_mots = int(duree * 2.5)
    
    if duree <= 35:
        nb_scenes = 3
    elif duree <= 48:
        nb_scenes = 4
    else:
        nb_scenes = 5

    mots_par_scene = int(total_mots / nb_scenes)
    return duree, total_mots, nb_scenes, mots_par_scene

def generer_prompt_systeme(nb_scenes, mots_par_scene, total_mots):
    return f"""Tu es une IA spécialisée dans la génération de JSON strict.
Tu es un réalisateur de documentaires historiques mystérieux au format TikTok.

RÈGLES ABSOLUES :
1. Génère UN SEUL objet JSON global et valide. Pas de blocs séparés, pas de notes à la fin, pas de tirets.
2. NE CRÉE JAMAIS de clés en double. Tout le texte de la scène doit être dans une seule et unique chaîne "texte_voix_off" (fais 3 ou 4 phrases, mais garde-les dans la même variable).
3. Le champ "mot_cle_visuel" DOIT ÊTRE RÉDIGÉ EN ANGLAIS EXCLUSIVEMENT.

Voici la SEULE structure autorisée (tu dois générer exactement {nb_scenes} scènes dans le tableau "scenes") :
{{
    "titre": "Titre accrocheur du short",
    "scenes": [
        {{
            "num_scene": 1,
            "texte_voix_off": "Tout le texte de la scène 1 se trouve ici, d'un seul bloc, sans retours à la ligne compliqués (environ {mots_par_scene} mots).",
            "mot_cle_visuel": "ENGLISH PROMPT ONLY (ex: 'ancient wooden ship buried under dark dirt, cinematic lighting, 8k')"
        }},
        {{
            "num_scene": 2,
            "texte_voix_off": "Tout le texte de la scène 2 se trouve ici...",
            "mot_cle_visuel": "ENGLISH PROMPT ONLY (ex: 'anglo saxon gold helmet artifacts close up, 8k resolution')"
        }}
    ]
}}"""

def executer_pipeline_generation():
    sujet, idx = charger_prochain_sujet()
    if not sujet:
        print("🎉 Tous les sujets du fichier Excel ont été traités !")
        return

    # 🔥 FIX KEYERROR : Utilisation sécurisée avec .get()
    sujet_id = sujet.get("ID", str(idx))
    duree_csv = sujet.get("Duree_Cible", "45") or "45"
    id_video = sujet.get("Id_Video", f"video_{sujet_id}") or f"video_{sujet_id}"
    
    duree, total_mots, nb_scenes, mots_par_scene = calculer_contraintes_video(duree_csv)
    
    print(f"🎬 Sujet trouvé : '{sujet.get('Sujet', 'Sujet inconnu')}' (ID: {sujet_id})")
    print(f"⏱️ Configuration dynamique : {duree}s ciblées -> {nb_scenes} scènes, ~{total_mots} mots au total.")

    sys_prompt = generer_prompt_systeme(nb_scenes, mots_par_scene, total_mots)
    user_prompt = f"""Crée le script pour le sujet suivant :
- Thème : {sujet.get('Sujet', '')}
- Époque : {sujet.get('Époque', '')}
- Région : {sujet.get('Pays/Région', '')}
- Hook de départ obligatoire (à placer en scène 1) : {sujet.get('Hook', '')}"""

    print("🤖 Odysseus écrit le script sur mesure...")
    response = client.chat.completions.create(
        model="llama3.2",
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.65
    )
    
    contenu_brut = response.choices[0].message.content.strip()
    
    # 🔥 LE FIX : Nettoyage radical du contenu de l'IA
    # On cherche la première { et la dernière } pour ignorer le blabla autourgenerer_prompt_system
    debut_json = contenu_brut.find('{')
    fin_json = contenu_brut.rfind('}')
    
    if debut_json != -1 and fin_json != -1:
        contenu_propre = contenu_brut[debut_json:fin_json + 1]
    else:
        contenu_propre = contenu_brut # Au cas où il n'y a pas d'accolades du tout

    try:
        donnees_video = json.loads(contenu_propre)
        
        with open("script_output.json", "w", encoding="utf-8") as f:
            json.dump(donnees_video, f, indent=4, ensure_ascii=False)
            
        print("✅ Script généré avec succès et enregistré.")
        
        mettre_a_jour_statut(idx, "Publie")
        print(f"💾 Fichier CSV mis à jour (Ligne {sujet_id} passée à 'Publie').")
        
    except json.JSONDecodeError as e:
        print(f"❌ Erreur critique de lecture JSON : {e}")
        print("--- Contenu brut renvoyé par l'IA ---")
        print(contenu_brut)
        print("-------------------------------------")
        mettre_a_jour_statut(idx, "Erreur")

if __name__ == "__main__":
    executer_pipeline_generation()