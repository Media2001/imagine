# Doctrine — projet Imagine

Révision : **11/11/2026** (création).

Ces règles s'appliquent à tous les agents. En cas de contradiction entre une consigne et la doctrine, la doctrine l'emporte : l'agent le signale dans son rapport au lieu de trancher.

## 1. Ce qui fait foi

1. `docs/cahier-des-charges-v3.1.pdf` (texte : `docs/cahier-des-charges-v3.1.txt`).
2. `docs/decisions.md`, qui précise ou corrige le cahier des charges quand Ced a tranché.
3. Le brief du lot.

Un agent ne comble jamais un silence du cahier des charges par une invention. Il choisit l'interprétation la plus proche du texte, l'applique, et l'écrit dans son rapport (« j'ai compris X »). Si le choix engage de l'argent, des droits d'accès ou la comptabilité, il ne choisit pas : il pose la question dans « À arbitrer par Ced ».

## 2. Périmètre

Ced réalise toute la production technique. Le **design** (maquettes) et le **référencement** (plan, mots-clés, plan de redirections) sont fournis par d'autres : on implémente leurs spécifications, on ne les invente pas. Odoo est le périmètre de Step : notre travail s'arrête à ce que le connecteur transmet.

## 3. Interdits

- **Secrets** : aucun mot de passe, clé, token ou fichier de configuration dans le dépôt.
- **Données réelles** : aucun abonné, aucun export Access, aucun contact Brevo, aucun client Stripe, ni dans le dépôt ni dans un prompt. Les tests utilisent des jeux fictifs (`wp/tests/fixtures/`), avec des noms manifestement inventés et des adresses en `@example.org`.
- **Comptes réels** : aucun accès au site actuel, à Stripe, PayPal, Brevo, Odoo ou CoopHub sans GO écrit de Ced nommant la tâche. Stripe et PayPal : mode test uniquement.
- **Achats** : aucune licence, aucun service payant.
- **Déploiement** : rien en préproduction ni en production sans GO écrit.
- **Git** : un worker ne fait jamais d'opération Git. Seule la tâche de synchronisation en fait.

## 4. Comment on construit

- **Le standard d'abord.** Avant d'écrire du code, vérifier ce que font déjà WordPress, WooCommerce, Subscriptions, Memberships et les extensions retenues (§4.1 du cahier des charges), en citant la documentation officielle. Le sur-mesure se limite à ce qu'elles ne font pas.
- **Les tests d'abord.** Chaque règle métier arrive avec ses tests automatisés. Les parcours de réception du chapitre 5 deviennent des tests de bout en bout. Un lot sans tests n'est pas `PRET`.
- **La logique métier hors de WordPress.** Les règles (numéros, échéances, droits) sont écrites en PHP pur, testables sans base ni WordPress ; une couche fine les branche sur WooCommerce.
- **Paywall côté serveur.** Le texte réservé n'est jamais dans la réponse envoyée à un visiteur non autorisé : page, REST, flux, oEmbed, recherche, aperçus. Un test d'étanchéité le vérifie.
- **Pas de constructeur de pages.** Thème sur mesure, HTML sémantique, aucun script superflu : les seuils du chapitre 5 (Lighthouse mobile, WCAG 2.1 AA) sont des obligations de résultat.
- **Idempotence.** Tout ce qui part vers Odoo passe par une file d'attente ; un événement rejoué ne crée pas de doublon.

## 5. Conventions de code

- PHP 8.2 minimum, `declare(strict_types=1)`, PSR-12, espace de noms `Imagine\`.
- Préfixe `imagine_` pour tout ce qui est global dans WordPress (options, hooks, tables, métadonnées).
- Textes de l'interface en français, passés par les fonctions de traduction.
- Aucune modification du code d'une extension tierce : uniquement des hooks.
- Chaque extension sur mesure a un `README.md` : ce qu'elle fait, ses réglages, comment lancer ses tests.

## 6. Tracer les écarts

Toute demande qui sort du cahier des charges, toute contradiction interne au cahier des charges et tout blocage dû à un tiers (Imagine, Step, CoopHub, hébergeur) est signalé dans le rapport. Claude le reporte dans `docs/ecarts.md` avec sa date.
