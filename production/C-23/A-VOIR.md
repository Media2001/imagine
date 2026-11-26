# C-23 — Corrections V2, 26 novembre 2026

**NON PRÊT : le rejeu normal refuse le prérequis découverte livré, sans le forcer.**
L’ancien `PRET` est archivé dans `PRET-historique-V1.txt` et retiré. Aucune fuite hors mutation n’est établie par ce refus ; il ne constitue pas une matrice de livraison verte.

## Commandes et résultats V2

Depuis `C:/Users/Ced/imagine`, sous bash Windows :

```bash
PYTHONIOENCODING=utf-8 python -B wp/tests/demo/c23-tests.py
PYTHONIOENCODING=cp1252 PYTHONUTF8=0 python -B wp/tests/demo/c23-tests.py
PYTHONIOENCODING=utf-8 python -B wp/tests/demo/c23-mutations.py nouveau-b06-mutations-V2
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/c23-preparer.py --b06-seul --label nouveau-b06-V2
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/c23-preparer.py --label nouveau-rejeu-V2
PYTHONIOENCODING=utf-8 python -B wp/tests/demo/c23-verifier.py
```

Les noms de reçus sont immuables : choisir un nom nouveau, jamais réécrire les preuves ci-dessous. La commande GET reste `python -B wp/outils/demo/c23.py <nom>` avec son contexte privé sur stdin, jamais enregistré. Préparation/restauration et mutations ne sont pas prétendues lecture seule.

