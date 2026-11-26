# Relecture indépendante Codex — B-07

Date : 26 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine, brief B-07, cahier des charges §3.11 et §4.2, décisions et règle des liens sortants de B-05. Examen des sources et preuves locales uniquement ; aucun accès au site ni à une base. Le rapport de Claude n’a pas été lu.

## 1. Conformité

Le périmètre nominal est présent : trois types, événements futurs triés, passé séparé, inscription gratuite privée, administration et raccord aux outils de confidentialité. Aucun billet, paiement, quota, export de liste ou transport n’est ajouté par les classes Agenda. Les deux événements B-00 sont complétés et deux fixtures supplémentaires sont documentées. Le choix du raccord natif et le consentement facultatif sont explicités.

- **R1 — important — `wp/themes/imagine/single-imagine_evenement.php:21`.** Le corps d’un événement partenaire passe directement dans `the_content()`. Un lien saisi dans sa description, par exemple `<a href="https://example.org/programme">Programme</a>`, reste sans `sponsored` : le filtre B-05 existant ne traite que le CPT `imagine_partenaire`, pas `imagine_evenement`. Seul le bouton construit plus bas est protégé. Cela ne respecte pas la règle B-05, qui inclut les liens du texte. **Correction proposée :** réutiliser le traitement B-05 pour le contenu des seuls événements de type partenaire ; vérifier les liens du corps et le bouton, avec un contre-exemple sur une rencontre ordinaire.

- **R2 — important — `wp/plugins/imagine-site/Agenda.php:57`.** La description du JSON-LD provient du `post_content` brut dépouillé de ses balises, tandis que la fiche affiche le contenu rendu par WordPress. Un shortcode déjà disponible, tel que `[imagine_demo_calendrier]`, figure littéralement dans le JSON-LD alors que la fiche affiche son tableau ; un bloc dynamique présente le même risque. Le balisage ne correspond donc pas nécessairement aux champs affichés. **Correction proposée :** définir une projection commune du texte effectivement affiché et du texte balisé, sans exécuter deux fois les contenus dynamiques ; tester au moins un contenu transformé par WordPress.

## 2. Exactitude métier

Déroulés manuels du code, sans prétendre à une exécution WordPress :

1. **Rencontre gratuite future (§3.11).** Un visiteur fournit nom et email, consentement absent : `ouvert()` accepte, l’adresse est normalisée, le verrou est acquis, une inscription privée est créée avec consentement `0`. Un second envoi avec la casse différente retrouve la même ligne et renvoie le même succès. Aucun compte n’est recherché dans ce parcours.
2. **Date de début atteinte (§3.11).** À l’égalité exacte, la règle `debut > maintenant` refuse l’inscription. Le formulaire disparaît et un POST valide reste refusé. La seconde vérification après acquisition du verrou couvre le franchissement de cette borne pendant l’attente.
3. **Partenaire futur (§3.11).** Le bouton externe reçoit `sponsored noopener noreferrer`, aucun formulaire n’est rendu, le POST direct est refusé par le type. R1 concerne le chemin supplémentaire par la description.

Les dates impossibles ou incomplètes ferment l’inscription et excluent l’événement des groupes. Le tri par timestamp, puis identifiant, ne repose pas sur l’année courante.

- **R3 — mineur — `wp/themes/imagine/single-imagine_evenement.php:22`.** La branche « passé » précède celle du partenaire : dès son début, un événement partenaire perd son lien externe et son étiquette « Partenariat ». Le brief ferme les inscriptions des événements passés, sans demander de retirer leur destination externe. **Correction proposée :** conserver l’étiquette et le lien commercial dans la fiche archivée, indépendamment de la fermeture de l’inscription ; ajouter le cas « partenaire passé ».

## 3. Tests

Exécutions effectuées sans écriture de reçu :

| Commande | Résultat de cette relecture |
|---|---|
| `python production/B-07/verifier.py` | **PASS : 51 contrôles**, aucune divergence d’empreinte ni incohérence des reçus sélectionnés. |
| Commande Docker de `b07.py::rules`, exécutée directement sans son écriture de reçu | Arrêt avant PHP : **`Wsl/Service/E_ACCESSDENIED`**, code de sortie 1. |
| `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1` | Même refus d’accès WSL ; **0 test exécuté**, bilan du lanceur : 1 erreur d’environnement. |

Aucun PHP natif n’est disponible dans le PATH. L’image n’a pas été reconstruite. Les recettes HTTP, adaptateur et confidentialité n’ont pas été relancées : elles accèdent à la démonstration et à sa base et écrivent d’autres fichiers, contrairement aux droits du relecteur.

