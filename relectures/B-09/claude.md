# Relecture B-09 — Les autres pages (FAQ, légales, contact)

Relecteur : Claude, indépendant. Brief : `briefs/B-09-autres-pages.md`. Cahier des charges : §3.14, §4.4.
Production relue : `wp/plugins/imagine-site/{Contact,ContactConfidentialite,AutresPages}.php`, `wp/outils/demo/b09-seed.php`, tests `wp/plugins/imagine-site/tests/ContactAdapterTest.php` et stubs, harnais `wp/tests/demo/b09-*.php`, `production/B-09/{NOTE,A-VOIR}.md`.

Ce verdict n'est pas un GO.

## 1. Conformité

Le lot fait ce que demande le brief, ni moins ni plus. Rattachement par point :

- **Le standard d'abord** : cinq pages WordPress natives, aucune table ni type « FAQ » ajouté. Justifié en cinq lignes dans `NOTE.md`. Conforme au §3.14 et à la doctrine « standard d'abord ».
- **FAQ** : `b09-seed.php:16-19,29` insère exactement quatre blocs Titre niveau 2 — Accès numérique, Abonnement, Facturation, Livraison — sans question/réponse. L'ajout rédactionnel passe par le bloc Détails natif, documenté sans code (`README.md:420`). Conforme.
- **Pages légales** : CGV, confidentialité, cookies créées vides. La confidentialité est **réellement** désignée : `b09-seed.php:50-53` écrit `wp_page_for_privacy_policy` puis relit `get_privacy_policy_url()`. Pas de bandeau cookies ajouté. Conforme au brief et au §4.4 (déclaration native).
- **Formulaire de contact** : nom, email, message, case de consentement non cochée (`Contact.php:116-119`). Même mécanique que « Proposer un sujet » de B-08, corrections comprises (voir §5 ci-dessous). Stockage privé, visible de la seule administration, déclaré à l'export/effacement natifs de C-21 (`ContactConfidentialite.php`). Conforme.
- **Menu de pied de page** : emplacement natif `imagine-footer` (`AutresPages.php:14-16`), menu `imagine-b09-footer`, création reprenable après interruption (marqueurs précoces `wp_create_nav_menu` / `wp_add_nav_menu_item`, `b09-seed.php:60-138`). Menu principal non réécrit. Conforme.
- **Règles « rien ne part » / non-énumération** : aucun `wp_mail`/`wp_remote_get` dans le chemin ; aucune recherche de compte (`Contact.php` n'interroge jamais `user`). Message identique quelle que soit l'adresse. Conforme au brief (« ne révèle pas si une adresse a un compte »).
- **Inventaire pour la voie 1** : type `imagine_contact`, cinq clés `imagine_contact_*`, registre `imagine-contacts` — documenté dans `NOTE.md:22-39`. Conforme à la demande d'écrire où le message est rangé.
- **Aucun texte inventé** : pages vides, aucun texte juridique ni FAQ, aucun style. Conforme.

Interprétations signalées par Hermès (acceptables) : succès du POST détecté par égalité de la chaîne de message (`Contact.php:88`) ; le brouillon natif `Privacy Policy` est conservé, seule la désignation bascule (`b09-seed.php:44-50`).

## 2. Exactitude métier — cas déroulés à la main

- **Cas FAQ (§3.14)** : visiteur ouvre la FAQ → quatre rubriques, aucune Q/R. Le seed insère quatre `h2`, contenu sinon vide. **Conforme.**
- **Cas contact + RGPD (§3.14 / §4.4)**, consentement non coché : `traiter()` vérifie nonce + champs → `enregistrer()` assainit, valide (`SujetRegles::valide`), insère en `private` avec métas, relit chaque méta puis renvoie vrai ; `recevoir()` redirige `?contact=enregistree`. Aucun email/HTTP. Récupérable par l'export, effaçable. **Conforme.** Deux adresses (avec et sans compte) donnent le même accusé — test `testFormulaire...PasEnumeration` l'affirme (`$a === $b`).
- **Cas limite — antislash (règle de la file)** : `C:\dossier\fichier` et antislash final. POST échappé par WP → `wp_unslash` une fois → `wp_slash($meta)` à l'écriture ; le stub `wp_insert_post` déséchappe la méta (`ContactWPStubs.php:59`). Relecture à l'identique au détail admin et à l'export. Test `testAntislash...` confirme. **Conforme.**
- **Cas limite — erreur d'écriture** : échec `wp_insert_post` ou méta non relue → « refusée », aucun post orphelin (`Contact.php:59-67`, test `testErreurs...`). **Conforme.**
- **Cas limite — panne de lecture DB pendant export/effacement** : `Contact::ids()` renvoie `null` (≠ collection vide) → `exporter()` renvoie `WP_Error`, `effacer()` renvoie `done=false`/retenu. Jamais de « effacé » faussement annoncé. Test `testPrivacyPagination...` le couvre. **Conforme au §4.4.**
- **Cas limite — pagination 101 messages + tiers** : tranches de 50/50/1, `done` au bon moment, message du tiers jamais présent, effacement ciblé laissant le tiers. **Conforme.**
- **Cas limite — étanchéité REST/recherche** : type `public=false`, `show_in_rest=false`, `exclude_from_search=true`, statut `private` (`Contact.php:34-42`). La mutation `b09-mutation-prive.php` inverse ces arguments et publie un témoin ; le témoin devient détectable, l'état normal non. **Conforme** à « un seul contrôle d'étanchéité avec sa mutation ».

## 3. Tests

- **Rejeu autorisé** (`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`, conteneur jetable sans réseau, dépôt en lecture seule) — dernière ligne :
  `REJEU : 1161 tests, 36282 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`
  Les six tests Contact sont inclus dans cette suite. **Au vert.**
- **Note hors B-09** : le même rejeu signale un échec de paquet voie 1 — `A-30 NATIVE_PACKET_INVALID` (ligne `PAQUETS : 10 vérifiés, 1 échecs`). Hors périmètre B-09 et sans lien avec ce code. À noter : cet état diffère de `NOTE.md` (qui citait A-26/A-27/A-30/A-31 rouges) ; l'environnement a évolué entre la production d'Hermès et ma relecture (rescellages de la voie 1). Le PRET B-09 ne certifie pas ces paquets, ce que la NOTE dit déjà honnêtement.
- **Couverture des cas limites** : bonne (énumération, antislash, erreurs d'écriture, panne DB, pagination, tiers, admin only, portée du raccord footer). Pas seulement le nominal.
- **Tests qui vérifient la règle, pas le code** : oui. Le harnais de mutation `b09-horslive.php` tue douze mutants (slash, consentement coché, mail, http, publish, rest, export vidé, effacement neutralisé, lecture, admin, raccord, nonce) — preuve que les tests mordent sur les vraies règles.
- **Non rejoué par moi** : les recettes sur la démonstration fictive vivante (structure 16, contact 31, readback) exigent le site `imagine-test-demo` et des conteneurs que je ne suis pas autorisé à lancer ici. J'ai lu leurs reçus (`structure-finale-verifiee.json`, `recette-finale.json`, `readback-final.json`) sans les réexécuter. Le brief n'imposait que le rejeu PHP, fait.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle : jeux fictifs, adresses `@example.org`. Conforme §3.
- Nonce vérifié (`Contact.php:75`), échappement systématique en sortie (`esc_html`/`esc_url`/`nl2br`), requête préparée `$wpdb->prepare` (`Contact.php:102`). Détail admin derrière `current_user_can('manage_options')` (`Contact.php:21-22`). Toutes les capacités du type exigent `manage_options`, création manuelle `do_not_allow`.
- Paywall / fuite de texte réservé : sans objet au sens article, mais l'étanchéité du message privé (REST, recherche, export WXR `can_export=false`) est contrôlée et mutée. Aucune voie ne laisse sortir le message.
- Rien ne part : observateur `b09-observer.php` + mutants mail/http confirment compteurs à zéro depuis le code B-09.

## 5. Doctrine

- **Standard d'abord** : respecté ; le sur-mesure se limite au stockage privé du contact et à sa déclaration aux outils natifs.
- **Conventions §5** : `declare(strict_types=1)`, espace `Imagine\Site`, préfixe `imagine_`, textes passés par `__()`, hooks seulement. Conforme.
- **Réemploi** : `SujetRegles` est partagé entre Sujet (B-08) et Contact. Bien. **Mais** `Contact.php` est une quasi-copie de `Sujet.php` et `ContactConfidentialite.php` une copie verbatim de `SujetConfidentialite.php` (seuls les noms changent). Voir « Décisions techniques » ci-dessous.

## Verdict

**Conforme.** Points classés :

- **Bloquant** : aucun.
- **Important** : aucun.
- **Mineur 1** (doctrine/maintenance) — `Contact.php`/`ContactConfidentialite.php` dupliquent presque intégralement `Sujet.php`/`SujetConfidentialite.php` de B-08. Une base ou un trait partagé éviterait que deux corrections futures divergent. Traité en décision technique ci-dessous.
- **Mineur 2** (robustesse) — `recevoir()` déduit le succès par comparaison de la chaîne de message traduite (`Contact.php:88`). Fonctionne, mais couple la logique à un libellé ; un booléen/énum renvoyé par `traiter()` serait plus sûr.

## Décisions techniques, défaut proposé

1. **Factorisation Contact/Sujet** (Mineur 1). *Défaut prudent proposé : garder en l'état pour ce lot.* Le brief impose explicitement « même mécanique que B-08 », B-08 est clos et ne doit pas être touché ici ; une factorisation croiserait deux lots. À arbitrer par Claude après coup : extraire une base commune lors d'un lot de refactorisation dédié, ou laisser. Hermès n'a pas à attendre.
2. **Succès renvoyé par `traiter()`** (Mineur 2). *Défaut prudent : laisser* ; à reprendre si un autre appelant réutilise `traiter()`.

## Pour Imagine

- Avant ouverture au public : décider de la rétention automatique et de l'anti-spam des messages de contact (la NOTE les signale absents). *Réglage par défaut prudent : aucune purge automatique, aucune ouverture publique du formulaire tant que la décision n'est pas prise.*

## À arbitrer par Ced (visuel / réel)

- Les textes juridiques (CGV, confidentialité, cookies) et les réponses de la FAQ viennent d'Imagine et de son conseil : confirmes-tu qu'ils restent hors de ce lot (pages volontairement vides) ? *Défaut : oui, squelette vide.*
- Validation visuelle du pied de page (placement des cinq liens, menu principal inchangé) et de l'apparence des pages vides : à faire sur captures, le code ne la tranche pas.

---

`codex.md` non ouvert (présent mais à lire seulement au moment de la fusion). Fusion non faite à ce stade, conformément à la consigne.
