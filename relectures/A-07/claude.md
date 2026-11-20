# Relecture A-07 — Contrôle de l'exposition de l'outil de staging (Claude, indépendant)

Date : 20/11/2026. Relecteur : Claude, indépendant. Je n'ai pas ouvert `codex.md`. Fusion non faite (consigne explicite de Ced).

Objet relu : `production/A-07/exposition.md`, `production/A-07/PRET`. Brief : `briefs/A-07-exposition-outil-staging.md`. Nature du lot : contrôle en lecture seule, livrable rédactionnel, sans code ni test automatisé.

## Portée de ma vérification

Je n'ai **pas** rejoué l'audit réseau moi-même. Deux raisons :
1. Mon mandat limite l'exécution aux « tests du lot » ; A-07 n'en a aucun (le brief ne prévoit pas de `composer test`).
2. Les commandes Windows (`Get-NetConnectionProfile`, `netsh …portproxy`, `Get-NetFirewallRule`) ont été refusées par le bac à sable local ; `docker` n'est pas dans le PATH Windows (il tourne côté WSL).

Ma relecture est donc **documentaire** : cohérence interne, couverture du brief, justesse du raisonnement, respect des contraintes de forme. Les sorties de commandes citées par Hermès sont **plausibles et non recontrôlées** par moi. C'est une limite réelle de cette relecture, à lever par Ced s'il veut une contre-mesure (voir « À arbitrer »).

## 1. Conformité

- **Couverture des 6 points du brief : complète.** Écoutes (ligne 5), passage WSL→LAN (ligne 6), pare-feu (ligne 7), box/UPnP (ligne 8), tunnels et accès distants (ligne 9), test extérieur (ligne 10). Chaque point porte une preuve en lecture seule. Rien d'ajouté hors périmètre.
- **Mandat « lecture seule » respecté.** `exposition.md` ligne 12 et `PRET` affirment « Aucun service ni réglage modifié ». Contrôle croisé du dépôt : les seuls fichiers `wp/` non suivis (`wp/outils/staging/policy.php`, modifs `lib.php`, `harness.py`) sont étiquetés A-01 (`policy.php` ligne 5 : « Liste négative A-01 »). Ils ne relèvent pas d'A-07. Le lot n'a donc rien touché au réseau ni au système. Conforme.
- **Forme — en-tête (ligne 1).** Le brief prescrivait deux formulations : « rien n'est joignable… d'après ce qui a pu être vérifié », ou la liste de ce qui l'est. Hermès écrit une 3ᵉ formule : « Aucun accès depuis Internet démontré ; l'absence d'exposition n'est pas établie, notamment en IPv6. » C'est un écart à la lettre du brief, mais c'est **plus honnête** que la formule imposée (il refuse d'affirmer une absence qu'il n'a pas prouvée). Je retiens l'interprétation, signalée de fait par la phrase. **Mineur, favorable.**
- **Forme — colonnes du tableau (ligne 3).** Le brief demande explicitement quatre éléments : point / résultat / preuve / **ce qui n'a pas pu être vérifié**. Le tableau n'a que 3 colonnes : le « non vérifié » est fondu dans « Résultat et limite ». L'information est présente mais non isolée, ce qui nuit à la lecture rapide des angles morts. Correction proposée : colonne distincte « Non vérifié ». **Mineur.**

## 2. Exactitude (raisonnement technique, non rejoué)

Déroulé à la main des points à risque, sur la logique énoncée :

- **Profil pare-feu « public » ≠ redirection Internet (ligne 7).** Correct : un profil Windows classe l'emplacement réseau, il n'ouvre pas la box. La nuance est juste et évite un faux positif.
- **WSL en mode miroir (ligne 6).** Correct et important : en miroir, un service qui écoute dans WSL est atteignable via la pile réseau de l'hôte Windows, donc soumis au pare-feu Windows et non à un `portproxy`. Cela explique logiquement pourquoi « aucune entrée portproxy » n'est pas une preuve d'absence d'exposition. Raisonnement cohérent.
- **UPnP à zéro redirection (ligne 8).** Correct : la collection vide ne prouve ni réponse de la box, ni absence de redirection manuelle, de DMZ ou d'ouverture IPv6. Caveat bien posé.
- **Tailscale sans Funnel, RDP actif (ligne 9).** Correct : Tailscale seul n'expose pas à Internet sans Funnel ; RDP activé est bien une surface d'accès distant. Les deux sont signalés avec la bonne portée.
- **IPv6 (lignes 1, 7, 10).** Bien vu, non demandé explicitement par le brief : en mode miroir, l'IPv6 est un chemin distinct et une IPv6 publique globale peut être routée sans NAT. L'angle mort est correctement érigé en limite.

**Point important (présentation, pas erreur).** La combinaison [WSL miroir + règle entrante autorisant 7000 sur profil **public**] est le risque local le plus concret : si la box route un jour le 7000 ou attribue une IPv6 publique, le tableau de bord (et son accès agent `/mcp`, même port) devient joignable sans mot de passe. Le rapport cite les deux faits séparément (lignes 6 et 7) mais ne les relie pas en une phrase-pivot. La recommandation 2 (ligne 12) y répond, mais le lien mériterait d'être la tête de gondole du constat. Correction proposée : une phrase reliant explicitement miroir + autorisation publique 7000 = surface prioritaire. **Important.**

## 3. Tests

- **Aucun test automatisé attendu ni lancé** : lot de contrôle rédactionnel, le brief ne prévoit pas `composer test`. Conforme à la nature du lot.
- La seule « vérification » possible est la ré-exécution des commandes de preuve. Je ne l'ai pas faite (voir « Portée »). Les preuves citées restent donc **affirmées, non recontrôlées**. Ce n'est pas un défaut d'Hermès ; c'est une limite de ma relecture à combler côté Ced.

## 4. Sécurité et données

- **Aucune donnée interdite dans le rapport.** Pas de mot de passe, pas d'adresse IP publique (ligne 10 : « l'adresse publique connue de la box », sans la citer), pas d'identifiant. Contrainte finale du brief respectée.
- **Aucun balayage externe lancé** (ligne 10) ; la vérification depuis l'extérieur est correctement déléguée à Ced, avec le bon protocole (4G, Wi-Fi/VPN/Tailscale coupés, HTTP, pas d'identifiant, variante IPv6 entre crochets). Prudent et conforme.
- **Sorties « filtrées »** (ligne 9, `tailscale … --json` filtré) : bonne hygiène, cohérente avec l'interdiction des secrets.

