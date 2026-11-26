# Relecture C-24 — Formulaire de personnalisation (Claude, relecteur indépendant)

Brief : `briefs/C-24-formulaire-de-personnalisation.md`. Cahier des charges : §3.7, §3.10, §4.2, §4.4.
Production relue : `wp/plugins/imagine-site/Personnalisation*.php`, `wp/tests/demo/c24-*.php`, `wp/outils/demo/c24-seed.py`, `production/C-24/`.
Ce verdict n'est pas un GO (doctrine §6).

## Rejeu des tests (commande autorisée, sans argument)

Commande exécutée : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`
(conteneur jetable, `network=none`, `rootfs=ro`, dépôt monté en lecture seule, `cap-drop=ALL`, `no-new-privileges`).

Dernière ligne :

```
REJEU : 1128 tests, 35565 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Également : `OUTILS : 16 outils, 311 contrôles, 0 échecs`. L'outil `a24` est vert (17 contrôles).

## 1. Conformité

Le lot fait ce que le brief demande, sans débordement. Correspondances :

- **Questions = donnée, pas code** (§3.7). Réglage additif dans l'écran C-10 : `PersonnalisationReglages::champs()` + injection dans le formulaire Settings API existant. Ajouter une ligne crée une question sans toucher au code. ✓
- **Rubrique « Personnalisez ce que vous recevez »** dans Mon compte (§3.7) : `Personnalisation::compte()`, hook `woocommerce_account_dashboard`. Lecture, modification, effacement ; chaque réponse datée (`date_utc`). Rien n'est obligatoire : aucun attribut `required` (vérifié ligne `c24-runtime.php:39`). ✓
- **Consentement distinct** (§4.4, §3.7) : case séparée, non cochée (`Personnalisation.php:160`, `checked(... ?? false)`), texte conforme au brief. Stocké dans `imagine_personnalisation_consentement`, daté à part des étiquettes (`META`) et des newsletters (`Newsletters::META`). Trois formulaires indépendants. ✓
- **Point d'accroche nommé pour Brevo** (§3.10) : `Personnalisation::attributsConnecteur($id)` projette les attributs, et `imagine_personnalisation_attributs_modifies` (constante `ACCROCHE`) est émis sans écouteur livré. Transmission uniquement si consentement **et** inscription à ≥ 1 newsletter. ✓
- **Rien ne part** : aucun client Brevo, aucun `wp_mail`, aucune requête HTTP. `APRES_INSCRIPTION_ACHAT` est un emplacement nommé, non raccordé. ✓
- **Réserve d'identifiants (leçon C-22)** : options `imagine_personnalisation_reserve_q_*`/`_c_*`, alimentées par le catalogue courant, l'historique des réponses et le **rejeu du journal C-10** (`Imagine\Pilotage\Administration\Reglages::JOURNAL`, dépendance C-10 présente et résolue). Un identifiant retiré reste refusé ; un choix actif ne peut changer de question. ✓
- **Compte sans email** : rubrique présente, pas de case de consentement, consentement refusé côté serveur (`enregistrer` : garde `Newsletters::admissible`). Défaut conforme au brief. ✓
- **C-21** : callbacks d'export et d'effacement **ajoutés** sans modifier C-21 (`PersonnalisationConfidentialite`). ✓

**Interprétations signalées (par Hermès, et confirmées ici) :**

1. `attributsConnecteur` exige, en plus du consentement et de la newsletter, l'**admissibilité email** (`Newsletters::admissible`). Ce n'est pas écrit tel quel au §3.10, mais c'est cohérent avec le brief (« compte sans email… exclu de tous les envois ») et redondant en pratique (une préférence newsletter suppose un email). Interprétation prudente, acceptable.
2. **Localité en choix fermés** : le brief demande explicitement de la poser en question si un texte libre est voulu → voir « Pour Imagine ».

## 2. Exactitude métier — cas déroulés à la main

