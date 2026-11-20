# Banc PHP isolé — C-02

Depuis le dossier du projet `C:/Users/Ced/imagine`, avec Python et Docker WSL
existants (aucune installation hôte) :

```sh
python wp/tests/entreprise-runner/run.py prepare
python wp/tests/entreprise-runner/run.py run --name final
python wp/tests/entreprise-runner/regression_c04.py
python wp/tests/entreprise-runner/exemple.py
python wp/tests/entreprise-runner/run.py close
python wp/tests/entreprise-runner/check_artifacts.py
```

`prepare` copie la bibliothèque, vérifie le Composer téléchargé, installe les
seules dépendances de développement verrouillées dans un conteneur jetable et
compare le lock avec l’original sans l’écrire. Réseau de préparation uniquement
pour ces dépendances publiques : aucun registre ni requête métier. L’image
synthétique existante est utilisée avec l’entrypoint `sleep` : aucun démarrage
WordPress, base, site ou application. Aucun montage, port, privilège ou accès
aux autres conteneurs n’est donné. Réseau déconnecté avant les suites.

Le wrapper réutilise en lecture seule `numeros-runner/run.py`, avec ses propres
label, état et sortie `production/C-02/tests/`. Les filtres PHPUnit doivent être
des noms simples : `--filter NumeroEntrepriseTest`. Chaque passage conserve
les codes PHPUnit, PSR-12, syntaxe et validation Composer ; il supprime l’ancien
JUnit du conteneur avant de lancer PHPUnit et vérifie les empreintes copiées.
Ne réutiliser un nom de preuve déjà livré qu’à l’occasion d’une correction
explicitement autorisée ; les fichiers RED/GREEN historiques restent en place.

`regression_c04.py` copie le connecteur dans un autre dossier du runner C-02,
sans modifier les sources et preuves C-04 ; ses dépendances de test sont copiées
du runner avant régénération locale de l’autoload. C-01/C-03 sont rejoués par
`composer test` dans la bibliothèque pilotage.

`exemple.py` exécute l’exemple PHP du README final et garde la sortie réelle.
`close` supprime seulement le runner possédant le label C-02 après vérification
de son périmètre, puis relit son absence. Les noms de conteneurs C-01/C-03/C-04,
les sites existants et leurs volumes ne sont jamais touchés.

`check_artifacts.py` vérifie après fermeture les JUnit, les octets effectivement
testés, la préservation des 377 fichiers initiaux (sauf les deux ajouts partagés
exactement reconstructibles), l’absence de nouveau fichier chez les voisins,
la documentation finale et les marqueurs. Il construit un manifeste de livraison
propre C-02 et un reçu technique séparé ; il ne donne ni GO ni avis de relecteur.
