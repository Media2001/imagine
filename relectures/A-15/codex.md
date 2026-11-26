# Relecture indépendante Codex — A-15

Date : 26 novembre 2026. Références lues : `relecteurs/AGENTS.md`, doctrine, grille, brief A-15, cahier des charges §3.8 et décisions. Périmètre : `production/A-15/`, outil et tests A-15 dans `wp/`, dépendances A11/A12 et banc A02. Le rapport de Claude n'a pas été lu.

## 1. Conformité

Le script, les tests, les deux lignes du mode d'emploi, le paquet unique `preuves/final/` et `PRET` sont présents. Le registre chargé est bien `WC()->mailer()->get_emails()` ; les classes commerciales sont attribuées par réflexion. Aucun choix d'email à conserver, supprimer ou réécrire n'est effectué. La limite des services extérieurs figure explicitement dans le mode d'emploi.

Les interprétations sont annoncées : état natif `is_enabled()`, absence d'historique d'envoi, limites des filtres arbitraires et des transports inconnus, refus de l'éditeur bloc. En revanche, deux restrictions de l'inventaire produisent des faux négatifs sur des personnalisations ordinaires.

**I1 — important — `wp/outils/bascule/a15/Inventory.php:33` : variantes natives d'objet et de titre ignorées.** Le calcul ne consulte que `subject`, `heading`, puis trois clés fixes de contenu. Les autres champs pourtant retournés par `get_form_fields()` ne sont pas examinés. Un email dont seule une variante telle que `subject_full` ou `subject_partial` est personnalisée ressort donc avec `subject_customised=false` ; même problème pour les variantes de `heading`. Les emails de remboursement constituent notamment un cas à couvrir. Ce n'est pas une transformation arbitraire par filtre, mais un réglage natif entrant dans le brief. **Correction proposée :** prendre en charge les variantes natives déclarées par chaque classe, comparer chaque valeur à son propre défaut et agréger les résultats sans exporter les textes. Ajouter les cas variante seule modifiée, variante laissée au défaut et champ vide de repli, sur les deux magasins. Constat par lecture du calcul ; ces cas n'ont pas pu être exécutés dans cette relecture.

**I2 — important — `wp/outils/bascule/a15/Inventory.php:80` : les gabarits communs surchargés sont absents de l'inventaire.** Seuls `template_html` et `template_plain` sont résolus. Une surcharge du thème portant uniquement sur `woocommerce/emails/email-header.php` ou `email-footer.php` n'entre jamais dans cette boucle : les lignes restent « non surchargé » et le compteur reste à zéro en l'absence d'autre surcharge, alors que la présentation des emails est personnalisée. **Correction proposée :** inventorier également les gabarits communs natifs applicables, sans les rendre, les rattacher aux emails concernés et les compter une seule fois dans le résumé. Éprouver une surcharge commune seule et la priorité enfant/parent. Le test livré ne place qu'un gabarit principal ; il ne couvre pas ce cas.

## 2. Exactitude métier

Deux cas du périmètre §3.8/brief sont déroulés à la main et comparés aux sorties livrées, dans les deux magasins :

- **Email client désactivé et personnalisé :** `seed.php` désactive `customer_on_hold_order`, modifie son objet et son contenu additionnel ; le banc surcharge son gabarit principal. Le calcul donne client, désactivé, objet et contenu personnalisés, un fichier surchargé. Les JSON classic/HPOS portent ces valeurs sans les textes canaris. Cas conforme.
- **Notification administrative avec destinataire personnalisé :** `new_order` reçoit un destinataire fictif et un objet modifié. Le calcul donne administration, destinataire personnalisé, objet personnalisé. Les deux sorties concordent et ne contiennent pas l'adresse. Cas conforme.

Les comptes livrés sont cohérents : 43 emails déclarés, 12 actifs pour WooCommerce, 16 pour Subscriptions et 1 pour Memberships ; un gabarit distinct surchargé. Les sorties des passages répétés sont identiques. Les limites calendaires ne s'appliquent pas : ce lot ne calcule aucun déclenchement ni aucune échéance.