**Cas 1 — §3.10, conjonction de transmission.** Profil A-PAPIER : réponse `situation-fictive = reveur-fictif`, consentement donné (accord `true`, daté), inscrit à ≥ 1 newsletter, email valide.
- À la main : `transmissible({accord:true,date}, newsletter:true, email:true)` = `true` → `attributsConnecteur` = `{situation-fictive:{choix:[reveur-fictif],date}}`.
- Retrait du consentement (`accord:false`) → `false` → `[]`. Désinscription de toutes les newsletters → `[]`. Compte sans email → `[]`.
- Résultat du code identique (contrôles `conjonction_ouvre_attributs`, `retrait_consentement_garde_reponses`, `sans_newsletter_aucun_attribut`, et les 8 combinaisons booléennes de `c24-rules.php`). **Conforme.**

**Cas 2 — §3.7, identifiant réservé (leçon C-22).** Question `cinquieme-c24-fictive` ajoutée par le réglage, puis retirée, puis ré-ajoutée avec le même identifiant.
- À la main : au retrait, le journal C-10 garde l'événement ; `nettoyer` rejoue le journal → `reserve_q_cinquieme` existe. La ré-soumission porte un identifiant absent du catalogue courant mais réservé → `InvalidArgumentException` → valeur conservée inchangée, erreur de réglage affichée.
- Résultat du code identique (`identifiant_question_retire_reserve`, et côté mutation `question_reservee_refusee`/`choix_reserve_refuse`). **Conforme.**

**Cas limite — compte sans email :** rubrique présente, pas de case, consentement refusé serveur (`sansmail_rubrique_presente_sans_case`, `sansmail_consentement_refuse`). **Conforme.**

**Cas limite — effacement/export (C-21) :** l'export contient étiquettes + consentement ; l'effacement retire les deux métadonnées ; les réponses d'un tiers ne sont pas touchées ; après effacement, les **réserves d'identifiants subsistent** (`reserve_apres_privacy_reste`). **Conforme.**

Changement d'année / calendrier incomplet : sans objet ici (pas de logique de date métier ; seules des dates UTC d'horodatage, format `Y-m-d\TH:i:s\Z` validé par regex).

## 3. Tests

