# Banc C05 — corrections de fusion

Python hôte ne fait que le transport Docker et la lecture des reçus. **Tout PHP, Composer, PHPUnit et WordPress s'exécute dans les conteneurs jetables possédés**, jamais sur Windows ou l'hôte WSL. Aucun Git, bootstrap partagé, staging existant ou compte réel.

## PHPUnit standard

`tests/Echeancier/PlanificateurTest.php` et `ReglagesAdministrationTest.php` sont découverts par la testsuite `Echeancier` du `phpunit.xml` racine. Le fichier autonome `tests/Echeancier/run.php` est supprimé ; les données fictives communes vivent dans `Fixture.php`, sans exécution de tests au chargement. Dans le conteneur autorisé :

```sh
composer test
composer test -- --testsuite Echeancier
composer lint
composer validate --strict --no-check-publish
```

Le standard exécute Numeros, Robots, Entreprise, Acces, Envoi **et Echeancier**. `corrections.py` réutilise le banc PHP/Composer des lots précédents sans les modifier : image synthétique existante, entrypoint sleep, label propre `org.imagine.c05-standard-runner`, sans montage, volume, port ou base/web. Préparation seule avec réseau pour les dépendances publiques verrouillées ; comparaison byte-à-byte du lock existant, aucun lock réécrit. Réseau déconnecté **avant** les tests. La source C04 nécessaire à Envoi est copiée en lecture seule dans le runner, sans modification de C04.

Chaque `run` recopie les sources finales, vérifie leurs empreintes dans le conteneur, supprime l'ancien JUnit, conserve le nouveau JUnit et les sorties réelles (y compris RED), puis exécute lint global, syntaxe et Composer strict. Aucun nom de reçu n'est écrasé.

## Vrai Subscriptions, e2e séparé

Le wrapper réutilise `run.py`, avec sortie et état redirigés vers le **nouveau paquet de preuves**. Image déjà présente `sha256:2fa44089da3ca9aeaba5da0b74bbb3e9e1592b14c07d114c6a635b5c814208f2`, sans pull ; paquet autorisé `/home/ced/staging-wp/plugins/woocommerce-subscriptions.zip`, empreinte contrôlée `ed8c529d1382e2d06fa6e605e799c9db5607d8459806c229e74a20571f871083`. Aucune licence activée, ZIP jamais exporté dans le dépôt.

Conteneur `imagine-c05-<aléatoire>`, label `org.imagine.c05-runner=true`, réseau `none` dès sa création, sans montage/volume/port ni privilèges, capacités supprimées. Sites entièrement inventés classique et HPOS, MariaDB sur socket Unix seulement, aucun HTTP/FPM, emails et HTTP sortants bloqués.

Quatre commandes fictives par stockage : 20 février et 9/10/11 avril 2027. Deux blocs de quatre numéros, huit positions par scénario. Dates futures lues dans `next_payment` et les actions natives ; **seule l'action possédée concernée** est exécutée explicitement en accéléré. Confirmations locales Woo à l'heure réelle du banc, sans manipulation d'horloge, passerelle ni opération bancaire. La fenêtre du 9 avril contient cinq dates acceptées par Option A ; les clôtures identiques rang 4/rang 1 sont refusées avant création de commandes.

Adaptateur admin appelé explicitement dans la fixture, jamais branché au bootstrap partagé. Formulaire et nonce WP réels, option sans REST, douze combinaisons persistées/relues par stockage. Le refus anonyme traverse le vrai `wp_die` avec filtre de traduction et handler terminal intercepté pour le test ; filtres retirés dans `finally`. Aucune sauvegarde HTTP ni validation visuelle revendiquée.

## Rejouer depuis C:/Users/Ced/imagine

Choisir **un nom de paquet neuf** ; `prepare` refuse un paquet déjà existant. Les fermetures vérifient positivement la propriété, suppriment seulement leur runner, puis exigent le diagnostic Docker « no such object ». Aucun prune ni intervention sur `.hermes.lock`.

```bash
export IMAGINE_C05_PACKET=rejeu-parent-unique
python -B wp/tests/echeancier-runner/corrections.py prepare && (
  python -B wp/tests/echeancier-runner/corrections.py run --name final
  result=$?
  python -B wp/tests/echeancier-runner/corrections.py close || result=1
  exit "$result"
) &&
python -B wp/tests/echeancier-runner/corrections.py e2e-prepare && (
  python -B wp/tests/echeancier-runner/corrections.py e2e --name final-e2e
  result=$?
  python -B wp/tests/echeancier-runner/corrections.py e2e-close || result=1
  exit "$result"
) &&
python -B wp/tests/echeancier-runner/corrections.py verify
unset IMAGINE_C05_PACKET
```

Vérification sans réexécuter PHP de la remise courante :

```bash
IMAGINE_C05_PACKET=fusion-22nov-1458 python -B wp/tests/echeancier-runner/corrections.py verify
```

Le vérificateur contrôle les six suites JUnit, les tests jonction/09-avril, les sources actuelles, les résultats classique/HPOS, les deux citations distinctes, l'inventaire/les empreintes C01/C04/C06/C07, le README partagé et le lock inchangés. Retirer seulement la ligne Echeancier du XML doit reconstruire exactement l'empreinte historique du XML C07. `verification.json` scelle aussi les notes C05 et le runner ; une revérification refuse tout écart sans écraser ce reçu.

Les reçus `production/C-05/preuves/`, `notes.md`, `reprise.md`, `verify.py` et les collecteurs antérieurs restent **historiques** ; l'ancien `verify.py` ne valide pas la migration PHPUnit. Remise actuelle : `production/C-05/corrections-22nov-1458.md` et `replays/fusion-22nov-1458/`. `citations.py` a complété les deux lacunes officielles dans `sources/review-fusion-22nov-1458.json`, sans archive de page ; ne pas réexécuter vers la même destination.

Q1 (marge du premier SEPA) reste à arbitrer : aucune nouvelle politique financière. Q2 a déjà son défaut explicite dans les arbitrages du 22/11. Aucun raccord admin ou encaisseur de production activé ; PRET n'est ni clôture par les relecteurs ni GO réel.
