# Vérification C-28 — second et dernier tour

Date : 2026-11-27. Vérificateur : Claude (tour 2).
Base : `corrections/C-28.md` (fusion du 27/11, 12 h 40). Code relu puis corrigé par Hermès.
Méthode : `git diff` depuis la version relue (commit `ea938105`, dépôt de la fusion) sur `wp/` et `production/C-28/`, relecture des fichiers cités, contrôle d'intégrité des empreintes scellées, relance des vérificateurs accessibles. **Pas de relecture complète refaite.**

## 0. Intégrité du code livré

Les empreintes des sources C-28 livrées correspondent **exactement** au manifeste scellé `production/C-28/reception-corrections.json` :

| Fichier | SHA-256 (livré = scellé) |
|---|---|
| `PacksThematiques.php` | `70e5d519…febee` ✔ |
| `AchatsNumeros.php` | `013b3ba9…3434b70` ✔ |
| `single-product.php` | `feb4a54b…c15e95` ✔ |
| `tests/PacksC28Test.php` | `f65026c2…0651a6` ✔ |
| `tests/PacksC28AdapterTest.php` | `195db8da…0ef4a13` ✔ |

Le code que je relis est bien celui qu'Hermès a scellé et testé.

## 1. Instructions de `corrections/C-28.md` — état

### Instruction 1 — C28-01 : indisponibilité d'un pack appliquée côté serveur
**Appliquée.** Le masquage du bouton subsiste (`wp/themes/imagine/single-product.php:36-40`), mais il est désormais **doublé de gardes serveur** dans `PacksThematiques.php` :
- `achetable()` sur `woocommerce_is_purchasable` (`PacksThematiques.php:47-51`, enregistré l.209) : un pack dont `numeros()` vaut `[]` n'est plus achetable.
- `ajouter()` sur `woocommerce_add_to_cart_validation` (`:53-60`, l.210) : refuse l'**ajout natif direct** (`?add-to-cart=ID`) avec message.
- `panier()` sur `woocommerce_check_cart_items` (`:62-71`, l.211) : **revalide à la validation de commande** un panier constitué avant la dépublication.
- `preparer()` lève une exception si `numeros()===[]` au moment du paiement (`:95-97`).

Les deux chemins que Codex avait identifiés (panier pré-constitué, ajout natif direct) sont fermés côté serveur. Plus de paiement plein pour un instantané vide.

### Instruction 2 — C28-02 : capture réservée à la première persistance du paiement
**Appliquée.** La logique de `payer()` a été scindée :
- `preparer()` sur `woocommerce_before_order_object_save` (`:74-103`) ne capture que la **transition non payé → payé** : il recharge l'objet commande persisté et sort si celui-ci est déjà payé (`:84-86`). La capture vit dans une `WeakMap` éphémère, pas sur le produit.
- `payer()` sur `woocommerce_after_order_object_save` (`:106-135`) **consomme la capture éphémère** et **ne relit jamais `wc_get_product()`**. Si l'instantané est absent ou non fiable (`instantane` vide, produit ou `paye_le` discordants), il pose la méta `ANOMALIE` (`:125-133`) — accès fermé, aucune reconstruction, aucune réparation automatique.
- `instantanes()` (`:138-157`) renvoie `[]` dès que `ANOMALIE` est posée ou que le produit/`paye_le` ne concorde pas.

La reconstruction tardive sur la liste vivante, avec une date de paiement antérieure, n'est plus possible.

### Instruction 3 — tests couvrant C28-01 et C28-02 dans la suite scellée rejouable
**Appliquée.** Ajouts scellés : `tests/PacksC28Test.php`, `tests/PacksC28AdapterTest.php`, `tests/fixtures/c28-adapter.php`, `wp/tests/demo/c28-canaris.py`, `wp/tests/demo/c28-corrections-runtime.php`. Les canaris rejouables couvrent nommément les deux points :
`C28-01-direct`, `C28-01-checkout`, `C28-02-late-reconstruction`, `C28-02-paid-missing-date`, `C28-symmetry` (cinq rouges) + `GREEN`. Le vérificateur offline confirme que ces mutants portent sur les **empreintes exactes des sources livrées** (`canaris_sources_courantes`), et que la fenêtre de panne après persistance est couverte (18 contrôles, « objet rechargé / édition / sauvegarde tardive fermée et signalée »).

### Instruction 4 — documenter les lanceurs non rejoués en relecture
**Appliquée.** `production/C-28/A-VOIR.md:64-66`, section « Lanceurs non rejoués par les relecteurs initiaux » : PHPUnit non lançable côté Codex (`Wsl/Service/E_ACCESSDENIED`), recettes `--live`/mutantes non rejouées des deux côtés, commandes exactes de rejeu fournies (`:33-50`).

