# Vérification B-07 — 2e et dernier tour

Objet : contrôler que les huit instructions de `corrections/B-07.md` ont été appliquées
par Hermès (fusion 21 h 41 → lot « correction2141 »), relancer les tests, repérer toute
régression. Pas de nouvelle relecture complète.

Base de comparaison : état relu `a54397d4` (dernier commit avant l'écriture des rapports,
21 h 08) → `HEAD`. `git diff` restreint aux fichiers B-07 (la fenêtre temporelle contient
d'autres lots, écartés).

---

## 1. Instructions de corrections/B-07.md

| # | Instruction | Statut | Où |
|---|---|---|---|
| 1 | R1 — liens du corps d'un partenaire déclarés `sponsored` | **Appliquée** | `wp/themes/imagine/functions.php:156-161` |
| 2 | R4 — export : propager l'échec de lecture (jamais « page vide ») | **Appliquée** | `wp/plugins/imagine-site/AgendaConfidentialite.php:22-25,35` |
| 3 | R2 — une seule projection du texte affiché / balisé | **Appliquée** | `wp/plugins/imagine-site/Agenda.php:94-110` ; `wp/themes/imagine/single-imagine_evenement.php:13,22,30` |
| 4 | Partenaire passé — garder étiquette et lien | **Appliquée** | `wp/themes/imagine/single-imagine_evenement.php:23-29` |
| 5 | i18n — libellés littéraux extractibles + domaine unifié | **Appliquée** | `Agenda.php:13-18,208,215` ; `single`/`archive` (domaine `imagine`) |
| 6 | Signaler un événement incomplet en administration | **Appliquée** | `Agenda.php:196-198` (`#imagine-agenda-incomplet`, `role="alert"`) |
| 7 | Supprimer le ternaire redondant à l'archive | **Appliquée** | `wp/themes/imagine/archive-imagine_evenement.php:14` |
| 8 | Couvrir l'adaptateur par une preuve rejouable | **Appliquée** | `wp/plugins/imagine-site/tests/AgendaAdapterTest.php` (+ `AgendaWPStubs.php`) |

Détail des points sensibles :

- **R1.** Le filtre B-05 `imagine_partner_content` ne sort plus seulement sur
  `imagine_partenaire` : il traite aussi un `imagine_evenement` **quand**
  `imagine_type === 'partenaire'`. Tout lien sortant du corps reçoit `sponsored`, en plus
  du bouton. Vérifié par `testLiensDuCorpsPartenaireEtContreExemples` : lien partenaire →
  `sponsored` ; rencontre ordinaire et liens internes → rien ; B-05 (`imagine_partenaire`)
  reste couvert.
- **R4.** `exporter()` renvoie désormais `array|\WP_Error` et retourne un `\WP_Error` sur
  lecture ratée (`Agenda::inscriptions() === null`), au lieu de `['data'=>[], 'done'=>false]`.
  C'est **le motif natif** des outils RGPD (WordPress interrompt l'export sur `is_wp_error`)
  et il est **identique à l'exporteur C-21** (`Confidentialite.php:322,405`), comme l'exigeait
  l'instruction. Testé : panne à la page 1 puis reprise sans omettre l'inscription, et export
  de 121 inscriptions paginé 50/50/21.
- **R2.** Nouvelle `Agenda::projection()` : `the_content` n'est appliqué **qu'une fois** ; la
  fiche affiche `projection['html']` et `schema($id, $projection)` réutilise le **même** rendu.
  `testProjectionFicheSchemaExecuteLeContenuUneSeuleFois` vérifie un shortcode exécuté une
  seule fois et `description` balisée = texte réellement affiché.
- **Instr. 4.** Dans `single-imagine_evenement.php`, la branche partenaire passe **avant** la
  branche « passé » : un partenaire passé garde « Partenariat » et son lien commercial, sans
  « inscriptions closes » ni formulaire. Testé (`testPartenairePasseConserveSonLienSansInscription`).
