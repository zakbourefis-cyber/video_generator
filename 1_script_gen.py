import json
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1", 
    api_key="local-machine"
)

SYSTEM_PROMPT = """Tu es un réalisateur de documentaires captivants au format Short/TikTok. 
Tu dois obligatoirement répondre au format JSON strict, sans aucune phrase autour, sans balises ```json.

Contraintes d'écriture :
- Rédige un script complet qui dure entre 45 et 60 secondes (environ 140 à 160 mots au total).
- Le ton doit être mystérieux, dramatique et rythmé.
- Découpe l'histoire en exactement 5 scènes logiques.

L'objet JSON doit suivre exactement cette structure :
{
    "titre": "Le titre global du short",
    "scenes": [
        {
            "num_scene": 1,
            "texte_voix_off": "Texte de la première scène (environ 30 mots). Doit commencer par un énorme hook accrocheur.",
            "mot_cle_visuel": "Un SEUL mot-clé très précis en ANGLAIS pour décrire l'image (ex: 'ancient egyptian gold')"
        },
        {
            "num_scene": 2,
            "texte_voix_off": "Suite de l'histoire, transition fluide (environ 30 mots).",
            "mot_cle_visuel": "Un mot-clé précis en ANGLAIS (ex: 'archeologist digging dark')"
        },
        {
            "num_scene": 3,
            "texte_voix_off": "Montée en tension ou révélation d'un fait surprenant (environ 30 mots).",
            "mot_cle_visuel": "Un mot-clé précis en ANGLAIS (ex: 'secret library alchemy')"
        },
        {
            "num_scene": 4,
            "texte_voix_off": "Conséquence historique ou explication du mystère (environ 30 mots).",
            "mot_cle_visuel": "Un mot-clé précis en ANGLAIS (ex: 'golden crown medieval')"
        },
        {
            "num_scene": 5,
            "texte_voix_off": "Conclusion forte qui pousse à s'abonner ou à réfléchir (environ 20 mots).",
            "mot_cle_visuel": "Un mot-clé précis en ANGLAIS (ex: 'mysterious universe space')"
        }
    ]
}"""

USER_PROMPT = "Crée un Short fascinant sur un secret oublié de l'Empire Romain."

def generer_script_professionnel():
    print("🤖 Odysseus (Llama 3.2) écrit le script multi-scènes...")
    
    response = client.chat.completions.create(
        model="llama3.2",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT}
        ],
        temperature=0.7
    )
    
    contenu_brut = response.choices[0].message.content.strip()
    
    try:
        donnees_video = json.loads(contenu_brut)
        print("✅ Super ! Script de 5 scènes généré avec succès.")
        return donnees_video
    except json.JSONDecodeError:
        print("❌ Erreur de structure JSON. Contenu brut reçu :")
        print(contenu_brut)
        return None

if __name__ == "__main__":
    script = generer_script_professionnel()
    if script:
        with open("script_output.json", "w", encoding="utf-8") as f:
            json.dump(script, f, indent=4, ensure_ascii=False)
        print("💾 Sauvegardé dans 'script_output.json'. Ready pour la suite.")