- **Passent** : rejeu vert ci-dessus. Suite pure (`c24-rules.php`), runtime natif avec transaction + ROLLBACK et readback (`c24-runtime.php`), mutations ciblées en mémoire (`c24-mutations.php`).
- **Cas limites couverts**, pas seulement le nominal : tiers refusé/inchangé, version périmée, cinquième question ajoutée/retirée, recyclage d'identifiant refusé (question, choix, historique de réponse effacée), aucun mail/HTTP, accroche sans écouteur.
- **Tests de mutation sérieux** : 5 mutants de vraies sources (garde question, garde choix, consentement, newsletter, email) évalués en mémoire, jamais installés, chacun détecté séparément. Les tests lisent les métadonnées persistées, pas seulement les retours.
- **Lacune de couverture (mineur)** : l'**injection HTML dans la page C-10** (wrapper `admin_menu` priorité 145 qui fait `ob_start` / repère `</form>` / `substr_replace`) n'est testée qu'indirectement par capture Chromium. Le test automatisé ne vérifie que `champs()` isolément (`champ_C10_dans_formulaire`), pas l'insertion dans le vrai formulaire. Si le markup C-10 change (balise `</form>`, marqueur `value="imagine_reglages"`), l'injection **échoue en silence** (section absente, aucune erreur). L'ordre d'enregistrement est sain (C-10 à la priorité 10, raccord à 145), donc le risque est une régression future de markup, pas un bug actuel.
- **Lacune de couverture (mineur)** : le chemin de rollback de `PersonnalisationReglages::journal()` (réserve ou `add_option` indisponible → restauration de l'option, `wp_die` si échec) n'a pas de test dédié.

## 4. Sécurité et données

- **Aucun secret, aucune donnée réelle.** Jeu de démonstration manifestement fictif (« fictif/fictive », lunes, nuages, lucioles) ; adresses de test en `@example.org`. ✓
- **Contrôle des droits / nonces** : `traiter()` vérifie méthode POST, `compte === id` courant, nonce `imagine_personnalisation_$id`, puis `enregistrer` revérifie `id === get_current_user_id()`. Concurrence optimiste (`version()` + `hash_equals`) et verrou nommé MySQL (`GET_LOCK`). ✓
- **Échappement des sorties** : `esc_html`, `esc_attr`, `esc_url`, `esc_textarea`, `checked`, `selected` systématiques. ✓
- **Requêtes préparées** : tous les `$wpdb->get_col/get_var` passent par `$wpdb->prepare` (y compris `esc_like` sur le préfixe de journal). ✓
- **Paywall** : hors périmètre de ce lot (aucun texte réservé servi). Aucune voie de sortie du texte réservé introduite.
- **RGPD (§4.4)** : consentement explicite distinct pour les étiquettes ✓ ; étiquettes et consentement entrent dans l'export et la suppression natifs ✓.

## 5. Doctrine

- **Standard d'abord** : Settings API, exporters/erasers de données personnelles natifs, `user_meta`, `admin-post.php`. Aucune table ni extension nouvelle. Le sur-mesure se limite aux règles propres aux questions/étiquettes. Références officielles citées dans `TRANSMISSION.md` (Plugin Handbook). ✓
- **Logique métier hors WordPress** : `PersonnalisationRegles` est du PHP pur sans dépendance WP (catalogue fermé, transitions datées, conjonction de transmission), testé seul par `c24-rules.php`. ✓
- **Conventions §5** : `declare(strict_types=1)`, namespace `Imagine\`, préfixe `imagine_`, textes passés par les fonctions de traduction, aucune modification de code tiers (uniquement des hooks). ✓
- **Point doctrine §5 (mineur)** : le `README.md` d'`imagine-site` ne mentionne pas la personnalisation (ni ses réglages, ni comment lancer `c24-*`). À compléter pour respecter « chaque extension sur mesure a un README ».

## 6. Études

Sans objet (lot avec code).

## Verdict : Conforme

Le lot applique le brief et les §3.7 / §3.10 / §4.2 / §4.4, rejeu vert, cas du cahier des charges déroulés à la main et concordants. Verdict **Conforme** — ce n'est pas un GO ; la validation visuelle reste à Ced.

Points classés :

- **Bloquant** : aucun.
- **Important** : aucun strict. (Le point le plus proche : l'injection dans la page C-10 échouerait en silence si le markup C-10 changeait — voir §3. Classé mineur car l'état actuel fonctionne et l'ordre des priorités est sûr.)
- **Mineur** :
  1. Injection HTML dans C-10 non couverte par un test d'intégration (§3) ; échec silencieux possible en cas de refonte du markup C-10.
  2. Chemin de rollback de `journal()` non testé (§3).
  3. `README.md` d'`imagine-site` non mis à jour pour la personnalisation (§5).
  4. Documentation (`A-VOIR.md`, `TRANSMISSION.md`) annonce « 1 126 tests / 35 550 assertions » ; le rejeu actuel donne **1 128 / 35 565**. Écart bénin (chiffres de la doc un peu antérieurs), à rafraîchir.

## Décisions techniques, défaut proposé (Hermès applique, Claude arbitre après coup)

- **Catégorie technique — couverture de l'injection C-10.** Défaut prudent proposé : ajouter un contrôle qui rend la vraie page de réglages C-10 (ou un gabarit fidèle) et vérifie que `id="imagine-personnalisation-reglages"` apparaît **entre** l'ouverture et `</form>`. Hermès peut l'appliquer sans attendre.
- **Catégorie technique — README.** Défaut : compléter `wp/plugins/imagine-site/README.md` (rôle des quatre classes, réglage C-10, commandes `c24-*`).

## Pour Imagine (réglages métier)

- **Localité : choix fermés ou texte libre ?** Défaut appliqué par Hermès : **choix fermés exclusivement** (prudent, on ne recueille qu'une étiquette). Question fermée : « La question “localité” doit-elle rester à choix fermés (oui/non) ? » Si un texte libre est voulu, il faudra une spécification distincte (ce lot ne recueille aucun champ libre).

## À arbitrer par Ced (visuel / réel)

- **Placement visuel de la rubrique.** La section Mon compte et la section de réglage C-10 reprennent le squelette B-01, sans style inventé. Question fermée : « Les sections C22/C24 de Mon compte, et la section C10, sont-elles à leur bonne place sous “Enregistrer” ? » Défaut : emplacement actuel inchangé.
- La présentation JSON de l'éditeur de choix dans C-10 est un squelette technique, pas une ergonomie validée.

---

**Fusion non réalisée** (conformément à la consigne). `relectures/C-24/codex.md` existe mais n'a pas été ouvert. La fusion (`corrections/C-24.md`) reste à faire sur demande.
