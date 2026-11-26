# Vérification A-07 (2ᵉ et dernier tour)

Vérificateur : Claude, 26/11/2026. Lot : contrôle de l'exposition de l'outil de staging — livrable rédactionnel, lecture seule, **sans code ni test automatisé**.

Méthode : `git diff b2fc286b..HEAD` sur `production/A-07` (version relue le 20 novembre → version corrigée par Hermès le 26 novembre) et `git log` sur `wp/`. Contrôle instruction par instruction de `corrections/A-07.md` contre `production/A-07/exposition.md`. Pas de relecture complète refaite.

Seul `production/A-07/exposition.md` a changé sur le fond (plus `PRET` et `corrections-26nov.json` ajoutés). Aucune empreinte A-07 dans `wp/` : les correspondances trouvées (`wp/outils/bascule/repetition.md`, `wp/tests/staging-e2e/…`) sont le mot « exposition » et des hachés de preuves d'autres lots, sans lien avec A-07.

---

## 1. Instructions de `corrections/A-07.md` (§4)

| # | Instruction | État | Emplacement |
|---|---|---|---|
| 1 | Compléter l'inventaire des tunnels (Cloudflare/cloudflared, ngrok) : présence/activité ou « non vérifié » avec raison, périmètre Windows/WSL | **Appliquée** | `exposition.md:11-12` — deux lignes distinctes, « Présence : non vérifié ; activité : non vérifié », raison (« aucun résultat individuel conservé »), périmètre Windows/portables/WSL en colonne « Non vérifié » |
| 2 | Requalifier le résultat UPnP : séparer découverte/réponse et énumération ; si pas de réponse exploitable, « redirections non déterminées » + blocage | **Appliquée** | `exposition.md:10` — « Service découvert/répondant : non déterminé. Redirections non déterminées. » ; collection déclarée vide sans preuve de réponse exploitable ; blocage signalé (« commande complète non conservée, pas de nouvelle exécution ») |
| 3 | Étendre le test extérieur aux sites : ouverture manuelle d'un port de site publié (IPv4, IPv6 si dispo) ; autres ports non vérifiés un à un ; interdiction de balayage + avertissement sur l'échec | **Appliquée** | `exposition.md:29` — port de site relevé dans l'instantané Docker, répétition IPv6 entre crochets, « autres ports restent non vérifiés tant qu'ils ne sont pas contrôlés un à un », « sans balayage », « un délai/échec ne prouve pas une absence générale » |
| 4 | Rétablir la 4ᵉ colonne « Non vérifié » | **Appliquée** | `exposition.md:5` — tableau à 4 colonnes : Point vérifié / Résultat déclaré / Preuve historique-procédure / Non vérifié |
| 5 | Phrase-pivot du risque prioritaire (WSL miroir + autorisation publique 7000) en tête du constat | **Appliquée** | `exposition.md:3` — bloc gras « Surface prioritaire… » placé avant le tableau |
| 6 | Rendre la preuve pare-feu reproductible : commande exacte avec filtres et champs non sensibles | **Appliquée** | `exposition.md:18-25` — bloc PowerShell `Get-NetFirewallRule` + `Get-NetFirewallPortFilter`, filtre TCP/ports 7000 et 8081-8200, sélection Direction/Enabled/Action/Protocol/LocalPort/Profile (aucun champ sensible) |
| 7 | Préciser le caractère instantané de la liste des ports (allocation dynamique 8081-8200) | **Appliquée** | `exposition.md:7` — « à cet instant… Allocation dynamique dans 8081–8200 : cet instantané n'invalide pas la règle sur toute la plage » |

**7 / 7 appliquées.** L'en-tête en 3ᵉ formulation, que la fusion (§1) demandait de **conserver**, est bien conservé (`exposition.md:1`).

Nuance, non bloquante : les instructions 2 et 6 appellent « la commande exécutée et le statut observé » / une commande « rejouée ». Hermès n'a **rien ré-exécuté** (UPnP non rejoué, association pare-feu « proposée et non exécutée »). C'est conforme au mandat lecture seule du lot et explicitement déclaré ; ce n'est donc pas un écart, mais il faut lire le livrable comme un constat historique annoté, pas comme un contrôle réseau neuf.

## 2. Résultat des tests

A-07 **n'a aucun test automatisé** (lot documentaire, confirmé par la fusion et par l'absence de harnais dans `production/A-07`). Rien à relancer. Le mandat « tests du lot » est donc vide.

Contrôles internes au livrable (`corrections-26nov.json`) : `exit_code 0`, 7 contrôles de contenu à `true`. Ils sont **déclarés par Hermès, non rejoués** par un harnais indépendant. Point vérifiable par moi : l'empreinte `exposition_sha256` du JSON correspond bien au fichier livré — `sha256 = cecf4c8…62954b8`, identique. Le JSON décrit donc la version réellement présente.

## 3. Régressions ou modifications non demandées

Aucune régression.

- Le fichier a été entièrement reformaté, mais c'est la conséquence directe de l'ajout de la 4ᵉ colonne (instruction 4) ; aucun contenu du constat du 20 novembre n'a été perdu.
- En-tête daté enrichi (« constat du 20 novembre… corrections documentaires du 26 novembre ») : cohérent, trace la correction. Hors liste mais légitime.
- Seul défaut cosmétique : **pas de saut de ligne final** (`\ No newline at end of file`). Sans incidence.
- Le lot reste strictement lecture seule : aucune règle, service ou réglage réseau modifié ; aucune adresse publiée ; aucune attestation d'absence d'exposition — ce que le `PRET` redit explicitement.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les 7 instructions de la fusion sont appliquées et localisables, sans régression ni sortie du périmètre lecture seule. Il ne reste aucun problème de fond : les seuls « non vérifié » sont des limites assumées et documentées (pas des oublis), et les deux questions ouvertes de la fusion (§5 : rejouer soi-même les preuves ; faire des recommandations un lot d'action distinct) sont des arbitrages métier/réel qui relèvent de Ced, non des défauts du livrable.

Rappel : ce verdict clôt la vérification de code/étude ; ce n'est pas un GO au sens du §3 de la doctrine.
