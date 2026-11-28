# C-32 — corrections locales ; réception démo encore à produire

**PRET retiré.** Cette reprise n’a lancé aucun navigateur ni accès/mutation du site démo, aucune préparation d’image et aucun rejeu global. Les anciens `*-final-V2`, `reception-V2.json`, `image-V2` et `replay-V2` restent historiques : ils ne valident pas le code corrigé. Le parent tient le verrou et arbitre le créneau après C31 ; aucun verrou touché.

## Ce que Ced regardera après installation par le parent

Ouvrir en navigation privée : http://192.168.129.32:8085/gestion-des-cookies/ . Une table de quatorze lignes, sous le texte éditorial B09 demeuré vide : nom/motif, producteur, geste, durée et usage. Aucun texte juridique, bandeau, consentement ou script livré. Le geste de session WooCommerce n’annonce plus la connexion.

L’ancien relevé trouvait sept cookies natifs `sbjs_…` en simple lecture, par JavaScript. **Ils restent activés** ; le code ne change aucun réglage d’attribution. Le réglage natif qui les éteindrait reste décrit au README pour Imagine et son conseil, pas appliqué. La nouvelle recette calcule deux verdicts : inventaire autorisé et zéro-cookie strict. Le FAIL strict ne devient jamais une réussite par exclusion silencieuse : il figure dans `checks` et `--strict` rend son processus rouge. L’inventaire peut réussir avec les seuls sept noms `sbjs_…` exacts, jamais avec une session, un panier ou un huitième nom, même déjà listé.

Le parcours reprend les URL de C26 **par identité**, y compris ses dix pages coopérative/soutien/sujet et quatre fiches événement, sans toucher sa matrice. Deux sondes hors liste HTTP/JavaScript sont retirées en nettoyage. Les sessions étrangères ne sont jamais supprimées : apparition/modification/disparition concurrente est signalée et empêche le verdict de restauration réussie. Les préimages privées ne sont pas dans le dépôt.

## Tests locaux effectivement exécutables sans site

Depuis `C:/Users/Ced/imagine`, avec une étiquette neuve pour ne pas écraser les reçus :
```bash
python -B production/C-32/test-local.py corrections-local-final-V2
python -B production/C-32/verifier.py --local
```
Le premier lance seulement les tests purs C32, le contrôle syntaxique Python et PHPUnit C32/PHP dans l’image locale préexistante, conteneur jetable sans réseau, wp monté en lecture seule. Aucune construction d’image, aucun banc partagé modifié. Le reçu local contient les commandes exactes, codes retour, logs et empreintes après les dernières écritures. Les sources officielles ont été vérifiées séparément par téléchargement de documentation publique, sans accès démo (`official-corrections-V2.json`).

## Recettes du parent — NE PAS lancer en parallèle de C31

Les étiquettes ci-dessous sont réservées à la réception corrigée ; si l’une existe déjà, utiliser un jeu entièrement neuf et adapter les constantes de `reception_c32.py` **puis refaire le reçu local**. Ne jamais réécrire une preuve. Les corrections ne changent que `Cookies.php` côté fonctionnel ; l’amorçage partagé est vérifié par son seul contrat.

```bash
# Installation bornée, ancien Cookies.php autorisé par le reçu historique exact.
python -B -c "import sys,json; sys.dont_write_bytecode=True; sys.path.insert(0,'wp/outils/demo'); import c32; old=json.loads((c32.OUT/'reception-V2.json').read_text(encoding='utf-8')); c32.PREIMAGES={c32.FILES[0]:old['sources']['wp/'+c32.FILES[0]]}; c32.b13.install(c32,'installation-corrections-V2')"
python -B wp/outils/demo/c32.py native native-corrections-V2
python -B wp/outils/demo/c32-browser.py browser-corrections-V2 --strict
# Lire browser-corrections-V2.json avant de continuer : inventaire PASS requis.
# Le code retour strict peut être 1 UNIQUEMENT si strict_zero_cookie=FAIL
# et inventory=PASS, sans erreur/restauration manquée. Ne pas relancer pour le verdir.
python -B wp/outils/demo/c32-standard.py standard-corrections-V2
python -B wp/outils/demo/c32.py image image-corrections-V2
python -B wp/outils/demo/c32.py replay replay-corrections-V2
python -B production/C-32/finaliser.py --live
python -B production/C-32/verifier.py --live
# Contrôle distinct, rouge si un cookie subsiste, sans mutation :
python -B production/C-32/verifier.py --strict
```

Le finaliseur recalcule le verdict strict depuis les observations, contrôle la couverture et les sessions, vérifie le contrat/readback démo **avant** de déposer `reception-corrections-V2.json` et `PRET`. Les totaux PHPUnit/assertions proviennent du `T01_RESULT` courant ; aucune copie de l’ancien 1220 ou du 1229 relu. L’instruction 7 reste au parent : produire le rejeu frais, archivé sous le nom corrigé pour préserver `replay-V2.json`. Sans ces gates : **local seulement, pas prêt live**. Après réception, le README peut encore être lu comme compte rendu de ce worker local : ses sources scellées ne sont pas modifiées pour raconter la validation parent.

