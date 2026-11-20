# Relecture A-00 — Claude indépendant

**Lot :** A-00 — Étude de couverture des extensions.
**Nature :** étude documentaire, sans code, sans installation, sans achat.
**Relu :** `production/A-00/couverture-extensions.md` (+ `RELECTURE.md`, `PRET`, `verification.json`, `registre-citations.json`, `sources-officielles.json`, `sources-collectees.json`).
**Référentiel :** `doctrine/grille-relecture.md`, `doctrine/doctrine.md`, brief `briefs/A-00-couverture-extensions.md`, cahier des charges v3.1, `docs/decisions.md`.
**Non lu volontairement :** `relectures/A-00/codex.md` (existe). **Fusion non faite**, conformément à la consigne.

> Verdict en bas. Un verdict, même « Conforme », n'est pas un GO.

## Ce que j'ai vérifié moi-même

- **Intégrité des artefacts.** Empreintes SHA‑256 des 6 fichiers recalculées : toutes identiques à celles inscrites dans `verification.json` et `PRET`. `couverture-extensions.md` = `7ca81bdf…`, `verification.json` = `7f07d746…`. Dossier cohérent, non altéré.
- **Citations porteuses, re‑vérifiées en ligne (indépendamment du worker) :**
  - Besoin 2 — « It always uses the next occurring alignment date, regardless of the billing interval. » : **confirmé mot pour mot**. L'exemple officiel « souscription 6 avril, trimestriel aligné au 1er → premier renouvellement le 1er mai (pas le 1er juillet) » : **confirmé**.
  - Besoin 7 — « If you use the Stripe Creditor ID, Stripe always sends the notifications. » et « The customer must accept a mandate that authorizes the debit. » : **confirmés mot pour mot**. La page ajoute « By default, Stripe sends these notifications automatically » : va dans le sens de l'étude.
  - Besoin 5 — matrice PayPal : ligne « Synchronized or prorated payments » = ✗ pour PayPal Subscriptions, ✓ pour Vaulting ; « Requires Vault approval (Reference Transactions) » pour Vaulting : **confirmés**.
- **Cas déroulé à la main (§3.5).** Calendrier fictif 10 jan/avr/juil/oct, inscription 20 fév 2027, paiement immédiat puis à chaque date commune : 20/02, 10/04, 10/07, 10/10/2027 et 10/01/2028 avant l'anniversaire du 20/02/2028 = **cinq charges**. Le contre‑exemple de l'étude est exact.
- **Ancrage décisionnel.** `docs/decisions.md` (11/11 : « leurs moyens de paiement ne sont donc pas migrés : ils restent en place » ; 19/11 : rythme trimestriel) fonde bien les besoins 18 et 2.
- **Tests du lot.** Aucun `composer test` : lot d'étude sans code (rien dans `wp/` pour A‑00, ce qui est normal). Le `verification.json` (253 contrôles, 0 échec) est l'auto‑contrôle du worker ; je ne l'ai pas rejoué, mais j'en ai validé indépendamment les points clés (empreintes, littéralité de 3 citations, décompte des 5 charges).

## 1. Conformité

- **Livrable présent et au format.** `couverture-extensions.md` puis `PRET`. Tableau de synthèse (besoin · natif/module/sur mesure · source), une section par besoin, liste des modules complémentaires avec éditeur, liste du reste à développer, « À arbitrer par Ced » en questions fermées. Les 19 besoins du brief sont traités.
- **Besoin 2 « à examiner en premier ».** La synchronisation des renouvellements est bien traitée en tête, avec le contre‑exemple officiel et l'API de déplacement des dates.
- **Renvois au cahier.** Chaque besoin pointe son §. Vérifié sur §3.4, §3.5, §3.6, §3.8, §4.3, §4.4 : les interprétations correspondent au texte (carte/Bancontact → mandat SEPA ; case à cocher + accès immédiat ; emails Stripe désactivés / PayPal minimisés ; paywall serveur multi‑canaux).
- **Interprétations signalées.** Les choix d'argent et d'accès ne sont pas tranchés : ils partent en arbitrage (questions 1 à 10). Conforme à la doctrine §1.
- **Pas de sur‑portée.** Aucun GO, aucune architecture financière imposée, aucune recette prétendue. `PRET` dit explicitement qu'il ne vaut ni recette ni GO ni statut A‑01.

## 2. Exactitude métier

- **Besoin 2.** Juste. Deux idées distinctes et correctes : (a) l'alignement natif prend la prochaine date mensuelle et ignore l'intervalle long (donc pas de garantie de dates civiles communes à tous) ; (b) « expiration après N paiements » ≠ reconduction annuelle. Le modèle réel du §3.5 est **par numéro** (quatre numéros/an), ce que l'étude distingue.
- **Besoins 3‑4.** Justes et utiles. Bancontact → SEPA documenté ; carte → SEPA **non** documenté comme automatique → doute. Case à cocher native et accès dès acceptation → doute. C'est exactement ce que §3.6 exige et ce que la doc ne prouve pas.
- **Besoin 7.** Juste et important. Avec l'identifiant créancier **Stripe**, les prénotifications SEPA partent toujours : « aucun email Stripe » n'est pas garanti. La voie de sortie (identifiant créancier propre à Imagine + avis de prélèvement via Brevo, email n°2 du §3.8) est bien posée en arbitrage.
- **Cas limites.** Changement d'année, dates de clôture, reprise de l'existant, retards/échecs : couverts en doute et renvoyés en recette. Rien d'inventé.

