# B-03 — Valeurs à fixer par le designer

Aucune direction graphique nouvelle n’est proposée. Les valeurs ci-dessous sont des défauts de fonctionnement dans `wp/themes/imagine/assets/tokens.css` ; l’interface reste celle du squelette B01.

- **Largeur de lecture** : `--imagine-reading-column`, actuellement `70ch` ; conserver la plage de 65 à 75 signes, sous réserve de la largeur disponible sur mobile.
- **Tailles de texte** : `--imagine-reading-size-normal`, `--imagine-reading-size-large`, `--imagine-reading-size-larger` (`1.125rem`, `1.25rem`, `1.5rem`), avec Grand par défaut ; conserver l’agrandissement utilisateur.
- **Interligne** : `--imagine-reading-leading` (`1.8`). Police et titres réutilisent les variables B01 `--imagine-font`, `--imagine-h1`, `--imagine-h2`, `--imagine-h3`.
- **Clair** : `--imagine-reading-light-paper` / `--imagine-reading-light-ink` (`#ffffff` / `#000000`).
- **Sépia** : `--imagine-reading-sepia-paper` / `--imagine-reading-sepia-ink` (`#f4ecd8` / `#241c14`).
- **Sombre** : `--imagine-reading-dark-paper` / `--imagine-reading-dark-ink` (`#171717` / `#f3f3f3`).
- **Espacements, focus et barre** : variables B01 `--imagine-space`, `--imagine-small-space`, `--imagine-focus` ; couche technique `--imagine-reading-progress-layer` (`1`). La barre reste fixée en haut, sans animation ni masquage des contrôles de droits.

Les trois couples texte/fond sont testés à au moins **4,5:1** ; toute nouvelle palette doit repasser ce test et une inspection des contrôles/états de focus. Aucun logo, police distante, icône, recadrage ou animation n’a été ajouté. Les figures et leurs légendes viennent toujours du HTML autorisé d’origine, sans réécriture des contenus.
