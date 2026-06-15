import json
import csv
import os
from openai import OpenAI

# Configuration du client Odysseus local
client = OpenAI(
    base_url="http://localhost:11434/v1", 
    api_key="local-machine"
)

FICHIER_SUJETS = "50_Sujets_Viraux.csv"

def charger_prochain_sujet():
    """Lit le CSV et retourne la première ligne avec le statut 'En attente'"""
    if not os.path.exists(FICHIER_SUJETS):
        print(f"❌ Erreur : Le fichier {FICHIER_SUJETS} est introuvable.")
        return None, None

    lignes = []
    sujet_selectionne = None
    index_selectionne = -1

    with open(FICHIER_SUJETS, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        lignes = list(reader)

    # Recherche du premier sujet en attente
    for idx, ligne in enumerate(lignes):
        # Sécurité au cas où la colonne Statut n'existe pas encore
        statut = ligne.get("Statut", "En attente").strip()
        if statut == "En attente" or statut == "":
            sujet_selectionne = ligne
            index_selectionne = idx
            break

    return sujet_selectionne, index_selectionne

def mettre_a_jour_statut(index_ligne, nouveau_statut):
    """Met à jour le statut de la ligne traitée dans le CSV"""
    lignes = []
    with open(FICHIER_SUJETS, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        champs = reader.fieldnames
        lignes = list(reader)

    # Si les colonnes de contrôle n'existent pas, on s'assure qu'elles sont là
    if "Statut" not in champs: champs.append("Statut")
    if "Duree_Cible" not in champs: champs.append("Duree_Cible")
    if "Id_Video" not in champs: champs.append("Id_Video")

    lignes[index_ligne]["Statut"] = nouveau_statut

    with open(FICHIER_SUJETS, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=champs)
        writer.writeheader()
        writer.writerows(lignes)

def calculer_contraintes_video(duree_cible):
    """Calcule le nombre de mots et de scènes optimal selon la durée"""
    try:
        duree = int(duree_cible)
    except (ValueError, TypeError):
        duree = 45 # Durée par défaut si non renseignée

    total_mots = int(duree * 2.5) # 2.5 mots par seconde
    
    if duree <= 35:
        nb_scenes = 3
    elif duree <= 48:
        nb_scenes = 4
    else:
        nb_scenes = 5

    mots_par_scene = int(total_mots / nb_scenes)
    return duree, total_mots, nb_scenes, mots_par_scene

def generer_prompt_systeme(nb_scenes, mots_par_scene, total_mots):
    """Génère un prompt système dynamique adapté aux contraintes de temps"""
    return f"""Tu es un réalisateur de documentaires captivants au format Short/TikTok.
Tu dois obligatoirement répondre au format JSON strict, sans aucune phrase autour, sans balises ```json.

Contraintes strictes d'écriture :
- Rédige un script complet contenant un total global d'environ {total_mots} mots.
- Le ton doit être mystérieux, dramatique et rythmé.
- Découpe l'histoire en exactement {nb_scenes} scènes logiques.

L'objet JSON doit suivre exactement cette structure :
{{
    "titre": "Le titre global du short",
    "scenes": [
        {{
            "num_scene": 1,
            "texte_voix_off": "Texte de la scène (environ {mots_par_scene} mots). La scène 1 DOIT impérativement intégrer le Hook imposé.",
            "mot_cle_visuel": "Un SEUL mot-clé précis en ANGLAIS décrivant l'action (ex: 'ancient coins close up')"
        }}
    ]
}}
Génère ainsi les {nb_scenes} scènes dans le tableau 'scenes'."""

def executer_pipeline_generation():
    # 1. Sélection du sujet
    sujet, idx = charger_prochain_sujet()
    if not sujet:
        print("🎉 Tous les sujets du fichier Excel ont été traités !")
        return

    # Injection de valeurs par défaut si ton CSV initial ne les a pas encore
    duree_csv = sujet.get("Duree_Cible", "45") or "45"
    id_video = sujet.get("Id_Video", f"video_{sujet['ID']}") or f"video_{sujet['ID']}"
    
    # 2. Calcul des contraintes dynamiques
    duree, total_mots, nb_scenes, mots_par_scene = calculer_contraintes_video(duree_csv)
    
    print(f"🎬 Sujet trouvé : '{sujet['Sujet']}' (ID: {sujet['ID']})")
    print(f"⏱️ Configuration dynamique : {duree}s ciblées -> {nb_scenes} scènes, ~{total_mots} mots au total.")

    # 3. Préparation des messages pour Llama 3.2
    sys_prompt = generer_prompt_systeme(nb_scenes, mots_par_scene, total_mots)
    user_prompt = f"""Crée le script pour le sujet suivant :
- Thème : {sujet['Sujet']}
- Époque : {sujet['Époque']}
- Région : {sujet['Pays/Région']}
- Hook de départ obligatoire (à placer en scène 1) : {sujet['Hook']}"""

    # 4. Appel de l'IA locale via Odysseus
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
    
    try:
        donnees_video = json.loads(contenu_brut)
        
        # On sauvegarde le script sous le nom unique de la vidéo
        nom_fichier_sortie = "script_output.json"
        with open(nom_fichier_sortie, "w", encoding="utf-8") as f:
            json.dump(donnees_video, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Script généré avec succès et enregistré dans '{nom_fichier_sortie}'.")
        
        # 5. On valide la ligne dans le CSV
        mettre_a_jour_statut(idx, "Publie")
        print(f"💾 Fichier CSV mis à jour (Ligne {sujet['ID']} passée à 'Publie').")
        
    except json.JSONDecodeError:
        print("❌ L'IA a échoué à produire un JSON propre. Passage en statut Erreur.")
        mettre_a_jour_statut(idx, "Erreur")

if __name__ == "__main__":
    executer_pipeline_generation()