## 3. Tests

- Lot sans code : pas de suite automatisée à lancer, et l'étude le dit (« A‑00 n'ajoute aucun test fonctionnel d'extension »).
- La frontière avec A‑01 est nette : lecture seule du reçu `e49f54c5e931` (104 PASS / 4 observations), aucune recette passerelle/HTTP/cadeau/groupe/migration revendiquée. Empreinte du reçu recoupée dans `verification.json`.
- Les contrôles documentaires portent sur la structure, les sources et les décomptes — pas sur une conformité financière ni une étanchéité de site. L'étude ne confond pas les deux.

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle d'abonné dans les artefacts. Les dates du contre‑exemple sont fictives et étiquetées comme telles.
- Aucune connexion à un site, un compte, une base ou une API payante. Collecte limitée à des pages publiques de documentation.
- Paywall : l'étude ne déclare **pas** Memberships étanche sur la seule base du shortcode ; elle liste REST/oEmbed/recherche/partages/PDF en doute à tester. Cohérent avec l'obligation de test d'étanchéité du §4.4.

## 5. Doctrine

- **Standard d'abord** respecté : toute l'étude sépare natif / module / sur mesure avant tout code.
- Pas de code, donc §5 des conventions sans objet.
- Modules retenus avec éditeur, sans achat. L'ancien Gifting (retiré) et un module de coupons (natif) sont explicitement écartés de la liste d'achats : bon réflexe anti‑doublon.

## 6. Études (sources)

- 38 sources officielles, numérotées, contiguës, chacune avec URL, date de consultation et extrait exact. Registre et sources recoupés avec le texte : concordants.
- Redirections The Events Calendar → `docs.nexcess.com` consignées ; indisponibilités (403 PayPal, 404 anciennes routes) signalées et non comblées par du forum/blog. Conforme à l'exigence « sans source : doute ».
- Les affirmations de capacité d'extension que j'ai échantillonnées portent toutes une citation ; les 28 % de phrases sourcées correspondent aux affirmations factuelles, le reste étant du raisonnement métier.

---

## Verdict : **Conforme** (étude prête à relire et à arbitrer — pas un GO)

Étude solide, honnête sur ses limites, bien sourcée, qui pousse correctement en arbitrage ce qui engage l'argent et les droits. Aucune citation fabriquée (3 vérifications indépendantes passées), intégrité confirmée, conformité au brief établie. Points ci‑dessous, aucun bloquant pour l'étude en tant que telle.

### Bloquant
- Néant au titre de l'étude. (L'impossibilité d'un « zéro email Stripe » avec l'identifiant créancier Stripe est un obstacle **projet** réel, mais l'étude le traite correctement en arbitrage — ce n'est pas un défaut du livrable.)

### Important
1. **Écarts à tracer (doctrine §6).** `docs/ecarts.md` n'existe pas. Deux contradictions révélées par l'étude relèvent du §6 et devront y être consignées, datées, à l'étape de fusion/correction (tâche du fusionneur, pas du worker) :
   - Besoin 7 : §3.8 demande les emails Stripe désactivés, mais le règlement SEPA + l'identifiant créancier Stripe imposent une prénotification ; résolution probable = identifiant créancier propre à Imagine + avis Brevo.
   - Besoin 2 / §3.5 : l'alignement natif ne garantit pas des dates civiles communes à tous les abonnés (contre‑exemple officiel 6 avril → 1er mai).
2. **Licence Teams déclenchée.** En retenant Teams for WooCommerce Memberships (besoin 9), A‑00 active la question de licence ouverte n°5 de `docs/decisions.md` (« Teams for Memberships si l'étude A‑00 le retient »). À remonter à Ced : A‑00 le retient ⇒ licence Teams à confirmer.

### Mineur
1. **Renvoi besoin 13 (ligne 242).** « user‑agent seul interdit par la doctrine » : la doctrine est muette sur les robots. L'exigence (« Un agent utilisateur seul ne suffit pas ») est au **§4.4 du cahier**. Citer le §4.4 plutôt que « la doctrine ».
2. **Clarté besoin 2 / question d'arbitrage n°1.** Le garde‑fou réel contre la 5e charge est la règle « quatre numéros par année d'abonnement » du §3.5 (comptage par numéro, non par date civile). L'étude la cite, mais le contre‑exemple et la question 1 sont surtout formulés en dates civiles ; rappeler explicitement le bornage par numéro lèverait l'ambiguïté. Clarté, pas erreur.
3. **Qualification source 34/31‑33 (besoin 17).** La « documentation officielle de l'éditeur » repose sur la filiation The Events Calendar → Nexcess (docs.nexcess.com). C'est bien la doc de l'éditeur, et l'étude le signale ; à garder en tête lors de la recette (seule source non recoupée en ligne par cette relecture).

### À arbitrer par Ced (déjà bien posé par l'étude)
Les dix questions fermées de l'étude sont pertinentes et fermées. Priorités suggérées pour débloquer la suite : question 1 (quatre paiements par année d'engagement), question 2 (carte → SEPA obligatoire ?), question 4 (identifiant créancier Stripe : exception ou identifiant propre ?). Les points « droits/argent/juridique » restent à faire valider par Imagine/conseil.

---

**Suite du circuit.** `relectures/A-00/codex.md` existe mais n'a pas été ouvert. La fusion (`corrections/A-00.md`) n'est pas faite, conformément à la consigne reçue. À lancer ensuite, sur demande.
