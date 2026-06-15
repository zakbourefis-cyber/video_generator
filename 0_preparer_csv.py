import csv
import os

FICHIER_ENTREE = "50_Sujets_Viraux.csv"
FICHIER_SORTIE = "50_Sujets_Viraux_Prets.csv"

def estimer_duree(categorie, potentiel):
    """Assigne une durée selon la complexité du sujet"""
    cat = categorie.lower()
    if "mystère" in cat or "disparition" in cat or "légende" in cat:
        return 60 
    elif "bataille" in cat or "catastrophe" in cat or "empire" in cat:
        return 45 
    else:
        return 35 

def preparer_fichier():
    if not os.path.exists(FICHIER_ENTREE):
        print(f"❌ Erreur : Place bien ton fichier {FICHIER_ENTREE} dans ce dossier.")
        return

    # 🔥 FIX ENCODAGE : On tente d'abord UTF-8, puis on passe en plan B (Excel Windows)
    try:
        with open(FICHIER_ENTREE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            lignes = list(reader)
            champs_originaux = reader.fieldnames
    except UnicodeDecodeError:
        print("⚠️ Encodage Excel détecté. Basculement sur la lecture 'latin-1'...")
        with open(FICHIER_ENTREE, mode='r', encoding='latin-1') as f:
            # On force le délimiteur virgule au cas où
            reader = csv.DictReader(f, delimiter=',')
            lignes = list(reader)
            champs_originaux = reader.fieldnames

    if not champs_originaux:
        print("❌ Erreur : Le fichier CSV semble vide ou mal formaté.")
        return

    # On ajoute nos 3 colonnes techniques
    nouveaux_champs = champs_originaux + ["Statut", "Duree_Cible", "Id_Video"]

    for idx, ligne in enumerate(lignes):
        sujet = ligne.get('Sujet', f'video_sans_nom_{idx}')
        titre_propre = "".join(c for c in sujet if c.isalnum() or c == ' ').strip().replace(' ', '_').lower()
        id_video = f"{ligne.get('ID', idx)}_{titre_propre}"
        
        ligne["Statut"] = "En attente"
        ligne["Duree_Cible"] = estimer_duree(ligne.get('Catégorie', ''), str(ligne.get('Potentiel Viral (/10)', '8')))
        ligne["Id_Video"] = id_video

    # On force la sauvegarde en UTF-8 propre (avec le sigle utf-8-sig pour qu'Excel le lise bien après)
    with open(FICHIER_SORTIE, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=nouveaux_champs)
        writer.writeheader()
        writer.writerows(lignes)

    print(f"✅ Fichier prêt ! {len(lignes)} sujets ont été mis à jour avec leurs durées dynamiques.")
    print(f"👉 N'oublie pas de changer FICHIER_SUJETS = '{FICHIER_SORTIE}' dans 1_script_gen_auto.py !")

if __name__ == "__main__":
    preparer_fichier()