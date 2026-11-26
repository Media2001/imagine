# Relecture indépendante Codex — B-05

Date : 26 novembre 2026. Référentiel : `relecteurs/AGENTS.md`, doctrine, brief B-05 et cahier des charges §3.12, lignes 909–913. Aucun accès à la démonstration, à une base ou à un compte ; aucune lecture du rapport Claude.

## 1. Conformité

Le périmètre principal est respecté : désignation manuelle unique, absence de rotation, archive « Nos partenaires », fiche B-01 conservée, texte « Partenariat » et classe structurelle aux trois emplacements. Les deux captures sont présentes et ont été examinées ; la distinction graphique reste explicitement au designer. Aucun style supplémentaire n'est nécessaire pour ce lot en squelette.

L'option native et la réutilisation des gabarits sont documentées. Les requêtes d'articles explicites restent sur `post` ; le CPT partenaire est exclu de la recherche et le filtre traite aussi le type forcé dans les recherches et flux. La garantie sur **tous** les liens sortants présente toutefois le défaut R1.

## 2. Exactitude métier

Cas déroulés à la lecture du code, distincts d'une exécution WordPress :

- **Aucune désignation** : l'option absente vaut zéro ; `selection()` retourne `null` et le gabarit quitte avant d'émettre le bloc. Conforme au brief.
- **Remplacement d'un partenaire par l'autre** : un seul identifiant est enregistré ; le deuxième remplace le premier. Une saisie invalide conserve le choix valide précédent ; une valeur explicite zéro masque le bloc. Conforme au comportement documenté.
- **Dépublication du partenaire choisi** : le contrôle `post_status === 'publish'` échoue et masque le bloc. Aucun autre partenaire n'est choisi automatiquement. Conforme.

**R1 — Important — `wp/themes/imagine/functions.php:162`.** La détection des liens externes analyse directement l'attribut `href` avec `wp_parse_url()` et abandonne lorsque celui-ci ne fournit pas d'hôte. Or une ancre saisie en HTML avec `href=" https://example.org/partenaire"` reste un lien externe valide pour le navigateur : l'espace initial est ignoré lors de la résolution de l'URL. L'analyse PHP de cette chaîne brute ne fournit pas l'hôte attendu ; le lien échappe donc à l'ajout de `sponsored`. Même divergence avec `https:////example.org/partenaire`. Le filtre hérité de B-01 ne suffit ainsi pas à la garantie reprise par B-05.

Correction proposée : normaliser les URL HTTP(S) selon leur destination effective avant de décider qu'elles sont internes, ou traiter prudemment les formes ambiguës comme commerciales dans le seul contenu partenaire. Conserver les relations existantes et ajouter ces cas à la recette des pages rendues. La résolution externe des deux exemples a été vérifiée localement avec `new URL()` sous Node ; le chemin PHP est un constat de lecture, non une reproduction WordPress exécutée pendant cette relecture.

## 3. Tests

Vérifications locales exécutées sans écriture de fichiers :

- Fonction `receipts()` du vérificateur B-05 exécutée après extraction de ses seules fonctions de lecture, sans importer le transport ni appeler `live()` : réussite. Les reçus enregistrent **15/15**, **38/38** et **13/13** contrôles positifs ; le journal T01 rapporte **1 097 tests / 34 443 assertions**, sans échec, erreur ou test ignoré.
- Comparaison SHA-256 : les **10 sources/documents** de `source_sha256` et les **9 pièces** de `receipt_sha256` concordent avec `final.json`.
- Contrôle local du sélecteur de l'accueil : l'identifiant visé est bien sur le titre `h2`, sans lien descendant ; voir R2.

Ces résultats vérifient les preuves enregistrées, **pas un nouveau passage des parcours natifs**. Le lancement complet de `b05-verifier.py` est exclu : sa fonction `live()` accède au site et à sa base, contrairement aux droits du relecteur. Les recettes HTTP et administration modifient également l'état de la démonstration et écrivent des preuves. PHP n'est pas disponible dans le PATH Windows ; la tentative d'exécution PHP locale via WSL est refusée avec `Wsl/Service/E_ACCESSDENIED`. Aucun contournement ni installation n'a été effectué.

Limite supplémentaire de traçabilité : le fichier partagé `wp/plugins/imagine-site/imagine-site.php` ne correspond plus à l'empreinte de `native.source_readback` dans le reçu final. Les autres fichiers de code de cette liste correspondent. Sans comparaison à l'installation, les anciens résultats ne certifient donc pas l'intégralité de l'assemblage courant ; cet écart n'est pas attribué à B-05.

**R2 — Important — `wp/tests/demo/b05-http.py:61`.** Le sélecteur `#imagine-latest-posts a[rel~=sponsored]` cherche les liens à l'intérieur du titre de section. Dans le gabarit, la liste des articles est située après ce titre. Le compteur vaut donc zéro même si tous les liens de la liste deviennent sponsorisés : les deux contrôles `articles_accueil_non_sponsored_*` sont des faux positifs.

Correction proposée : cibler la section contenant ce titre, vérifier d'abord qu'elle contient les liens d'articles attendus, puis vérifier l'absence de `sponsored`. Vérifier également qu'aucun identifiant de partenaire ne figure dans cette liste. Une mutation ajoutant `sponsored` à un lien d'article doit faire échouer le contrôle. Le témoin sur la fiche article, correctement présent et testé à la ligne 79, ne couvre pas ce rendu de liste.

## 4. Sécurité et données

Les sources et preuves examinées utilisent des partenaires fictifs. Aucun secret identifié dans ce périmètre. La sauvegarde repose sur la Settings API et `options.php` ; le champ échappe titres et attributs et valide le type ainsi que le statut du contenu choisi. Les reçus couvrent les refus de nonce et de capacité, sans rejeu indépendant ici.

Le lot ne modifie pas la décision du paywall ni la sortie du corps des articles. Aucun contournement du paywall identifié dans les changements examinés. R1 concerne la qualification commerciale des liens, pas une autorisation d'accès.

## 5. Doctrine

Réemploi des mécanismes WordPress et du processeur HTML existant ; pas de dépendance supplémentaire ni de règle d'acceptation éditoriale inventée. Les ajouts PHP portent `strict_types`, un espace de noms `Imagine`, les préfixes attendus et les traductions françaises. Le contrat README et les deux captures sont fournis.

Les choix techniques sont documentés ; aucune question métier ou touchant au réel n'est nécessaire pour appliquer les corrections proposées. La validation visuelle demeure hors du verdict technique.

## 6. Études (lots sans code)

Sans objet : lot de code. Les références officielles sont consignées dans `production/B-05/natif-sources.json` ; aucune consultation externe effectuée pour cette relecture.

## Verdict

**À corriger.**

- **Bloquant** : aucun identifié.
- **Important** : R1, liens externes pouvant échapper à `sponsored` ; R2, contrôle de l'accueil qui passe sans examiner les liens d'articles.
- **Mineur** : aucun retenu.

Ce verdict n'est pas un GO. Les tests natifs et les contrôles des pages rendues restent à rejouer après correction dans leur environnement autorisé.
