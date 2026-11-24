# Relecture indépendante Codex — C-12

Date : 24 novembre 2026. Références : doctrine, brief C-12, cahier des charges §3.9 et chapitre 7 auquel il renvoie, décisions consignées. Examen de `production/C-12`, du raccord WordPress, des profils et des tests concernés. Aucune consultation de l’autre relecture, aucun accès à un site, une base ou un compte. Seul ce rapport est écrit.

## 1. Conformité

Les livrables demandés sont présents : ouverture sur première lecture, vérification fictive explicitée, état attaché au compte, compteur, bloc d’épuisement, cinq réglages dans la section Accès, profils V-DEC/V-DEC-FIN, parcours A-VOIR et PRET. Le défaut fermé et le périmètre vide sont prudents. Les limites concernant les autres adresses email et le futur refus des adresses jetables sont déclarées. La distinction durée/nombre, les paramètres figés et la fermeture des relectures après épuisement sont documentées.

**R1 — important — Le raccord neutralise la sélection éditoriale des articles.**

- **Localisation :** `wp/plugins/imagine-site/Decouverte.php:204`, `$content['decouverte'] = true;`.
- **Problème :** tout article réservé d’un numéro sélectionné devient admissible, sans désignation éditoriale de cet article. Le §3.9 renvoie au chapitre 7 pour l’étendue ; son point 17 indique que « La rédaction désigne les articles ouverts en découverte. Le reste est réservé. » Le contrat C-06 conserve précisément ce second filtre : `production/C-06/notes.md:145` exige le marqueur éditorial, et `PerimetreDecouverte::prerequis()` refuse un contenu avec `decouverte=false`. C-12 écrase cette information au lieu de la raccorder. La liste de numéros de l’administration ne permet pas de maintenir fermé un article particulier d’un numéro ouvert. Cette interprétation élargissant les droits n’est ni réglable ni signalée comme telle.
- **Correction proposée :** raccorder une désignation éditoriale explicite par article, fermée en son absence, et la combiner avec la liste des numéros avant toute ouverture/consommation. Si une variante « tous les articles du numéro » est conservée pour arbitrage, l’isoler derrière un réglage explicite à défaut prudent. Ajouter un test avec deux articles réservés du même numéro, un seul désigné : le second doit rester en extrait et ne déclencher ni ouverture ni décompte.

## 2. Exactitude métier

Déroulés manuels du code, distincts d’une exécution PHP :

| Cas | Résultat attendu et résultat du code |
|---|---|
| Compte vérifié, aucun autre droit, quota de deux articles admissibles | Première lecture A : état créé, A enregistré, accès complet. Relecture A : liste inchangée. Lecture B : second crédit enregistré et texte livré. Lecture C : motif et bloc `decouverte_epuisee`, sans ajout. Conforme à la règle de consommation et au contrat C-06. |
| Découverte d’un jour débutant le 31/12/2026 à 12:00:00 UTC | À 11:59:59 UTC le 01/01/2027 : 86 399 secondes, accès complet. À 12:00:00 : 86 400 secondes, accès épuisé. `DureeDecouverte` compare les secondes écoulées ; le changement d’année ne renouvelle pas le droit. |
| Article non désigné, mais appartenant à un numéro autorisé, quota disponible | Attendu : hors périmètre éditorial, sans consommation. Le raccord force le marqueur à vrai, livre le texte et ajoute l’article. Écart R1. |

Autres contrôles par lecture : une date de sortie future ne déclenche pas d’ouverture ; une date éditoriale invalide ferme le paywall ; les PDF sont exclus de la découverte. Le calendrier des clôtures postales ne gouverne pas ce lot. Le même compte retrouve son état après changement de session ; augmenter le quota courant ne modifie pas son quota initial. Une option corrompue provoque un refus, sans réinitialisation. Le compare-and-swap impose une nouvelle évaluation du quota après conflit d’écriture.

## 3. Tests

**Exécutés localement le 24/11/2026 :**

- `python -B -m unittest discover -s wp/tests/demo -p test_c12_profiles.py -v` : **1 test réussi**.
- Suite `unittest discover` de `wp/tests/demo`, motif `test_*.py`, exécutée par `python -B -` avec les wheels existantes de `production/B-01/validation` ajoutées en lecture seule au chemin Python : **33 tests réussis**, dont le test C-12 précédent. Aucun téléchargement ni installation.

