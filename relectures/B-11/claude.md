# Relecture B-11 — vidéos, podcasts et sommaire audio (Claude, indépendant)

Date : 2026-11-27. Portée : `briefs/B-11-videos-podcasts-sommaire-audio.md`, `production/B-11/`, et dans `wp/` : `Medias.php`, `MediasRegles.php`, `AudioNumero.php`, leur raccord thème et tests. Références lues : doctrine, grille, cahier des charges §3.14, §3.3, §3.1, §4.4 (via le brief), C-06 (`Paywall`), C-11 (`PdfNumero`).

Je n'ai pas ouvert `codex.md`. La fusion n'est pas faite (consigne). Ce verdict n'est pas un GO.

## 0. Rejeu de la suite PHP (commande autorisée)

Commande jouée deux fois (conteneur jetable, hors réseau, dépôt en lecture seule) :

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne, **identique aux deux passages** (déterministe) :

> REJEU : 1189 tests, 36506 assertions, 1 échecs, 0 erreurs, 0 ignorés — FAIL

- Tests B-11 propres : `MediasB11Test` **4 tests / 34 assertions, 0 échec** (verts).
- Échec unique : `Imagine\Site\Tests\CatalogueTest::testOwnershipDoesNotBecomeAnotherPurchaseBeforeRelease` (`tests/CatalogueTest.php:33`, « Failed asserting that false is true »). **Ce n'est pas un test B-11.**
- Paquets : A-32 `A32_PARTIAL_EVIDENCE` toujours en échec connu, hors périmètre.
- Outils : 22 outils, 584 contrôles, 0 échec.

Je ne peux pas rejouer hors-ligne la recette runtime/navigateur de B-11 (`b11-runtime.php`, `b11-recette.py`) : elle exige le site de démonstration vivant, hors de mes droits (lecture seule, sans réseau). Les preuves d'étanchéité (0 appel sortant, témoins C26, mutations) viennent donc de `reception.json`, prises sur parole. J'atteste seulement le PHPUnit hors-ligne et la lecture du code.

## 1. Conformité

Le lot fait ce que le brief demande, sans plus.

- **Vidéo / podcast en lien seul, hôte en liste fermée** — `Medias.php:65` (`rendre`) produit un `<a>` explicite (« Voir la vidéo »), jamais d'iframe/script/vignette ; `MediasRegles::video` (`MediasRegles.php:24`) exige un hôte exact de `imagine_medias[hosts]`. Aucune URL dans le corps, donc l'auto-oEmbed natif n'est pas sollicité. Conforme au §3.14 et aux « cinq lignes ».
- **Réglage « intégrer après consentement », éteint par défaut, emplacement vide si allumé** — `Medias.php:78-81` : un `<div data-imagine-video-emplacement>` vide, sans appel. Défaut `0` (`Medias.php:19,35`). Conforme.
- **Podcast = lien HTTPS, rien d'autre** — `MediasRegles::lien` (`MediasRegles.php:10`). Conforme.
- **Sommaire audio servi comme le PDF de C-11** — `AudioNumero.php` réutilise sans modification `PdfNumero::directory()`, `PdfNumero::privateHeaders()` et `Paywall::decisionPdf()`. Blob `.wav` hors racine publique, mode 0600, pas de pièce jointe publique. Conforme au §3.3 et à C-11.
- **Suit le texte** — pour un article (`post`), `rendre` renvoie `''` si `Paywall::decision()['complet']` est faux (`Medias.php:68`) : qui n'a que l'extrait n'a ni lien ni adresse. Conforme.

Interprétations signalées par Hermès (NOTE.md), que je confirme comme interprétations et non comme faits du cahier des charges : l'audio réservé « aux ayants droit du numéro » est le **défaut prudent** (rangé pour Imagine) ; A-CARTE n'obtient pas l'audio du numéro 11 antérieur car c'est le réglage C-06 existant, pas un défaut B-11. Correct au regard de la doctrine (« une règle ouverte devient un réglage », défaut fermé).

## 2. Exactitude métier (déroulé à la main)

**Cas A — article réservé 3454 rattaché au numéro 11 (§3.14 + paywall C-06).**
- A-CARTE (droit article via C-06) : `decision['complet']=true` → `rendre` renvoie « Voir la vidéo » + lien podcast. Code `Medias.php:68,75-86` : conforme. (recette : `temoin_ayant_droit`.)
- Anonyme : `complet=false` → `''`. Conforme. (`anonyme_ni_lien_ni_adresse`.)
- Connecté sans droit (V-INSCRIT) : `''`. Conforme.
Résultat du code = résultat attendu. ✔

