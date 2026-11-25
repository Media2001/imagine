# B-03 — Rapport du lot

**Fait** : mode lecture du thème, réglages locaux, reprise de position, durée serveur et progression ; aucun droit ni contenu de fixture modifié.
**Prêt à relire** : B-03, après vérification réelle et dépôt de `PRET` ; voir `A-VOIR.md` et `verification-finale.json`.
**À valider par Ced** : uniquement le visuel futur avec les valeurs du designer ; aucune question technique bloquante.
**Bloqué** : rien sur le fonctionnement demandé. L’inspection navigateur connecté n’est pas revendiquée : A-CARTE est testé en HTTP réel.
**Ensuite** : retour au parent, qui tient la file et le verrou ; aucun rapport V2 global écrit ici.

## Résultat

Thème seul : six fichiers ajoutés/modifiés, feuille dédiée activée par `html.imagine-reading`, JavaScript sans bibliothèque ni réseau (**5 756 octets**, gzip mesuré **1 851**). Bouton absent sans JS, vraie commande et état annoncé, sortie par Échap, fonds AA, largeur neutre `70ch`. Le corps passe toujours **une seule fois** par `imagine_article_body()` ; le HTML capturé après la décision C08 est réutilisé pour l’affichage et l’estimation (**200 mots/minute**, constante unique), sans lire le texte interdit pour en révéler la longueur. Les deux corps HTTP C08 sont comparés à l’avant-B03.

Tests réellement exécutés : **10 assertions PHP B03**, **5 tests JS**, **43 contrôles HTTP**, **14 tests locaux** (B01 adapté explicitement, corrections B01, portée C08 et contrat B03), **1 012 tests T01 / 34 006 assertions**, zéro échec courant ni ignoré ; **29 contrôles navigateur anonymes** (390 et 1440 px, reprise/Échap, trois palettes/tailles, sans JS). Le reçu final fait foi pour les nombres et les empreintes. Préparation obligatoire de l’image exécutée, script intact. Les contrôles PHP de bibliothèques passent par le même exécuteur canonique, dans un conteneur propre sans balayage des conteneurs d’autres workers.

## Décisions prises à défaut

- Réglages globaux au navigateur ; position et activation par article **et longueur de texte servi**, jamais par compte. Reprise proportionnelle, sortie mémorisée ; valeurs invalides ou stockage refusé : défauts prudents, lecture maintenue.
- Barre fixée en haut ; réglages simples dans le flux, hors `article`. Tous les blocs de droits restent présents, y compris si une décision complète porte un rappel ; seuls les appels périphériques disparaissent.
- Trois tailles neutres, « Grand » par défaut ; aucun choix de maquette, police distante ou bibliothèque. La signature et les contenus fictifs existants sont conservés, même incomplets.

## Écarts et incidents

L’ancien test B01 « aucun fichier JS » est logiquement dépassé par ce brief : résultat brut conservé, une seule assertion adaptée **en mémoire** vers une liste fermée dans le rejeu B03 ; aucun autre test/livre de lots modifié. Un premier contrôle navigateur trop bref en arrière-plan n’observait pas le rafraîchissement de progression ; vérification finale au premier plan réussie. Une capture a expiré, sans résultat fabriqué. Au premier lancement, Python global n’avait pas les parseurs HTML : réutilisation hors ligne des wheels B01 dans le scratch, sans installation globale.

**Périmètre respecté** : `wp/themes/imagine/`, seuls nouveaux tests B03 sous `wp/tests/demo/`, `production/B-03/`. Ni plugin partagé, file, verrou, outil de staging, autre lot ni fixture native modifiés/réensemencés. Site `imagine-test-demo` exclusivement ; aucun Git, email, paiement ou système réel. `PRET` n’est ni une clôture de relecture ni une validation visuelle.