- **Instr. 5.** `libellesTypes()` déclare les libellés en chaînes littérales traduisibles ;
  idem pour les champs de la boîte admin ; domaine de thème ramené à `imagine` dans les deux
  gabarits. `testLibellesLitterauxEtDomainesDesGabarits` contrôle, par analyse de jetons, que
  tout argument de `__`/`esc_html__`/`esc_html_e` dans `Agenda.php` et `AgendaConfidentialite.php`
  est une constante littérale, et que les gabarits ne contiennent plus `'imagine-site'` ni
  `=== 'partenaire' ?` (couvre aussi l'instruction 7).
- **Instr. 8.** `AgendaAdapterTest` (7 méthodes) exerce l'adaptateur via bouchons WordPress,
  dans le bac à sable rejouable. Il couvre explicitement les régressions R1, R2, R4, le
  partenaire passé, l'alerte admin, la borne de `ouvert` et le doublon.

## 2. Résultat des tests

**Je n'ai pas pu relancer la suite dans cette session.** Toute exécution externe (php, Docker,
`rejouer.ps1`) est refusée ici faute d'approbation interactive — le même mur que Codex avait
rencontré au 1er tour (WSL `E_ACCESSDENIED`). Je m'appuie donc sur les reçus d'Hermès, mais en
les contrôlant (cohérence interne, logs de mutation, comptes).

Reçus du rejeu canonique (`production/B-07/correction2141-suite-finale.log`, conteneur
`network=none`, `rootfs=ro`, montage `:ro`) :

- `REJEU : 1135 tests, 35709 assertions, 0 échec, 0 erreur, 0 ignoré — PASS`.
- `OUTILS : 18 outils, 417 contrôles, 0 échec ; hors rejeu : aucun`.

Point important : **« hors rejeu : aucun »**. Au 1er tour, l'adaptateur n'était prouvé que par
des reçus live et exclu du rejeu (1128 tests) ; c'était le reproche porté (instruction 8).
Désormais 1135 tests (**+7**, soit les 7 méthodes de `AgendaAdapterTest`) et **aucun** outil
hors rejeu : la preuve est devenue rejouable dans le bac à sable autorisé. La faiblesse
« reçus du producteur » du 1er tour est corrigée.

Détection par mutation (`correction2141-mutations-sources.json`, **sources réelles mutées**,
pas de réponses mutées en mémoire) : 6 mutations, **toutes détectées** par le bon test —
r1→`testLiensDuCorpsPartenaire`, r2 + double-contenu→`testProjection`, r4→`testExportErreur`,
formulaire→`testPartenairePasse`, alerte→`testAdministration`. Les tests de non-régression
mordent donc réellement.

Réserve : ces chiffres restent les reçus d'Hermès, non un rejeu indépendant de ma part. Mais
ils sont désormais rejouables par construction et corroborés par la mutation ; cette réserve
tient à la contrainte d'exécution de la session, pas à un défaut du lot.

## 3. Régressions / modifications non demandées

- **Aucune régression** repérée dans les fichiers B-07. Les changements correspondent un à un
  aux huit instructions.
- `wp/themes/imagine/header.php` a changé dans la fenêtre, **mais** au commit `fb04a68f`
  (26/11 23 h 28), soit **après** « correction2141 » (~22 h 30) : c'est un lot ultérieur
  (bascule menu `wp_nav_menu`), **étranger à B-07**. Pas imputable à cette correction.
- Observation mineure, non bloquante : `Agenda::evenement()` conserve une clé `description`
  tirée du contenu brut (`Agenda.php:63`), désormais **inutilisée** par `schema()` (qui prend
  la projection). Vestige sans effet — ni fuite ni divergence. À nettoyer un jour, hors B-07.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les huit instructions sont appliquées et fidèles (R4 reprend exactement le motif `WP_Error`
de C-21). La suite est verte **et** redevenue rejouable sans reçu live (point dur du 1er tour
levé), les non-régressions sont prouvées par mutation. Aucun problème de fond restant, aucune
question métier ouverte. La seule chose en suspens est la **validation visuelle** des gabarits
(`single`/`archive` sur le squelette B-01), qui relève de Ced par doctrine §6 — rien de
bloquant côté technique.

Rappel : ce verdict clôt la vérification de code ; ce n'est pas un GO de mise en ligne (§3).