Ces 33 tests vérifient principalement les contrats locaux, les gardes des scripts et des éléments de structure. Le test propre à C-12 vérifie le catalogue et les raccords textuels des profils ; il n’exécute pas le compteur PHP.

**Non rejoués :** les 25 contrôles PHP C-12, les 75 contrôles HTTP C-12 et les 28 contrôles C-11 ciblés. Le runner `wp/outils/demo/c12.py` contacte la démonstration, téléverse des recettes, modifie son état et écrit `production/C-12/resultats.json`, y compris avec `--check-only`. Cela dépasse les droits du relecteur et l’écriture unique autorisée. Aucun exécutable `php` n’est disponible dans le PATH consulté. Les 161 contrôles verts consignés dans la production sont donc une preuve fournie par le producteur, dont seule la composante locale de 33 tests a été reproduite ici.

Les recettes lues couvrent notamment l’épuisement, les sessions répétées, la concurrence sur le dernier crédit, les voies REST/flux/aperçus, une erreur de persistance et une panne du journal. Elles ne couvrent pas le refus éditorial décrit en R1.

**R2 — mineur — Le test du contenu futur est masqué par un quota déjà épuisé.**

- **Localisation :** `wp/tests/demo/c12-runtime.php:56`, contrôle `futur_pas_de_credit`.
- **Problème :** ce contrôle intervient après consommation des deux crédits et vérifie seulement `complet=false`. Un refus causé par le quota satisfait donc le test ; celui-ci ne prouve ni le motif lié au contenu futur, ni l’absence d’ouverture prématurée pour un nouveau compte.
- **Correction proposée :** tester ce cas avec un compte sans état, puis avec un quota disponible ; vérifier le motif attendu et l’état inchangé, en plus du refus du texte.

## 4. Sécurité et données

Les requêtes de stockage utilisent des paramètres préparés ; le nom de table vient de WordPress. L’option par compte n’est pas autoloadée et les écritures concurrentes sont conditionnelles. Les réglages passent par la Settings API, la capacité administrative et le nonce natif ; les champs affichés sont échappés. Aucun secret ni donnée personnelle réelle relevé dans les fichiers examinés ; les fixtures de comptes utilisent des adresses fictives.

La découverte n’est activée que pour une lecture GET singulière admissible. Les gardes excluent notamment REST, flux, aperçus, robots reconnaissables et préchargements. Les en-têtes du paywall interdisent le cache partagé. Ces protections sont cohérentes à la lecture ; leur étanchéité HTTP n’est pas certifiée par cette relecture locale. **R1 demeure un écart de droit d’accès : un lecteur découverte peut recevoir le corps d’un article non désigné.**

## 5. Doctrine

Réutilisation effective du moteur C-06 et des droits natifs ; absence de copie du calcul durée/quota dans le raccord. Le README décrit le stockage, les réglages, les commandes et les limites. Les fichiers applicatifs examinés déclarent les types stricts, utilisent l’espace de noms `Imagine` et traduisent les textes d’interface. Les options sont préfixées. L’extension de C-10 par enveloppement du HTML est fragile, mais cette dépendance est annoncée.

**R3 — mineur — Signature multiligne non conforme à PSR-12.**

- **Localisation :** `wp/plugins/imagine-site/Decouverte.php:177`, déclaration de `decider()`.
- **Problème :** la liste d’arguments est répartie sur deux lignes avec plusieurs arguments par ligne et la parenthèse fermante sur la dernière ligne d’arguments, contrairement à la convention PSR-12 imposée par la doctrine §5.
- **Correction proposée :** formater la signature multiligne avec un argument par ligne et la fermeture selon PSR-12, sans changer son comportement.

## 6. Études (lots sans code)

Sans objet : lot de code. Les liens officiels fournis dans A-VOIR ont été relevés, sans consultation externe conformément au rôle. Leur présence ne constitue pas une vérification indépendante des capacités des extensions.

## Verdict

**À corriger.** Ce verdict n’est pas un GO.

- **Bloquant :** aucun point classé à ce niveau.
- **Important : R1**, rétablir le filtre éditorial par article avant l’ouverture et le décompte.
- **Mineur : R2**, rendre discriminant le test du contenu futur ; **R3**, corriger la signature PSR-12.

Après correction de R1, rejouer la recette PHP/HTTP dans un cadre autorisé, avec les deux articles du même numéro dont un seul est désigné pour la découverte.