**Cas B — sommaire audio, numéros 11 et 39 (§3.3 + C-06/C-11).**
- P-NUMERO sur 11 : `decisionPdf.complet=true` + fichier présent → `<audio … imagine_audio=11>` (`AudioNumero.php:67-79`). ✔
- A-CARTE sur 39 (abonné actif) : audio rendu. ✔
- A-CARTE sur 11 (antérieur) : C-06 ferme → message réservé, **aucune adresse** (`AudioNumero.php:70`). ✔
- Anonyme sur `/?imagine_audio=11` : `serve` → `decisionPdf` faux → `302` vers la page numéro, aucun octet (`AudioNumero.php:111-113`). ✔

**Cas limites vérifiés par lecture.** HEAD autorisé → en-têtes `200` sans corps (`AudioNumero.php:119`). Méthode autre que GET/HEAD → `405` (`:92`). Nom de blob en traversée (`../secret.wav`) ou absent → `path()` lève, `serve` retombe en `302` (`:88,97-114`) ; couvert par la recette (`reference_traversal_refusee`, `blob_absent_refuse`). Pas de distinction observable entre « pas le droit » et « fichier manquant » (toujours `302`) : bon, pas de fuite d'existence. Exactitude métier : conforme.

## 3. Tests

- B-11 propre au vert (voir §0). Les règles pures (validation hôte, lien, casse, suffixe, tailles) sont vraiment testées dans `MediasB11Test`, pas une simple répétition du code — bon.
- **Mais le rejeu global est ROUGE** (FAIL). Cause établie ci-dessous. La NOTE de B-11 (ligne 52) et le README affirment « Rejeu général … 0 échec » : **cette affirmation n'est plus reproductible dans l'arbre courant.** À reconcilier.
- Les règles WordPress de B-11 (gating paywall de `rendre`/`lecteur`, endpoint `serve`, non-exposition REST, 0 appel sortant) ne sont couvertes que par la recette runtime/navigateur, non rejouable hors-ligne ici. Couverture réelle mais non vérifiable par le relecteur indépendant sans le site.

### Cause de l'échec (hors B-11)

`CatalogueTest` passe par le banc `tests/b04-adapter-fixture.php`. Depuis le commit **7b349c4b (2026-11-27 11:28)**, soit **après** le scellé de B-11 (`PRET`, 10:53), `AchatsNumeros::droits()` appelle `apply_filters('imagine_achat_instantanes', …)` (`AchatsNumeros.php:139`, commentaire « C28 »). Le banc B-04 **ne stubbe pas** `apply_filters` (seul `AgendaWPStubs.php` le fait). L'`Error` « undefined function » est alors avalée par le `catch (\Throwable)` de `Paywall::evaluerNumero` (`Paywall.php:148`), qui renvoie `complet=false` → `possede=false` → l'assertion `assertTrue($rows[0]['possede'])` tombe. Mécanisme compatible au mot près avec le message observé, et confirmé par `git log -S 'imagine_achat_instantanes'` (introduit uniquement en 7b349c4b).

Conclusion : régression **C-28** (travail en cours) sur le banc **B-04**, sans rapport avec le code B-11. B-11 n'a ni modifié ni rescellé ces fichiers. Mais tant que l'arbre reste ainsi, la porte doctrinale « tests au vert » n'est pas franchie pour le dépôt, et donc **B-11 ne peut pas être clôturé en l'état**.

## 4. Sécurité et données

- **Aucun secret, aucune donnée réelle.** Hôte `video-fictive.example.invalid`, podcast `…example.invalid`, WAV = silence fabriqué ; A-VOIR déclare tout fictif. Conforme §3.
- **Droits.** Enregistrement sous nonce + `current_user_can('edit_post')` (`Medias.php:123-125`). Audio : chaque GET/HEAD réévalue `decisionPdf` (`AudioNumero.php:98`), jamais de chemin physique ni X-Sendfile. Conforme.
- **Échappement.** `esc_url`/`esc_html`/`esc_attr`/`esc_textarea` partout ; `rel="external noopener noreferrer"` sur les liens tiers (pas de fuite de référent). Bon.
- **Métadonnées.** `_imagine_video`, `_imagine_podcast`, `_imagine_audio_blob` : préfixe `_` (protégées), non enregistrées pour REST. Non exposées. Correct — mais non prouvé par un test hors-ligne (seulement par les témoins C26 de la recette).
- **Étanchéité résiduelle.** La garantie « aucun appel sortant, oEmbed compris » tient **uniquement** parce que l'URL vit dans une méta séparée et n'est jamais collée dans le corps. B-11 ne verrouille pas le cas où un rédacteur colle l'URL dans le corps (ce qui réactiverait l'oEmbed natif). NOTE.md le reconnaît comme consigne. Risque opérationnel réel, à surfacer.