**M1 — mineur — `wp/outils/bascule/a15/Inventory.php:44` : une valeur de destinataire enregistrée est assimilée à une personnalisation.** Toute valeur non vide rend le booléen vrai, même lorsqu'elle égale exactement le destinataire administratif par défaut. Enregistrer les réglages sans changer ce champ suffit ainsi à produire un faux positif. **Correction proposée :** comparer en mémoire la destination configurée au défaut natif, avec normalisation des listes ; traiter séparément les ajouts CC/BCC. Tester défaut absent, défaut explicitement enregistré et destination différente, sans jamais restituer les adresses.

## 3. Tests

Exécutions effectuées pendant la relecture :

| Commande | Résultat |
|---|---|
| `python -B wp/tests/a15/verify.py production/A-15/preuves/final` | Code 0, 25 contrôles PASS |
| `python -B wp/tests/a15/test_contract.py` | Code 0, 2 tests OK |
| `python -B wp/tests/a15/run.py --output <dossier temporaire unique hors dépôt>` | Code 1, `DOCKER_IMAGE_FAILED:4294967295`, avant création du conteneur |

Le dernier échec empêche de revendiquer un rejeu indépendant des tests PHP et natifs. Aucun conteneur n'a été créé ; le lanceur confirme ses sources et dépendances inchangées. Les reçus temporaires de cette tentative sont hors dépôt. Aucun fichier de production ni de test n'a été modifié.

Le paquet livré contient 8 assertions PHP, 76 contrôles natifs et 7 contrôles du lanceur, tous déclarés PASS, ainsi qu'un contrôle PSR-12 sans erreur ni avertissement. Le vérificateur rejoué relie les sources A-15 présentes aux preuves livrées ; relire ces preuves ne constitue pas une nouvelle exécution native.

Les tests dépassent le nominal : appels effectifs à `wp_mail` et `WC_Email::send`, refus SQL avec compte privilégié, écritures de fichiers, HTTP, cron, rejouabilité, chemins interdits, drop-in, empreintes des 55 tables et des fichiers. Les cas I1, I2 et M1 restent absents. L'oracle de registre reprend les méthodes natives, ce qui vérifie bien la projection ; il ne démontre pas la couverture de toutes les personnalisations.

## 4. Sécurité et données

Aucune fuite observée dans le paquet contrôlé : adresse canari, objets, corps et identifiants de connexion sont absents des rapports. L'outil ne rend pas les emails. Les noms sont filtrés, les sorties créées sans écrasement avec permissions restrictives et les erreurs ordinaires remplacées par des codes.

Les gardes A11 et le confinement A12 sont réemployés. Le banc livré tente réellement les envois sous ces gardes et vérifie l'immuabilité des données ; cette preuve a été inspectée, mais n'a pas pu être reproduite ici en raison de l'échec Docker. Aucun accès à un site réel, à un compte ou à une API n'a été effectué. Nonces et paywall : sans objet pour ce complément CLI.

## 5. Doctrine

Réemploi du standard et des dépendances existantes, absence de modification d'extension tierce, espace de noms `Imagine`, typage strict et documentation d'usage : conformes sur le périmètre examiné. Les corrections proposées sont techniques et ne nécessitent aucun arbitrage métier ni action sur le réel. Aucun GO n'est demandé ou donné.

## 6. Études (lots sans code)

Sans objet : lot de code. Aucune vérification documentaire externe n'a été effectuée.

## Verdict

**À corriger.**

- **Bloquant :** aucun établi.
- **Important :** I1, variantes natives de personnalisation ignorées ; I2, surcharges des gabarits communs omises.
- **Mineur :** M1, destinataire par défaut enregistré déclaré personnalisé.

Le contrôle du paquet et les tests Python passent. Le rejeu natif indépendant demeure non réalisé après l'échec d'accès à l'image Docker. Ce verdict n'est pas un GO.
