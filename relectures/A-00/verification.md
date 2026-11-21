# A-00 — Vérification (2ᵉ et dernier tour)

**Lot :** A-00 — Étude de couverture des extensions (sans code).
**Date :** 21 novembre 2026.
**Rôle :** vérificateur. Je contrôle que les instructions de `corrections/A-00.md` ont été appliquées par Hermès après la fusion, je relance les tests, je relève régressions et ajouts non demandés. Ce n'est pas une relecture complète.
**Base de comparaison :** état relu du 20/11 (commit `1bb52d4`) → `HEAD`. `git diff` sur `production/A-00` et `wp/`. Tests relancés localement.

---

## 1. Instructions de `corrections/A-00.md` — état

| # | Instruction | État | Fichier : ligne |
|---|---|---|---|
| 1 | Besoin 3 — signaler la divergence brief / §3.6 (carte → carte au cahier ; carte → SEPA = extension du brief, non arbitrée) | **Appliquée** | `couverture-extensions.md:102` (« Divergence brief / cahier (§3.6) »), ligne de synthèse `:35`, arbitrage Q2 `:374` |
| 2 | Besoin 5 — fournir les cellules exactes avec en-têtes pour Subscriptions/Vaulting, **ou** classer en doute | **Appliquée (par le repli)** | `couverture-extensions.md:36` (ligne « doute, cellules probantes absentes ») et `:132` (« Doute documentaire »). `registre-citations.json:3-8` (bloc `qualification_21nov`, `collecte_nouvelle:false`). Les cellules n'ont pas été produites : l'instruction autorisait explicitement le repli « classer en doute », qui a été choisi. |
| 3 | Besoin 12 — ajouter l'extrait d'octroi **ou** reclasser « attribution via inscription gratuite » en doute ; conserver la durée | **Appliquée (par le repli)** | `couverture-extensions.md:220` (« Attribution via inscription gratuite : doute », durée native conservée). `registre-citations.json` bloc `sources_21_24`. |
| 4 | Besoins 4/6/15 — note d'articulation §3.6 (retrait au 1ᵉʳ rejet) vs §3.8 (grâce), sans choisir la priorité | **Appliquée** | Note : `couverture-extensions.md:112`. Renvois : `:148` (besoin 6) et `:271` (besoin 15). La priorité est explicitement laissée à Ced. |
| 5 | Besoin 13 (robots) — remplacer « interdit par la doctrine » par le renvoi au §4.4 | **Appliquée** | `couverture-extensions.md:244` (« user-agent seul insuffisant selon le §4.4 »). Ancienne formule supprimée (vérifié par test). |
| 6 | Besoin 2 — rappeler « quatre numéros par année d'engagement » (§3.5) près du contre-exemple et dans l'arbitrage n°1 | **Appliquée** | Garde-fou : `couverture-extensions.md:92`. Arbitrage Q1 : `:372`. |
| 7 | Registre des écarts — consigner dans `docs/ecarts.md`, datés 20/11 : (a) carte→SEPA, (b) emails Stripe §3.8, (c) besoin 2 §3.5 | **Appliquée — par le tenant du registre, pas par Hermès** | `docs/ecarts.md:11-13` (les trois lignes, datées 20/11/2026). Conforme au dispositif : la fusion précisait que Hermès n'a pas les droits sur `docs/` ; il a correctement différé (`notes.md`) et le tenant a porté l'action (commit `54608e7`). |
| 8 | Ne pas réécrire le fond correct ; corriger preuves et signalement d'écarts | **Appliquée** | Conclusions justes conservées (besoin 7, §3.5, standard d'abord). Aucune réécriture de fond constatée. Déclaré dans `notes.md`. |

**Bilan :** 8/8 appliquées. Aucune non appliquée. La seule « partialité » apparente (instr. 2 et 3) est le repli « classer en doute » que les instructions autorisaient nommément ; ce n'est pas un défaut d'application.

---

## 2. Résultat des tests