## 5. Doctrine

- « Standard d'abord » sans objet (pas de code). Mandat lecture seule tenu (§3 doctrine, « Staging »).
- Rien à reporter dans `docs/ecarts.md` : pas d'écart au cahier des charges, pas de contradiction interne, pas de blocage tiers.

## Compléments utiles (mineurs)

- **Instantané, pas état permanent (ligne 5).** Les ports de sites (8082…8097) sont alloués dynamiquement dans la plage 8081–8200 ; « 8081 n'écoute pas maintenant » n'invalide pas la règle pare-feu 8081–8200. À dire d'un mot pour éviter une lecture faussement rassurante. **Mineur.**
- **Test extérieur (ligne 10).** Ne couvre que le 7000. Suggérer à Ced de tester aussi un port de site publié (p. ex. 8082) pour couvrir la seconde famille de surfaces. **Mineur.**

## Verdict

**Conforme**, sous réserve des points ci-dessous. Rapport honnête, techniquement juste, contraintes de confidentialité tenues, mandat lecture seule respecté. Aucun point bloquant.

- **Bloquant** : aucun.
- **Important** :
  1. Relier explicitement [WSL miroir + autorisation pare-feu publique sur 7000] comme surface prioritaire, en tête du constat (§2).
- **Mineur** :
  1. Rétablir la 4ᵉ colonne « Non vérifié » demandée par le brief (§1).
  2. Signaler le caractère « instantané » de la liste des ports de sites (§Compléments).
  3. Étendre le test extérieur à un port de site, pas seulement 7000 (§Compléments).
  4. En-tête en 3ᵉ formulation : retenu car plus honnête, simplement noté (§1).

Ce verdict n'est pas un GO.

## À arbitrer par Ced (questions fermées)

1. Dois-je, dans une passe ultérieure, **rejouer moi-même** les commandes de preuve en lecture seule (approbation du bac à sable à accorder), ou te suffit-il de les relancer toi-même avec ce rapport ? (oui / non)
2. Veux-tu que les recommandations d'Hermès (restreindre l'écoute du 7000 à l'administration, authentifier tableau de bord et `/mcp`) deviennent un lot d'action distinct, ou restent-elles de simples priorités sans suite dans ce contrôle ? (lot / priorités seules)

---

Fusion avec `codex.md` : **non réalisée**, sur consigne explicite. `codex.md` n'a pas été ouvert.
