# Lot B-12 — Aucun appel sortant depuis le corps d'un contenu

**Voie** : 2. **Chantier** : B. **Délai** : deux heures. **Dépend de** : B-11 (vidéos, podcasts), B-00 (coupe-circuit de la démonstration). **Cahier des charges** : §3.14 (« vidéos externes intégrées »), §4.4 (cookies, consentement). Relis-les.

## Pourquoi

B-11 rend une vidéo comme un simple lien, sans rien charger chez un tiers. Mais sa garantie tient à une consigne : ne jamais coller l'adresse d'une vidéo dans le corps d'un article. Si un rédacteur le fait, WordPress interroge de lui-même le service de vidéo et intègre son lecteur, avec ses cookies, sans consentement. Une consigne s'oublie ; il faut un verrou.

## Ce qu'on veut

**Le standard d'abord.** Cinq lignes : par où WordPress intègre un contenu externe (adresse seule sur une ligne, bloc « Contenu embarqué », code court), à quels moments le serveur appelle le service (à l'affichage, à l'enregistrement, et par la route que l'éditeur utilise pour l'aperçu), et le point d'accroche natif qui permet de l'empêcher.

- Tant que l'outil de consentement n'est pas choisi, **aucune intégration externe n'est résolue**, quel que soit l'état du réglage de B-11 : une adresse de vidéo dans le corps s'affiche comme un lien ordinaire. Ni cadre, ni script, ni vignette, ni appel du serveur, à l'affichage comme à l'enregistrement, aperçu de l'éditeur compris.
- Les intégrations internes (un contenu du site lui-même) ne sont pas concernées : laisse-les comme elles sont, et dis ce que tu as constaté.
- **Rien n'est réécrit en base** : le verrou agit au rendu et à la résolution, le contenu saisi reste tel quel.
- Aucun réglage nouveau. Dis en trois lignes ce qu'il faudra lever le jour où le consentement existera.

Tu ne touches ni aux champs de B-11, ni au paywall.

## Preuve

Proportionnée. Un article d'essai dont le corps contient une adresse de vidéo seule sur une ligne, et un autre avec le bloc natif : zéro tentative sortante observée à l'affichage, à l'enregistrement et sur la route d'aperçu. **Le contrôle prouve d'abord qu'il peut échouer** : verrou retiré (mutation témoin), une tentative est observée, arrêtée avant transport par le coupe-circuit de B-00 ; verrou remis, aucune. Essais retirés, état rendu.

## Livrables

Le code, son test, cinq lignes dans le README de l'extension, `production/B-12/A-VOIR.md` (ce que Ced verra : un lien à la place d'un lecteur), `PRET`. Rapport court.