- **Tests : 28/28 dans chaque encodage**, Python réellement utilisé 3.11.15. Dernières preuves : `tests-finaux-final-V2.json`, `tests-utf8-final-V2.txt`, `tests-cp1252-final-V2.txt`.
- **B06 : 503 contrôles, zéro fuite, PASS, code 0**, `b06-livraison-finale-V2.json`, matrice complète `b06-livraison-finale-V2.md`. **35 voies (cinq pages × sept sorties), 14 publics** ; 490 cases plus 13 identités. Le coopérateur est un contrôle inverse, pas un refus. Cette recette **B06-only ne vaut pas livraison C23 complète**.
- **35 mutations des réponses HTTP natives B06**, une par voie : propre vert → témoin injecté en mémoire rouge (`leak=true`, `ok=false`) → octets d’origine restaurés verts. `b06-reponses-mutations-post-redirection-V2.json`, code 0, 35/35. Ce n’est pas une fuite injectée sur le site.
- **Mutation réelle séparée C23** : `python -B wp/outils/demo/c23-preparer.py --mutation --label mutation-finale-V2` a produit **1 922 contrôles, 177 fuites, FAIL**, code du détecteur 1 ; lanceur 0 parce que le rouge attendu et la restauration sont vérifiés. Les quatre contrôles inverses article/PDF/C08/achat passent. Le changement temporaire de politique découverte appartient exclusivement à cette mutation.
- **Dernier rejeu normal** `--label livraison-finale-V2` : **code 1**, `ETANCHEITE : 0 contrôles, 0 fuites — FAIL ; Prérequis découverte incompatible : politique livrée fermée ou sans numéro ; aucun réglage forcé`. Aucun cookie/session créé, aucun témoin B06 écrit dans ce refus.
- **Vérificateur** : JSON sur stdout, code 1 ; **36/39 contrôles vrais**, les trois rouges désignent uniquement ce prérequis, le code de livraison et la matrice vide. `verification-finale-V2.json`. Rejeu réel sans aucune écriture dans `production/` vérifié par inventaire avant/après : `verification-sans-ecriture-finale-V2.json`.
- **Image** : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1`, code 0, `T01 IMAGE READY`, preuve `image-preparation-V2.*`. Aucun paquet installé sur Windows.

## Ce qui manque pour redéposer PRET

Le réglage réellement livré est `ouverture=fermee`, `numeros=[]`. Un état de personnage ne peut pas rendre cette politique globalement fermée « épuisée » sans réécrire la politique. C23 ne la réécrit donc pas et ne prétend pas avoir préparé durablement un personnage compatible. La correction n°3 est appliquée sur son volet refus/préservation ; sa préparation durable reste bloquée sur ce prérequis. Ne pas utiliser `--mutation` pour obtenir une prétendue livraison normale verte.

Quand le lot propriétaire livre une politique découverte compatible, préparer durablement le seul personnage fictif selon cette politique, puis rejouer la livraison normale avec un nom neuf, en conservant les réglages. Aucun droit métier ni réglage d’ouverture n’a été choisi ici.

## B06 : preuve non vide et restauration

Les cinq pages étaient vides. **Cela n’a jamais été crédité comme une preuve d’absence de contenu réservé.** Le lanceur hors commande GET exige ces cinq corps vides, pose cinq témoins fictifs distincts `C23_COOP_TEMOIN_<ID>` sans changer date, identifiant, parent, statut ou métadonnée, puis vérifie la réception effective par `P-COOP` et l’absence pour les non-coopérateurs. Il restaure les lignes exactes et invalide les caches des seuls objets concernés ; toute dérive concurrente refuse la restauration plutôt que de l’écraser.

Sorties : HTML, REST unitaire, alias `rest_route`, collection incluse, oEmbed, embed, recherche. L’oEmbed autorisé prouve l’objet riche et le bon titre ; les six autres sorties prouvent aussi le témoin. Un flux forcé `post_type=page` retournait en réalité des articles, pas les pages B06 : il a été retiré des prétendues preuves B06 après un vrai rouge de non-vacuité. Les flux d’articles restent dans la matrice générale et recherchent aussi les témoins B06 quand celle-ci est exécutée. Aucun flux de pages non vide n’est prétendu prouvé.

`readback-final-post-redirection-V2.json` : état natif identique avant/après chacun des trois derniers rejeux, cinq pages 2867–2871 remises vides, attribut administratif de `P-COOP` conservé, profils et actions planifiées inchangés. Toutes les restaurations possèdent leur reçu distinct `*-restauration.json`.

## Corrections du détecteur

Les témoins sont cherchés dans **le corps brut complet décodé et la vue normalisée**, attributs/commentaires conservés. Cinq supports ont rougi avant correction (OG, Twitter, description, data-*, commentaire). Seules les positions natives exactes de réflexion du terme recherché sont masquées ; le reste du formulaire et la tête restent inspectés. Chaque corps 301/302/303/307/308 est retenu et inspecté, avec destination locale obligatoire et chaîne bornée. La régression 302→200 où seul le premier corps fuit passe ; destination extérieure refusée avant requête. La première régression exige une surface présente, `leak=true` et `ok=false`, et son inverse propre passe. Le SHA d’état est désormais dérivé du snapshot natif de chaque rejeu, jamais figé en dur.

Décisions et faux rouges conservés : `INCIDENTS.md`, `BLOQUE-V2.md`. Aucun code de paywall, plugin ou thème, aucun autre profil/site, aucun verrou, aucune file et aucun rapport parent modifiés. Cache d’hébergement et robots vérifiés demeurent hors de portée.

---

# Historique V1 — non opposable au code V2

Le texte ci-dessous est conservé pour traçabilité. Ses anciens noms, nombres, empreintes et commandes ne décrivent pas le rejeu V2. Copie indépendante : `A-VOIR-historique-V1.md`.

# C-23 — À voir : test d’étanchéité de livraison

**Cible unique : `imagine-test-demo`. Rien de réel, aucun autre site, aucun déploiement.**

## Rejouer

Depuis `C:/Users/Ced/imagine`, sous bash Windows :

```bash
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/c23-preparer.py --label livraison
PYTHONIOENCODING=utf-8 python -B wp/tests/demo/c23-tests.py
PYTHONIOENCODING=utf-8 python -B wp/tests/demo/c23-verifier.py
```

Le premier lanceur prépare les **sessions natives éphémères hors commande visiteur**, vérifie l’identité et les coupe-circuits existants, puis exécute en sous-processus cette **unique commande de test strictement GET** :

```bash
python -B wp/outils/demo/c23.py livraison
```

Le contexte (inventaire, cookies natifs et nonces REST) arrive par stdin privé, uniquement en mémoire. **Ne pas enregistrer ce stdin, ni le recopier dans un terminal ou un rapport.** Lancer directement `c23.py` sans ce contexte est un refus de prérequis, pas un autre mode de connexion. Le lanceur ne lit aucun mot de passe et n’utilise aucun POST HTTP. Il n’est pas lui-même prétendu lecture seule : sa préparation et sa restauration sont séparées de la commande testée.

Préparation bornée : reprise des réglages déjà inscrits dans l’état épuisé de `V-DEC-FIN` (quota de deux articles, périmètre existant), relecture fermée ; création de sessions natives pour les seuls personnages inspectés ; cookie local `tk_ai` fourni en mémoire pour éviter la création d’une métadonnée WooCommerce lors des refus administratifs. Puis, dans `finally`, restitution des lignes exactes de métadonnées et options initiales, identifiants de lignes/autoload compris, et relecture dans un autre processus. Aucun statut d’abonnement, calendrier ou action planifiée n’est modifié.

## Dernier résultat opposable

- `livraison.json`, `livraison.md`, `livraison.txt` : **1 432 contrôles, 0 fuite, PASS**, code de la commande **0**.
- **101 voies × 14 publics**, plus contrôles d’identité et contrôles inverses. Les contrôles supplémentaires ne sont pas présentés comme des cases de la matrice.
- `livraison-restauration.json` : absence de changement métier pendant les GET, métadonnées restaurées exactement, profils et actions planifiées identiques avant/après.
- `c09-readback.json` : recette C-09 existante, source distante identique à la source locale, **382 contrôles**, code **0**, aucun échec, état natif inchangé.
- `tests-finaux.json`, `tests-utf8.txt`, `tests-cp1252.txt` : **12 tests** dans chacun des deux environnements d’encodage, Python réellement utilisé **3.11.15**, deux codes **0**.
- `verification.json` : **25 contrôles de paquet**, aucun échec. Trois altérations de reçu dans une copie locale jetable sont refusées : total inventé, matrice vide, restauration déclarée fausse (`verifier-mutations.json`).
- `image-preparation.txt` et `.json` : `wp/tests/preparer-image.ps1` exécuté, code **0**, image T-01 vérifiée ; contexte temporaire créé puis nettoyé sous `production/C-23`, aucune installation sur Windows.

## Mutation réellement exécutée, puis restauration

```bash
PYTHONIOENCODING=utf-8 python -B wp/outils/demo/c23-preparer.py --mutation --label mutation-publics-complets
```

Cette commande de préparation **n’est pas** la commande visiteur : elle ouvre provisoirement le seul article fictif `42` par sa métadonnée éditoriale `imagine_reserve`, sans changer le code du paywall. La commande GET inchangée reçoit l’inventaire d’avant mutation : **1 432 contrôles, 177 fuites, FAIL**, code **1**. La case `article × anonyme` fuit réellement. Le lanceur de mutation revient à **0 uniquement parce qu’il vérifie ce rouge attendu et la restauration**. Lire `mutation-publics-complets.json` et `mutation-publics-complets-restauration.json` pour distinguer ces deux codes.

Le dernier rejeu `livraison` a été exécuté **après** cette restauration et repasse au vert. Les empreintes du détecteur et de ses sources sont contrôlées ; aucun reçu ne fige les fichiers de file, de doctrine, de documentation partagée ou d’un autre lot.

## Ce que la matrice dit — et ne dit pas

- Témoins déjà existants de C-08 conservés et inspectés. Le témoin principal commun est l’article fictif du T4 (`42`) : l’acheteur C-14 possède le T1, auquel appartient C-08. Assimiler son accès légitime à C-08 à une fuite aurait été faux.
- Les 22 articles réservés publiés et les cinq PDF fictifs sont inventoriés. Les témoins C-08, C-10, C-12 et B-00 sont recherchés dans toutes les réponses applicables ; absence de témoin dans un article inventorié = refus de prérequis.
- Le PDF T1 de l’acheteur est un **contrôle positif C-14**, pas une absence attendue. Son PDF T4 reste fermé. Le PDF de l’abonné actif est vérifié par sa phrase témoin **et son SHA-256 exact**.
- L’accueil montre cinq articles et ne contient pas l’article principal `42`. Le contrôle exige donc la présence réelle de C-08 dans une liste non vide. Archives et flux sont également inspectés sur un contenu réellement présent ; on ne valide pas une liste vide ou une mauvaise page.
- Les plans de site sont **désactivés nativement sur cette démonstration** : les quatre adresses doivent rendre 404. Cela prouve leur fermeture actuelle, pas leur contenu lorsqu’ils seront activés.
- Les refus administratifs, les pages partenaires et newsletters et l’espace compte sont lus ; aucun export, effacement, envoi, achat, upload ou action de gestion n’est déclenché.
- Le catalogue complet C-09 est rapproché de la situation native. Les neuf publics supplémentaires sans droit natif sont inclus, dont le coopérateur. `V-DEC`, dont la découverte est encore ouvrable, n’est pas consommé pour cette recette en lecture seule ; le cas découverte imposé par le brief est le vrai `V-DEC-FIN` épuisé. Les abonnés/équipe avec droit ne sont pas des refus attendus. Les liens offert/groupé manquants ne sont pas fabriqués.
- **Limites assumées du brief : cache d’hébergement partagé et robots réellement vérifiés non démontrables ici.** Le faux Googlebot, les faux en-têtes d’adresse et le faux Bingbot sont testés. Aucun DNS ni appel extérieur n’est lancé par cette recette.

Inventaire motivé de toutes les sorties depuis C-08 et des publics : `INVENTAIRE.md`, `inventaire-source.json`. Historique des problèmes rencontrés : `INCIDENTS.md`. Le rouge initial de diagnostic contenant une recherche réfléchie dans le titre n’est pas une fuite du site : les résultats et leurs identifiants sont désormais séparés du terme saisi, avec une régression et une contre-preuve où un résultat réellement fuyant reste détecté.

## Matrice du dernier rejeu

# Matrice C-23

Voie | anonyme | connecte-sans-abonnement | decouverte-epuisee | acheteur-autre-numero | faux-robot | profil-a-vir | profil-a-susp | profil-a-expire | profil-p-offrant | profil-p-offert | profil-p-gest | profil-p-benef | profil-p-pro | profil-p-coop
---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
article | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
accueil | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
numero | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
kiosque | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
thematique | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
archives | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
rest-contenu | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
rest-collection | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
rest-champs | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
rest-route | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
rest-embed | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
rest-recherche | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
rest-revisions | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
rest-edition | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
rss2 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
rss | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
atom | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
rdf | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
flux-article | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
oembed | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
embed | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
recherche | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
recherche-corps | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
rest-recherche-corps | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
rest-posts-corps | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
partage | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
extrait-automatique | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
c08-article | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
c12-epuisee | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
apercu | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
multipage | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
amp-inactif | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
prefetch | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
conditionnelle | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
sitemap | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
sitemap-articles | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
sitemap-numeros | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
sitemap-pdf | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-telechargement | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-direct | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-ancienne-source | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-piece-jointe | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-slug | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-media-rest | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-media-route | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-media-inclusion | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-medias-liste | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
partenaires | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
partenaire-49 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
partenaire-48 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
newsletters | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
mon-compte | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
admin-imagine-reglages | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
admin-imagine-liste-envoi | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
admin-imagine-echeances | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
admin-imagine-commandes | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
admin-imagine-justificatifs | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
admin-imagine-extractions | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
admin-imagine-tableau-de-bord | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
export-c21 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
effacement-c21 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
export-imagine_exporter_liste_envoi | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
export-imagine_extraire_abonnes | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-32-direct | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-32-source | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-32-attachment | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-32-REST | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-32-endpoint | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-25-direct | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-25-source | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-25-attachment | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-25-REST | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-25-endpoint | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-18-direct | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-18-source | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-18-attachment | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-18-REST | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-18-endpoint | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-11-direct | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-11-source | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-11-attachment | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-11-REST | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
pdf-inventorie-11-endpoint | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
article-inventorie-44 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
article-inventorie-43 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
article-inventorie-37 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
article-inventorie-36 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
article-inventorie-35 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
article-inventorie-30 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
article-inventorie-29 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
article-inventorie-28 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
article-inventorie-23 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
article-inventorie-22 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
article-inventorie-21 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
article-inventorie-16 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
article-inventorie-15 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
article-inventorie-14 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
article-inventorie-263 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
article-inventorie-234 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
article-inventorie-233 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK
article-inventorie-188 | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK

ETANCHEITE : 1432 contrôles, 0 fuites — PASS