- **Suite documentaire A-00 relancée** (`wp/tests/corrections-21nov/documentary.py`, conteneur jetable hors réseau, `--network none`, montages interdits) : **281 / 281 PASS**, 0 échec. Nettoyage du conteneur vérifié (`docker inspect` échoue après coup).
- La suite vérifie, entre autres, la **présence littérale** des corrections demandées et l'**absence** des anciennes formules :
  - présents : « Divergence brief / cahier », « Attribution via inscription gratuite : doute », « cellules et en-têtes », « quatre numéros réguliers par année », « Note d'articulation pour besoins 4, 6 et 15 », « user-agent seul insuffisant selon le §4.4 » ;
  - retirés : « user-agent seul interdit par la doctrine », « et une attribution via inscription gratuite ; ».
- Structure confirmée : 19 besoins ordonnés, 38 sources contiguës, registre aligné sur les extraits archivés (≥ 1 extrait cité par source).
- **Contre-exemple** recalculé mécaniquement : inscription le 20/02/2027 → 10/01, 10/04, 10/07, 10/10/2027 + 10/01/2028 = **cinq charges** avant le 20/02/2028. Cohérent avec le texte corrigé.
- `input_sha256` du test = empreintes des fichiers actuels : le test porte bien sur la version remise, pas sur une copie.
- **Pas de suite fonctionnelle à relancer pour A-00** : lot d'étude, sans code. Les tests PHP cités dans `notes.md` (175 tests / 19 912 assertions) relèvent des autres lots, pas d'A-00.

---

## 3. Régressions / modifications non demandées

Aucune **régression**. Les corrections n'ont pas abîmé les conclusions voisines (vérifié sur le diff).

Modifications présentes dans le diff **au-delà** de `corrections/A-00.md`, à porter à l'attention de Ced (légitimes mais hors périmètre de la fusion) :

1. **Arbitrages écrits de Ced du 21/11 transcrits dans le livrable** — ne viennent pas de `corrections/A-00.md` mais de décisions séparées de Ced :
   - Q1 (`:372`) réécrite avec la réponse « quatre paiements de date à date » **et** une « Proposition à relire » détaillée (quatre positions de paiement, écart d'une 5ᵉ date commune).
   - Q10 (`:379`) réécrite avec la réponse « même compte Stripe, sans CSV ».
   - Section 18 (`:313`) : « Hypothèse à confirmer » → « Scénario confirmé par Ced le 21/11 ».
   - **À confirmer par Ced :** que ces trois arbitrages sont bien les siens et fidèlement retranscrits. Ce sont des éléments de validation, pas un défaut d'Hermès.
2. **« Proposition à relire » en Q1** — mécanisme financier esquissé. Il reste borné (« aucune mise en œuvre », montants/rattrapages/première tranche renvoyés à Ced) et Ced avait autorisé « soumettre un mécanisme écartant la date commune en trop ». La frontière « l'étude n'arrête pas l'architecture à la place de Ced » est tenue, mais la proposition est détaillée : à relire par Ced.
3. **Fichiers ajoutés** : `notes.md` (journal des corrections et différés), bloc `qualification_21nov` dans `registre-citations.json`, en-tête 21/11 dans `PRET`, artefacts de test sous `tests-21nov/`. Attendus et déclarés.

Le diff `wp/` depuis l'état relu concerne les autres lots (connecteur, robots, entreprise, A-01) — **sans rapport avec A-00**, qui n'a pas de code.

---

## 4. Verdict

**Prêt pour la validation de Ced.**

Motif : les 8 instructions de la fusion sont appliquées (instr. 7 portée par le tenant du registre, comme prévu) ; la suite documentaire passe 281/281 ; aucune régression. Les seuls points ouverts ne sont pas des problèmes de fond restants d'Hermès : ce sont (a) la confirmation par Ced que les arbitrages du 21/11 transcrits en Q1/Q10/§18 sont les siens et fidèles, (b) la relecture de la « Proposition à relire » de Q1, et (c) les arbitrages déjà listés (questions 2–9 de l'étude, A/B/C de la fusion : carte/SEPA, retrait vs grâce, licence Teams). Ce sont exactement les décisions qui relèvent de Ced.

**Rappel :** ce verdict n'est pas un GO. Aucun développement, achat, activation ni mise en ligne n'est autorisé par cette vérification.