## 5. Doctrine

- **Standard d'abord** : respecté — `<audio>` natif, oEmbed natif inchangé, réemploi de `PdfNumero`/`Paywall` sans copie ni modification. Bon.
- **Logique métier hors WP** : `MediasRegles` pur et testable. Bon.
- **§5 conventions** : `declare(strict_types=1)`, `namespace Imagine\Site`, préfixe `imagine_`, i18n FR. Conforme.
- **Mineur** : l'injection de la section réglages (`Medias.php:142-161`) ré-emballe par tampon de sortie les rappels de rendu de la page `imagine-reglages` et insère avant `</form>`. Motif fragile (dépend de `</form>` et de la chaîne `imagine_reglages`), répété de lot en lot (C22/C24/C25/C27) plutôt que factorisé. Hérité, non propre à B-11 ; à surveiller.
- **Observation (non-défaut)** : `AudioNumero` s'écarte d'« exactement comme le PDF C-11 » sur deux points **justifiés** : `Content-Disposition: inline` (vs `attachment`) pour la lecture par le lecteur natif, et absence de pièce jointe/filtre `rest_prepare_attachment` (aucun attachment n'est créé). « Exactement » vaut donc pour le moteur d'accès et le stockage, pas pour la livraison octet-pour-octet. Conforme au brief.

## Verdict

**Code B-11 : Conforme.** Le lot fait ce que le brief demande, ses propres tests sont verts, le déroulé manuel des deux cas concorde avec le code.

**Clôture impossible en l'état** : le rejeu autorisé est FAIL et la NOTE B-11 affirme un rejeu général au vert qui n'est plus reproductible. Ce verdict n'est pas un GO.

Points classés :

- **Important (hors périmètre B-11, mais bloque la preuve et la clôture)** : REJEU = FAIL, déterministe. `CatalogueTest::testOwnershipDoesNotBecomeAnotherPurchaseBeforeRelease` échoue à cause d'une régression **C-28** (commit 7b349c4b, 11:28) : `AchatsNumeros::droits()` appelle `apply_filters` non stubbé dans le banc B-04, erreur avalée par le `catch` de `Paywall`. La NOTE/README de B-11 (« Rejeu général 0 échec ») doit être réconciliée avec l'arbre courant. Écart à tracer dans `docs/ecarts.md` à la clôture.
- **Mineur (B-11, interprétation technique)** : « 0 appel sortant » ne tient que si l'URL n'est jamais dans le corps ; B-11 ne l'empêche pas.
- **Mineur (B-11, vérifiabilité)** : les règles WP de B-11 ne sont couvertes que par la recette non rejouable hors-ligne ; le PHPUnit hors-ligne ne couvre que `MediasRegles`.
- **Mineur (doctrine, hérité)** : injection des réglages par tampon de sortie, motif fragile répété.
- **Observation** : `Content-Disposition: inline` et absence d'attachment — écarts justifiés par rapport à C-11.

### Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après coup)

1. **Banc B-04 vs C-28.** Question : faut-il stubber `apply_filters` dans `tests/b04-adapter-fixture.php` ? Défaut proposé : **oui**, ajouter le stub minimal (retourner `$value`) côté C-28, afin que le banc reflète le nouvel appel sans toucher à B-11. C'est du ressort du lot C-28, pas de B-11.
2. **Catch trop large de `Paywall::evaluerNumero`/`evaluer`.** Une `Error` de programmation (fonction indéfinie) y devient silencieusement « accès fermé ». Défaut proposé : **garder le fail-closed** (bon pour la sécurité) mais **ne pas confondre** une `Error` de code avec une absence de droit — au minimum la laisser remonter en test. Hors périmètre B-11 (C-06) ; à verser au lot concerné.

### Pour Imagine (réglage métier)

- Portée exacte du droit au sommaire audio (déjà posée par Hermès comme défaut « ayants droit du numéro »). Défaut prudent en place et fermé ; rien à trancher pour débloquer B-11.

### Pour Ced (visuel / touchant au réel)

- Aucune validation visuelle donnée : squelette B-01, lecteur natif, emplacement vide. À regarder en captures.
- Rien d'autre touchant au réel : aucun appel fournisseur, paiement, email ni ouverture de droit dans ce lot.
