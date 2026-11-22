# C-05 — corrections de fusion du 22 novembre 2026

**Fait :** instructions 1–5 de `corrections/C-05.md` appliquées ; fichier complet (60 lignes), doctrine et consigne permanente relus.
**Prêt à relire :** C05 corrigé, après gates réelles et suppression des deux conteneurs ; PRET redéposé seulement après vérification.
**À arbitrer :** Q1 reste ouverte pour le futur SEPA ; aucun choix financier nouveau. Q2 n’est pas reposée : défaut `restent_dues` déjà explicite le 22/11.
**Bloqué :** rien pour cette remise de prototype ; aucun raccord admin/encaisseur de production autorisé ni effectué.
**Suivi Claude :** item 6 seulement, reporter dans `docs/ecarts.md` le brief « jamais cinq » devenu obsolète face à Option A du 22/11. Aucun fichier `docs/`, verrou ou rapport global modifié.

## Corrections et périmètre

1. `Planificateur` valide récursivement les blocs précédents et compare rang 1 reconduit au rang 4 précédent. Le calendrier pourtant accepté par C01, avec `REG-2028-04` et `REG-2028-01` à même clôture, refuse explicitement `DATES_NON_CROISSANTES` (date commune 03/01/2028). Aucun déplacement de commune ni borne anniversaire. Le 09/04 reste valide et conserve cinq dates dans sa fenêtre numérique.
2. Les cas autonomes sont portés en vrais `*Test.php` PHPUnit ; le XML partagé autorisé reçoit uniquement la suite Echeancier. `tests/Echeancier/run.php` est supprimé, données communes séparées dans `Fixture.php`. Les 365 dates et les 28 fenêtres à cinq dates sont vérifiées dans la commande standard.
3. `finEngagement` est retiré. API : `planifier(Annee $annee, ?int $margeJours = null)`. Une année non activée (`finNumerique() === null`) se projette sans TypeError ; projection seule, aucune activation de droit ou de débit.
4. Refus admin par `wp_die()` et message traduit. Contrat PHPUnit + vrai WordPress classique/HPOS, filtre de traduction et handler terminal intercepté puis retiré dans `finally`.
5. Deux compléments officiels distincts : M3/[5], exemple complet 6 avril → 1er mai ; C05-02/[4], hook nommé et avertissement réellement dans sa section. URL finale, HTTP 200, heure, empreinte et brefs extraits vérifiés dans `sources/review-fusion-22nov-1458.json` ; anciennes collectes intactes.

Écritures : `src/Echeancier/{Planificateur,ReglagesAdministration}.php`, `tests/Echeancier/` (fixture, doubles et deux classes de test), `phpunit.xml`, runner dédié `wp/tests/echeancier-runner/` (scripts/scénarios et instructions), proposition, présente note, nouvelle collecte et paquet de preuves C05. README partagé, Composer JSON/lock et C01/C04/C06/C07 inchangés : inventaire protégé de **647 fichiers** comparé. Retirer uniquement la ligne Echeancier reconstruit exactement le SHA-256 du XML historique C07. Aucune preuve indépendante C06/C07 réécrite ou déclarée actualisée.

## Résultats réels — PHP dans les conteneurs uniquement

Paquet unique : `production/C-05/replays/fusion-22nov-1458/`.

| Suite standard | Tests | Assertions |
|---|---:|---:|
| Numeros | 42 | 121 |
| Robots | 101 | 298 |
| Entreprise | 41 | 19 561 |
| Acces | 63 | 10 388 |
| Envoi | 115 | 402 |
| **Echeancier** | **384** | **2 307** |
| **Total** | **746** | **33 077** |

`final.xml` / `final.json` : **0 échec, 0 erreur, 0 skipped**, `composer test` strict, lint global PSR-12, syntaxe et Composer validate strict : **tous exit 0**. RED jonction, API et refus admin conservés avant leurs corrections ; les GREEN intermédiaires avec lint encore non nul ne sont pas présentés comme gates finales.

`final-e2e-result.json` : vrai Subscriptions **9.4.1**, Woo **11.1.1**, WP **7.0.9**, PHP **8.2.36** ; classique + HPOS, quatre scénarios par stockage, deux blocs chacun. **8 abonnements, 8 initiales + 56 renouvellements réels = 64 commandes ; 352 contrôles par stockage, 704 au total + 12 d’enveloppe ; exit 0.** Dates natives/actions exactes, huit positions distinctes, jonction égale refusée avant création de commandes. Actions futures exécutées explicitement en accéléré, confirmations locales à l’heure réelle : aucune preuve de débit bancaire, retry, emails, Odoo ou sauvegarde HTTP revendiquée.

`standard-cleanup.json` et `cleanup.json` : suppression des seuls runners possédés, absence exacte revérifiée. Aucun montage/volume/port, aucune installation hôte, aucun service de staging touché ; réseau détaché avant PHPUnit, `none` dès création e2e. Dépendances Composer publiques préparées seulement dans le runner autorisé ; ZIP Subscriptions autorisé jamais versé au dépôt. `verification.json` lie sources finales, compteurs, notes, citations et cleanup. Ancien PRET archivé dans ce paquet ; reçus `preuves/` et notes antérieures restent historiques.

Incidents non bloquants : `execute_code` interdit en unattended, extraction web non disponible dans son backend ; aucune sortie fabriquée. Éditions/outils normaux et lectures HTTP publiques officielles ont servi de repli.

## Vérification parent

Depuis `C:/Users/Ced/imagine` :

```bash
IMAGINE_C05_PACKET=fusion-22nov-1458 python -B wp/tests/echeancier-runner/corrections.py verify
```

Rejeu PHP réel complet, nouveau paquet et fermeture même sur erreur : `wp/tests/echeancier-runner/README-corrections.md`. Consulter `final.xml`, `final.json`, `final-e2e-result.json` et `verification.json`. Aucun bootstrap à raccorder maintenant : bibliothèque non installable selon le README partagé. PRET n’est ni clôture, ni relecture indépendante, ni GO financier/réel.
