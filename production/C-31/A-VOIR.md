# C-31 — Corrections 1–5 : adresses à l'inscription

**État : corrections locales vérifiées ; PRET absent.** Le parent doit encore réaliser l'image et le rejeu globaux uniques après C32 puis sceller la réception. Les reçus `*-final-V2.*` sans préfixe `corrections-` et `reception-V2.json` sont historiques, pas l'acceptation actuelle.

## À ouvrir — démonstration fictive seulement

Base : `http://192.168.129.32:8085`.

- Réglages : `/wp-admin/options-general.php?page=imagine-domaines-refuses` → un domaine exact par ligne ; vide = aucune restriction ; aucune source externe. L'écran et le ton du message restent à valider visuellement, sans demande d'arbitrage technique.
- Domaines de démonstration : `jetable-fictif.example.org`, `temporaire-fictif.example.org`, `usage-unique-fictif.example.org`. Comparaison sans casse ; `sub.jetable-fictif.example.org` n'est pas hérité, il faut une ligne explicite. ASCII/punycode ; liste invalide rejetée atomiquement.
- Inscription WP : `/wp-login.php?action=register` ; Woo : `/my-account/`. L'inscription est ouverte **temporairement par la recette**, puis ses réglages exacts sont restaurés. La recette ne l'ouvre pas durablement.
- Mon compte : `/my-account/edit-account/`. Trois vrais POST du formulaire natif : adresse inchangée sur un domaine ajouté après création → sauvegarde du prénom témoin effective ; changement interdit → erreur et ni email ni prénom témoin écrits ; changement autorisé → email et billing_email effectivement écrits. Utilisateur de recette ensuite supprimé.
- Commande : `/checkout/`. La recette ouvre temporairement la boutique Woo et l'inscription, ajoute le produit B04 fictif existant au panier depuis le navigateur, puis soumet le vrai endpoint Store API avec son nonce et `create_account=true` : HTTP 400, message neutre, aucun compte ni commande ni adresse refusée en base après la requête. Paramètres, sessions, Cart et effets natifs de rendu restaurés.

**Captures actuelles** : `corrections-browser-final-V2.png` ; `corrections-compte-final-V2-inchange.png`, `corrections-compte-final-V2-refuse.png`, `corrections-compte-final-V2-autorise.png` ; `corrections-commande-final-V2.png`.

Le navigateur de recette désactive JavaScript et toute ressource tierce. La capture checkout montre donc le squelette natif Blocks, pas un formulaire hydraté ni un clic sur son bouton : le POST de commande est exécuté par HTTP sur la vraie Store API. Les trois sauvegardes Mon compte et les deux inscriptions sont, elles, de vrais clics/formulaires DOM. Ce n'est pas une validation du design général du site.

## Ce qui a changé

1. Câblage rejouable hors WordPress : hooks/signatures, troisième argument email, garde admin mais pas AJAX public, liste vide/domaine libre, Mon compte inchangé/changé, journal/restauration. Les nouveaux `*Test.php` sont découverts par le `phpunit.xml` existant ; aucun runner partagé modifié.
2. Assertion Mon compte vacante supprimée : vrais POST, relectures indépendantes, témoins positifs de sauvegarde et suppression du compte de recette.
3. **Persistance effectivement reproduite avant correction**, dans `wp_woocommerce_sessions.session_value`, sur checkout classique **et** Blocks/Store API. Validation avancée avant `update_session` et avant le callback REST du checkout, sans filtre global de création de comptes. Les invités sans création de compte et les comptes déjà connectés ne sont pas concernés.
4. Blocs PSR-12 corrigés dans les deux classes visées et instructions du runtime séparées. PHPCS ciblé : zéro erreur (avertissements de longueur désactivés explicitement, pas de reformatage partagé).
5. Recettes native/navigateur et suite du paquet rejouées après le dernier changement ; fermeture globale déléguée au parent comme demandé.

## Preuves finales réelles

| Preuve | Résultat |
|---|---|
| `corrections-cible-final-V2.json` / `.log` | 9 tests C31, 64 assertions, PASS |
| `corrections-suite-final-V2.json` / `.log` | paquet imagine-site complet : 267 tests, 3267 assertions, PASS |
| `corrections-native-final-V2.json` | 46 contrôles, PASS ; transaction restaurée exactement |
| `corrections-browser-final-V2.json` | 16 contrôles d'inscription WP/Woo, PASS |
| `corrections-compte-final-V2.json` | 29 contrôles, trois vraies sauvegardes, PASS |
| `corrections-commande-final-V2.json` | 13 contrôles, panier réel et vrai POST Store API, PASS |
| `corrections-style-final-V2.json` / `.log` | PHPCS PSR-12 ciblé : exit 0, zéro erreur |
| `corrections-standard-V2.json` | contrats des sources officielles installées WP 7.0.9 / Woo 11.2.2 |

La recherche d'absence parcourt **47 tables / 187 colonnes textuelles**, dont sessions, tables HPOS, anciens posts/postmeta, users/usermeta et options/journaux. Témoins positifs réellement déposés : options, usermeta, session et commande HPOS ; six colonnes détectées. Mutation « filtre Woo retiré → compte créé » conservée. Aucun compte créé par un refus ; nettoyage/relecture du témoin de mutation. Les adresses d'essai et témoins sont exclusivement fictifs en `example.org`.

Les recettes HTTP restaurent profils, rôles, actions planifiées, options métier et sessions. Seuls les caches de rendu B13/B15 et `_transient_wp_styles_for_blocks` sont admis comme volatils. La migration spontanée de Cart et la note native Woo du premier affichage ont été restaurées depuis leurs vraies préimages : `corrections-cart-restaure-V2.json`, puis restauration intégrée au runner de commande.

**Limites explicites** : wp-login tente deux appels de traduction natifs, bloqués et identifiés ; Woo/C31 ne font pas d'appel HTTP. Un changement d'adresse autorisé peut déclencher la notification native WordPress : son envoi est bloqué par la garde démo. Aucun email n'est envoyé. Aucun test d'étanchéité C26 ni lot voisin modifié.

## Finalisation par le parent

Lire `FINALISATION-V2.md`. Le README partagé n'a pas été modifié : section actualisée à intégrer depuis `README-fragment-V2.md`.

```text
python -B production/C-31/verifier.py --pre-final --live
```

Cette commande est verte et annonce volontairement `PRET: false`. Le vérificateur final et `finaliser.py` exigent les nouveaux reçus image/rejeu ; ils ne réutilisent pas le vert historique. Aucun Git, aucun verrou touché, aucun réel, aucune préparation d'image ni rejeu global lancés par l'enfant C31.

