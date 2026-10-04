# Recette — Élise Live Test 0.1.0-test.2

Statut : candidate GitHub, non publiée dans HACS, non installée. Cette fiche
décrit les actions proposées ; elle ne les autorise pas.

## Périmètre validé par Bruno

Matt 1.0.9 (`d4ad0e5`) comme socle vocal, avec sélection des API HA,
météo, GetHistory, mémoire et Investigator. Pas de modification du tampon,
du transport ou de la fermeture des tours. SDK identique à Matt :
`google-genai==2.21.0`, `msgpack==1.1.2`.

## État de départ vérifié le 4 octobre 2026

- HACS Élise Live Test installé : `8d0a253`.
- HACS pointe sur `main`, disponible : `003e810`. Cette mise à jour
  proposée par HACS n'est pas la candidate PR12 : ne pas l'utiliser pour
  cette recette tant que la publication de la candidate n'est pas vérifiée.
- Matt et Élise Live Test sont chargées ; Élise Live est désactivée.
- Matt utilise Gemini 3.8 Live avec transcription des réponses désactivée.
- Élise Live Test utilise le même modèle avec transcription activée.
- Registre Matt : conversation/stt/tts.gemini_live.
- Registre Élise Live Test : conversation/stt/tts.gemini_live_2.
- Le nom visible d'un pipeline ne prouve pas quelle intégration l'exécute.

## Proposition de mise à disposition — validation distincte requise

1. Valider la publication de PR12 dans le dépôt Test seulement, après CI verte.
2. Vérifier que HACS propose effectivement ce nouveau commit et la version
   0.1.0-test.2 avant tout téléchargement.
3. Conserver le commit de retour arrière `8d0a253` et le pipeline Matt
   fonctionnel ; une sauvegarde HA récente doit être identifiée.
4. Après accord explicite pour la recette HA : télécharger la candidate Test
   depuis HACS, puis un seul redémarrage.
5. Vérifier version chargée et journaux de dépendances. Les tests attestent
   le SDK du manifeste, pas la version réellement chargée dans HA.

## Réglages proposés pour une comparaison équivalente

Relever les options du Matt fonctionnel avant de toucher au Test ; conserver
sa clé, son prompt, sa voix, son modèle, ses réglages de recherche et
d'interruption. Ne pas recopier ni afficher les secrets dans les documents.

Dans Élise Live Test seulement, proposer de désactiver la transcription des
réponses pour reproduire le réglage Matt vérifié. Ce changement reste à valider
explicitement. Choisir ensemble les trois moteurs gemini_live_2 pour la
recette Test et vérifier le rattachement au registre. Ne pas créer une nouvelle
entrée d'intégration. Les API météo, mémoire et Investigator doivent être
sélectionnées avec leurs identifiants existants ; GetHistory est intégré.

## Ordre de recette

| Étape | Demande | Preuve attendue |
| --- | --- | --- |
| Voix courte | « Dis-moi bonjour » trois fois | Trois réponses audibles complètes ; trois tours terminés ; pas de boucle |
| Voix longue | Une réponse d'environ vingt secondes | Audio complet et conversation terminée normalement |
| Météo | « Donne-moi la météo complète pour aujourd'hui à Dammarie-les-Lys » | Outil appelé, résultat météo complet puis réponse cohérente ; noter les données absentes |
| Historique | « Quand le volet du salon a-t-il été fermé pour la dernière fois ? » | Résolution cover.volet_salon_2 et horaire local issus de l'historique |
| Mémoire | Rappeler un souvenir déjà validé | Appel mémoire et restitution fidèle, sans nouvelle écriture demandée |
| Investigator | Une question sur un événement existant | Appel d'Investigator et réponse fondée sur sa preuve |
| Commande réelle | Une lampe choisie par Bruno | Action et confirmation du même équipement ; cette commande exige son accord |

Commencer sur téléphone, puis Voice Preview. À chaque essai, noter heure locale,
moteurs, version, résultat et identifiant de tour si disponible. Ne pas tester
Réveil/Bonne nuit avant validation de ce palier vocal : leurs dépendances
métier et le délai Bonne nuit restent des suivis distincts.

## Arrêt et retour arrière

Au premier blocage, réponse coupée, équipement mal confirmé ou erreur outil :
arrêter la série et garder les journaux du tour. Revenir au pipeline Matt
fonctionnel selon le réglage de départ consigné, après validation de Bruno.
Ne pas ajouter de patch transport à chaud. Si un retrait du code Test est
nécessaire, utiliser le commit archivé `8d0a253` ; le retour de pipeline
ne requiert pas à lui seul un redémarrage. Tout redémarrage de restauration
reste une action distincte.

## Limites

La CI et les comparaisons de sources ne valident ni le cloud Gemini ni
la restitution sur Voice Preview. Le blocage synthétique avec transcription
activée reste documenté ; il ne prouve pas une panne du Matt utilisé par Bruno.
L'heure erronée et la météo abrégée restent des observations à vérifier.
