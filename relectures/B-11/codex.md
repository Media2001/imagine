# Relecture indépendante Codex — B-11

Date : 27 novembre 2026. Référentiel : `relecteurs/AGENTS.md`, doctrine, grille, brief B-11, cahier des charges §3.1, §3.3, §3.14 et §4.4, décisions consignées. Lecture du code, des tests et des preuves locales ; aucun accès au site, à une base ou à un compte. Rapport Claude non consulté. Seul ce rapport est écrit.

## 1. Conformité

Les éléments fonctionnels demandés sont présents : champs distincts pour vidéo et podcast, liste fermée d’hôtes, liens HTML sans oEmbed, intégration désactivée par défaut et emplacement vide lorsqu’elle est activée, lecteur audio natif et silence fictif. Le thème conserve son squelette. README, note sur le standard, trois lignes sur le futur consentement, A-VOIR et PRET sont livrés.

Le raccord audio reprend le répertoire privé et les en-têtes de C-11, ainsi que `Paywall::decisionPdf()` de C-06. Le choix de réserver l’audio est déclaré dans les décisions pour Imagine. Les limites WAV, dépôt local et absence de prise en charge Range sont explicites. Aucun défaut fonctionnel certain relevé par lecture dans les trois nouvelles classes ; la preuve de réception reste à corriger ci-dessous.

## 2. Exactitude métier

Cas déroulés à la lecture, comparés aux résultats consignés dans les recettes, sans prétendre les avoir rejoués sur WordPress :

| Cas | Chemin du code et résultat |
|---|---|
| Anonyme, article réservé (§3.1 et §4.4) | `Medias.php:68` consulte la même décision que le texte et retourne une chaîne vide avant de lire les adresses. La recette conserve un témoin positif acheteur/abonné puis contrôle l’absence des deux liens pour les profils refusés. Conforme. |
| Acheteur du numéro 11 (§3.1, zone 2 ; §3.3) | `AudioNumero.php:69` autorise le lecteur selon C-06 ; `AudioNumero.php:98` réévalue cette décision lors du GET. La preuve consigne le WAV attendu pour ce numéro et un refus pour le numéro 39 non acheté. Conforme. |
| Abonné actif, ancien numéro fermé par le réglage PDF | L’article reste accessible selon la décision article, mais l’audio du 11 suit le refus PDF ; celui du 39 couvert est autorisé. Ce résultat est expliqué dans la note, sans ouverture d’un droit supplémentaire. Conforme au brief imposant C-06 inchangé. |

Les dates et échéances restent déléguées au moteur existant. Les entrées vidéo hors liste, sous-domaines, suffixes trompeurs, identifiants, ports et antislashs sont traitées dans les tests unitaires. Le service audio refuse les références mal formées, les numéros non publiés et les méthodes autres que GET/HEAD.

## 3. Tests

**Exécutions pendant cette relecture :**

- `python -B wp/tests/demo/b11-verifier.py` : **échec, code 1**, sur `sources_apres_derniere_ecriture`, ligne 23. Les deux contrôles précédents passent ; la suite du vérificateur n’est pas exécutée.
- Tentative du lanceur PHP `wp/tests/demo/b11-horslive.php` avec la commande Docker de `b11-local.py`, exécutée directement pour ne pas créer de journal : image existante uniquement, réseau coupé, dépôt monté en lecture seule. **Blocage avant PHPUnit : `Wsl/Service/E_ACCESSDENIED`, code 1.** Aucun exécutable PHP/Docker natif trouvé dans le PATH, ni PHPUnit dans le paquet local. Les quatre tests ne sont donc pas déclarés rejoués.
- Les commandes `--live`, runtime et recette navigateur ne sont pas exécutées : elles accèdent au site, voire le modifient, contrairement aux droits du relecteur. Aucune préparation d’image ni installation effectuée.

Les preuves historiques annoncent 4 tests/34 assertions, 23 contrôles natifs et 90 contrôles navigateur, avec deux mutations de gardes. Leurs empreintes correspondent à `reception.json`. Ce sont des résultats livrés, distincts des exécutions ci-dessus.

**T1 — important — `production/B-11/reception.json:15`. Réception désynchronisée du fichier commun.** L’empreinte enregistrée de `wp/plugins/imagine-site/imagine-site.php` commence par `d21ac8e9`, contre `084a8383` actuellement. Une comparaison en mémoire confirme que retirer uniquement le bloc C-28 restitue exactement l’empreinte attendue : aucune modification B-11 n’est ainsi démontrée, mais la commande de réception échoue effectivement. **Correction proposée :** produire une réception complémentaire après rejeu sur l’ensemble courant, conserver les reçus historiques et faire pointer le vérificateur et A-VOIR vers cette réception. Ne pas simplement remplacer l’empreinte sans nouvelle validation.