Les preuves livrées annoncent 14 contrôles de règles, 15 d’adaptateur, 8 de confidentialité, 83 de recette, 29 de non-régression articles, 10 de contrôle final et une suite générale de 1 128 tests / 35 565 assertions. Ce sont des **résultats du producteur dont l’intégrité locale a été vérifiée**, pas des résultats PHP reproduits ici.

La couverture nominale comprend borne temporelle, doublon, absence de formulaire et refus direct, droits administratifs, confidentialité et absence de transport observé. Elle ne couvre pas R1–R3. Le test de confidentialité vérifie seulement `done=false` lors de l’erreur, puis rejoue l’effacement ; il ne poursuit pas la pagination de l’export après rétablissement de la lecture. C’est précisément le scénario de R4. Ajouter ces régressions aux corrections, sans compter les mutations de réponses en mémoire comme des parcours applicatifs supplémentaires.

## 4. Sécurité et données

- **R4 — important — `wp/plugins/imagine-site/AgendaConfidentialite.php:25`.** Une erreur de lecture produit `['data' => [], 'done' => false]`, soit une page valide demandant la poursuite de la pagination, et non un échec d’export. Avec une seule inscription : erreur à la page 1 ; lecture rétablie à la page 2 ; `array_slice(..., 50, 50)` renvoie une liste vide et le calcul final annonce `done=true`. L’export peut ainsi terminer sans l’inscription conservée en base. **Correction proposée :** propager une erreur native `WP_Error` et adapter le type de retour, comme le fait déjà l’exporteur C-21, afin d’arrêter la génération et de permettre un rejeu sans sauter de page. Tester une panne transitoire suivie d’une reprise, ainsi qu’un export dépassant 50 inscriptions. Constat établi par lecture du chemin de pagination ; parcours natif non exécuté ici.

Les contrôles visibles sont cohérents : nonce et méthode POST, validation des champs, contrôle de publication, requêtes préparées, verrou libéré dans `finally`, accès administratif `manage_options`, CPT privé exclu du REST et de l’export de liste. Les sorties HTML et le JSON-LD sont échappés. Le stockage des données personnelles est décrit. Aucun secret ou contact réel n’a été identifié dans les fichiers du lot examinés. Le paywall des articles n’est pas modifié ; sa non-régression demeure attestée par les reçus livrés, sans reproduction locale.

## 5. Doctrine

Le standard gratuit a été étudié avant le choix documenté du raccord natif. Les règles d’ouverture et de normalisation sont isolées en PHP pur ; les adaptations WordPress restent distinctes. Les fichiers PHP applicatifs déclarent les types stricts et utilisent l’espace de noms Imagine. Aucun style nouveau n’a été ajouté aux gabarits examinés.

- **R5 — mineur — `wp/plugins/imagine-site/Agenda.php:175`.** `esc_html__($label, ...)` reçoit les libellés variables de `TYPES`. Les outils d’extraction des traductions ne peuvent pas en déduire les chaînes ; le même procédé est employé pour plusieurs libellés de champs. **Correction proposée :** déclarer les traductions à partir de chaînes littérales dans une méthode de présentation, puis échapper le résultat lors de l’affichage.

- **R6 — mineur — `wp/plugins/imagine-site/Agenda.php:98`.** Le bloc conditionnel et son `return` sont condensés sur une ligne, contrairement à PSR-12 imposé par la doctrine §5 ; ce style se répète dans les nouveaux adaptateurs. **Correction proposée :** appliquer PSR-12 aux fichiers PHP du lot et contrôler leur formatage, sans changement fonctionnel.

## 6. Études (lots sans code)

Lot avec code : rubrique non applicable comme étude autonome. La note `STANDARD.md` est néanmoins contrôlée contre ses copies locales des sources officielles : RSVP sur types personnalisés, indépendance d’Event Tickets, champs personnalisés de Plus, email de confirmation et JSON-LD de The Events Calendar y figurent. Les adresses et passages sont indiqués ; aucune consultation réseau n’a été faite. L’absence d’installation des extensions est annoncée explicitement, sans présenter leur capacité documentaire comme une preuve d’exécution.

## Verdict

**À corriger.** Ce verdict n’est pas un GO.

- **Bloquant :** aucun point classé dans cette catégorie.
- **Important :** R1 — liens commerciaux du corps non traités ; R2 — description structurée différente du rendu ; R4 — export pouvant terminer en omettant des inscriptions après une erreur transitoire.
- **Mineur :** R3 — lien du partenaire passé supprimé ; R5 — chaînes de traduction dynamiques ; R6 — formatage PSR-12.

Les corrections proposées sont techniques et ne nécessitent pas de question à Ced. Le refus d’accès WSL limite la vérification indépendante ; il ne constitue pas un échec fonctionnel démontré du lot. La validation visuelle reste distincte de cette relecture.
