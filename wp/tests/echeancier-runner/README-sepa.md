# C-05 — marge de confirmation du premier SEPA

Remise : `production/C-05/sepa-22nov-1700.md`. Preuves finales : `production/C-05/replays/sepa-22nov-1715-final/`. TDD et premier passage : `replays/sepa-22nov-1700/` (historique, intact). Le banc `corrections.py` et ses moteurs PHP/Docker restent inchangés ; `sepa.py` importe ce banc, protège les deux reçus de préparation sous des noms distincts et remplace uniquement le vérificateur de remise (Q1 n’est plus ouverte).

PHP, Composer, PHPUnit et WordPress s’exécutent **seulement dans les conteneurs possédés**. Python Windows ne fait que transport, hashes et lecture des preuves. Aucun outil installé sur l’hôte, pas de Git, d’archive Imagine, de compte réel, de passerelle ni de licence activée. Les fixtures utilisent des identités inventées et `@example.org`.

## Commandes réellement utilisées

Depuis `C:/Users/Ced/imagine`, nouveau paquet final :

```bash
IMAGINE_C05_PACKET=sepa-22nov-1715-final python -B wp/tests/echeancier-runner/sepa.py prepare
IMAGINE_C05_PACKET=sepa-22nov-1715-final python -B wp/tests/echeancier-runner/sepa.py run --name final
IMAGINE_C05_PACKET=sepa-22nov-1715-final python -B wp/tests/echeancier-runner/sepa.py e2e-prepare
IMAGINE_C05_PACKET=sepa-22nov-1715-final python -B wp/tests/echeancier-runner/sepa.py e2e --name final-e2e
IMAGINE_C05_PACKET=sepa-22nov-1715-final python -B wp/tests/echeancier-runner/sepa.py close
IMAGINE_C05_PACKET=sepa-22nov-1715-final python -B wp/tests/echeancier-runner/sepa.py e2e-close
IMAGINE_C05_PACKET=sepa-22nov-1715-final python -B wp/tests/echeancier-runner/sepa.py verify
```

Le premier paquet a été préparé/fermé avec `corrections.py` et `IMAGINE_C05_PACKET=sepa-22nov-1700`. Ses cycles TDD ont exécuté exactement :

```text
python -B wp/tests/echeancier-runner/corrections.py run --name <reçu> --filter ConfirmationPremierSepaTest
```

Avec le même préfixe d’environnement et successivement `red-sepa-defaut`, `green-sepa-defaut`, `red-sepa-positions`, `green-sepa-positions`, `red-sepa-date`, `green-sepa-date`, `red-sepa-sans-marge`, `green-sepa-sans-marge`, `red-sepa-confirmation`, `green-sepa-confirmation`, `red-sepa-marge-obligatoire`, `green-sepa-marge-obligatoire`, `red-sepa-chronologie`, `green-sepa-chronologie`, puis `green-sepa-bornes`. Réglage admin : `e2e --name red-sepa-admin` puis `e2e --name green-sepa-admin`. Commande sous-jacente réelle dans chaque reçu JSON : `composer test -- --filter ConfirmationPremierSepaTest`. Le premier paquet conserve aussi `green-standard`, `final` et `final-e2e`, sans les présenter comme la remise finale après changement de documentation.

Le reçu RED admin échoue précisément sur `sepa_admin_field_present`, pas sur une installation ratée. Les RED méthode absente/nullabilité et propriété absente correspondent aux fonctionnalités encore manquantes ; les GREEN finaux n’ont aucune alerte. Le dernier groupe de cas verrouille les jours civils, les frontières de clôture et l’absence de régression, déjà corrects : aucune fausse phase RED fabriquée pour ces cas.

## Rejeu sûr

Choisir un paquet neuf ; aucune preuve existante n’est écrasée. Le paquet TDD par défaut reste `sepa-22nov-1700`, configurable par `IMAGINE_C05_TDD_PACKET`. Fermer chaque runner même après échec :

```bash
export IMAGINE_C05_PACKET=sepa-relecture-unique
python -B wp/tests/echeancier-runner/sepa.py prepare && (
  python -B wp/tests/echeancier-runner/sepa.py run --name final
  result=$?
  python -B wp/tests/echeancier-runner/sepa.py close || result=1
  exit "$result"
) &&
python -B wp/tests/echeancier-runner/sepa.py e2e-prepare && (
  python -B wp/tests/echeancier-runner/sepa.py e2e --name final-e2e
  result=$?
  python -B wp/tests/echeancier-runner/sepa.py e2e-close || result=1
  exit "$result"
) &&
python -B wp/tests/echeancier-runner/sepa.py verify
unset IMAGINE_C05_PACKET
```

`verify` lie sources actuelles, six suites JUnit dont les 19 cas SEPA, RED historiques, deux stockages, deux positions persistées/relues, dates/effets, chronologie des huit positions, inventaire protégé et absence exacte des deux runners. Il ne relance pas PHP et ne vaut pas relecture indépendante. Après scellement, il compare au reçu existant sans l’écraser. Le dépôt de PRET est lié séparément dans `remise.json` pour éviter une empreinte circulaire.

## Ce qui est prouvé, et ce qui ne l’est pas

La Settings API réelle enregistre le nouveau choix, rend les deux options et le choix sélectionné, conserve l’ancienne option sur saisie invalide, fournit une configuration utilisée par la projection pure. Ancienne clé absente : `avec_marge`. Même durée obligatoire qu’avant ; aucun nouveau nombre choisi. Sans confirmation effective, aucune date de paiement ; avec marge le seuil est `max(confirmation, commande + jours civils)`, sans marge la confirmation seule. Les charges/numéros C01 ne sont pas déplacés.

Le banc active explicitement l’adaptateur sans modifier le bootstrap partagé. Pas de sauvegarde HTTP ou de validation visuelle revendiquée. Vrai Subscriptions classique/HPOS : même preuve manuelle de huit positions par scénario, actions futures possédées exécutées explicitement une à une ; aucune file globale. Confirmations locales Woo à l’heure réelle, pas d’horloge changée ni de banque simulée comme réelle. Aucun effet ajouté sur montants, dette, accès, expédition, Odoo ou renouvellements SEPA.

Deux conteneurs par paquet de vérification, sans montage, volume, port ni privilège ; capacités retirées. Réseau du standard déconnecté avant tests (préparation Composer publique verrouillée seulement), réseau `none` dès création e2e ; MariaDB socket Unix et emails/HTTP bloqués. Suppression par noms exacts et diagnostic Docker d’absence. Les paquets historiques ne sont jamais réécrits pour prétendre qu’ils valident les nouveaux octets.