**T2 — important — `wp/outils/demo/b11-recette.py:79`. La sauvegarde valide est testée sans changement de valeur.** `edit()` ressaisit les constantes VIDEO/PODCAST déjà déposées par la fixture ; la relecture exige ensuite l’égalité avec `baseline_meta`. Un traitement qui ignore les écritures valides tout en refusant correctement les valeurs invalides satisfait donc ce contrôle. Le test natif utilise également ces mêmes adresses. **Correction proposée :** enregistrer des adresses fictives différentes de la préimage pour l’article et le numéro, les relire après rechargement et vérifier leur rendu ; exercer aussi l’effacement des champs. Restaurer ensuite la préimage. Une mutation supprimant la persistance doit faire échouer le contrôle.

**T3 — important — `wp/tests/demo/b11-observer.php:9`. La recette modifie le parcours qu’elle est censée valider.** L’en-tête envoyé par tous les contextes de recette force l’éditeur classique et réduit `allowed_options` à la seule option B-11. Le résultat ne démontre donc ni la sauvegarde dans l’éditeur effectivement livré ni le fonctionnement du formulaire complet de réglages. Cette limite est honnêtement déclarée, mais demeure une lacune de réception des champs et du réglage demandés. **Correction proposée :** ajouter une recette avec un observateur passif, sans ces deux substitutions, sur l’éditeur et le formulaire réellement livrés ; vérifier persistance, refus d’hôte, états OFF/ON, absence d’appel B-11 et conservation des autres réglages.

**T4 — important — `wp/outils/demo/b11-recette.py:89`. L’exception Gravatar n’est pas limitée à l’administration.** Le journal mélange administration et pages publiques, puis retire toutes les destinations `secure.gravatar.com` du contrôle. Une tentative Gravatar issue d’une page publique passerait donc le contrôle « zéro tiers » ; le contrôle final ne vérifie lui aussi que le nom d’hôte, pas la page d’origine. Cela ne prouve pas une fuite actuelle. **Correction proposée :** séparer les observations par page/contexte et phase, conserver l’exception documentée uniquement pour l’administration, et refuser toute tentative tierce publique. Un témoin Gravatar sur une page publique doit faire échouer cette assertion avant transport.

## 4. Sécurité et données

Les chemins examinés contrôlent la capacité `edit_post` et le nonce à l’enregistrement. Les sorties sont échappées ; les métadonnées sont protégées et non enregistrées pour REST. Les liens réservés sont filtrés côté serveur. L’audio n’est pas une pièce jointe publique : nom aléatoire, répertoire C-11, refus des liens symboliques, droits réévalués et en-têtes privés pour la réponse.

Aucun secret ni donnée réelle identifié dans les sources et preuves examinées. Les données sont explicitement fictives. L’écart historique de préférences administrateur est déclaré dans `NOTE.md:38` ; je ne considère pas l’état antérieur comme intégralement restauré. Les restaurations des recettes suivantes restent des preuves livrées, non des observations indépendantes sur le site.

## 5. Doctrine

Le standard est exposé avec références officielles dans la note ; aucun service externe n’a été consulté pendant cette relecture. Validation des URL en PHP pur, raccord WordPress séparé, `strict_types`, espace de noms Imagine, options/métadonnées préfixées et textes d’interface traduisibles : principes respectés dans le périmètre examiné. Aucun style nouveau ni règle d’accès dupliquée.

### Décisions techniques, défaut proposé

T1 à T4 sont techniques : défaut proposé, conserver le comportement fermé existant et compléter les preuves avec de nouveaux reçus, sans affaiblir les assertions ni altérer les historiques. Hermès peut appliquer ces corrections ; arbitrage technique ultérieur par Claude, sans question à Ced.

### Pour Imagine

Question métier déjà consignée : audio réservé aux ayants droit ou public. Défaut prudent maintenu : réservé selon la décision PDF C-06, conformément au brief ; aucune nouvelle règle d’accès proposée dans cette relecture.

## 6. Études (lots sans code)

Sans objet : lot avec code. Les références documentaires présentes ont été relevées, pas vérifiées en ligne.

## Verdict

**À corriger.**

- **Bloquant :** aucun défaut fonctionnel ou fuite démontré par cette relecture locale.
- **Important :** T1, réception périmée ; T2, persistance valide non prouvée ; T3, parcours éditorial modifié par le test ; T4, exception réseau trop large.
- **Mineur :** aucun point supplémentaire retenu.

Ce verdict n’est pas un GO. PHPUnit n’a pas pu démarrer dans cet environnement et la validation visuelle reste hors de cette relecture.