### Décision technique — déliement symétrique pack ↔ C-14 (Claude-m2)
**Appliquée.** `AchatsNumeros.php:195` : `$product->delete_meta_data('imagine_pack_numeros');` lors de la pose d'un numéro unique valide, par symétrie avec `PacksThematiques::enregistrer()`. Un produit ne peut plus porter les deux métas via une sauvegarde programmatique partielle.
*Réserve mineure de style (non bloquante)* : la clé est écrite en chaîne littérale `'imagine_pack_numeros'` plutôt que via la constante `PacksThematiques::PRODUIT`. Valeur identique, comportement correct ; à harmoniser un jour, sans incidence.

## 2. Résultat des tests

**Relancé par moi (indépendant, offline) :**
- `python wp/tests/demo/c28-verifier.py` → `{"C28":"PASS","mode":"offline","checks":31,"success":true}`.
  Ce vérificateur relit les preuves scellées **et les revérifie contre les sources courantes** : recette 200/200, parcours avant/payé/ajout/retrait/remboursements à numéros constants, natif 25/25, C14 45/45, fenêtre de panne 18/18, canaris 5 rouges + 1 vert sur sources courantes, PHPUnit branchement 3 tests/54 assertions, rejeu général > 1 100 tests `PASS`, sceaux sources+preuves conformes.

**Non relançable par moi dans cette session non-interactive :** l'exécution de `php`, `powershell` et `docker`/WSL exige une approbation indisponible ici. Je n'ai donc **pas** pu ré-exécuter moi-même la suite scellée Docker (`rejouer.ps1`), PHPUnit, les canaris ni la recette `--live`. Les chiffres ci-dessous proviennent des **reçus d'Hermès** (`correction-*-final*`), dont j'ai revalidé l'intégrité (empreintes) via le vérificateur offline :
- Rejeu général : **1 190 tests / 36 548 assertions**, 0 échec/erreur/ignoré, `PASS` ; outils 720 contrôles verts.
- PHPUnit C-28 : 3 tests / 54 assertions ; canaris 5 rouges puis 1 vert ; natif 25/25 ; fenêtre de panne 18/18 ; C14 45/45 ; recette HTTP 200/200 ; 19 fichiers PHP sans erreur de syntaxe.
- Paquets : 11 vérifiés, 1 échec `A-32 / A32_PACKAGE_DRIFT` et `A-31` hors rejeu — **connus et hors périmètre C-28**.

Rappel : au premier tour, Claude avait rejoué la suite PHP de façon indépendante. Ce second tour confirme l'intégrité et la cohérence des preuves, mais ne constitue pas un nouveau rejeu Docker indépendant.

## 3. Régressions ou modifications non demandées

- **Périmètre C-28 : aucune.** Le `git diff` sur les sources scellées est confiné aux quatre instructions et à la décision technique.
- **Hors périmètre C-28 (pas une régression du lot) :** `Acquisition.php` et `AcquisitionConfidentialite.php` sont modifiés dans la même fenêtre de synchro, mais **ne figurent pas** dans le manifeste scellé C-28 (`reception-corrections.json`). Ils relèvent d'un autre lot (acquisition/confidentialité). Signalé pour traçabilité ; sans impact sur C-28.
- Le mode Woo « Coming Soon » reste inchangé : le MU fictif n'exempte que la fiche de démonstration (`A-VOIR.md:12`). Cohérent avec la note de livraison.

## 4. Arbitrages encore en attente (hors code, pour mémoire)

Les deux questions de `corrections/C-28.md §5` restent **métier, adressées à Imagine**, pas à Ced, et ne bloquent pas la clôture du code (doctrine §4 « une règle ouverte devient un réglage ») :
1. « Produits groupés » (§3.3) = produit simple à prix unique — *défaut implémenté* : produit simple.
2. Pack contenant un numéro dépublié — *défaut implémenté* : blocage strict de tout le pack, aucun prix recalculé.
Leur défaut prudent est en place et testé.

## 5. Verdict

**Prêt pour la validation de Ced.**

Les deux points importants (C28-01, C28-02) sont corrigés côté serveur et couverts par des canaris rejouables rouges-puis-verts portant sur les sources livrées ; la décision technique est appliquée ; A-VOIR.md documente la lacune de rejeu signalée. Empreintes conformes au sceau, vérificateur offline au vert (31 contrôles). **Aucun problème de fond restant.**

Réserve de méthode, sans remettre le verdict en cause : dans cette session non-interactive je n'ai pas pu ré-exécuter moi-même la suite scellée Docker/PHPUnit/`--live` (approbation indisponible) ; je m'appuie sur le rejeu indépendant du premier tour et sur la revalidation d'intégrité des preuves. Si Ced souhaite un rejeu Docker frais avant clôture, les commandes sont dans `A-VOIR.md:33-50`.

**Un verdict de vérification n'est pas un GO** au sens de la doctrine §3 : il ne vaut ni mise en ligne, ni validation visuelle, ni autorisation de déploiement.
