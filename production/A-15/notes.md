# A-15 — livraison

Paquet unique et final : `preuves/final/`. Contrôle : `python wp/tests/a15/verify.py production/A-15/preuves/final` (25 PASS, code 0). Rejeu isolé : `python wp/tests/a15/run.py --output C:/Users/Ced/AppData/Local/hermes/cache/scratch/a15-rejeu-NOUVEAU`.

Banc A02 strictement fictif : **43 emails réellement déclarés** par WooCommerce 11.1.1, Subscriptions 9.4.1, Memberships 1.30.3 (WordPress 7.0.9), dans chacun des deux magasins classic/HPOS. Comptes actifs exacts par extension, désactivation, destinataire interne personnalisé, sujet/contenu en oui/non, surcharge effective de thème et contenu personnalisé d'un plan Memberships. Les canaris ne sortent pas, y compris dans l'ensemble du paquet. Deux extensions SMTP fictives, active et inactive, versions exactes ; Woo n'est pas confondu avec un transport par son simple formateur MIME.

**8 assertions PHP + 76 natives + 7 gardes runner, toutes vertes**. Aucun PHPUnit revendiqué. PSR-12 strict : code 0, 0 erreur / 0 avertissement, sources finales liées. Appels réellement tentés à wp_mail **et** WC_Email::send bloqués avant le transport canari ; SQL, écritures de fichiers, HTTP et cron également bloqués avant chargement des extensions. Un second passage avec le compte root prouve la transaction READ ONLY ; empreintes de toutes les tables, options/Action Scheduler inclus, et des fichiers du site identiques. Conteneurs sans réseau/ports/montages, supprimés par nom/label et absence relue. `preparer-image.ps1` relancé après les nouveaux tests, code 0.

Décisions prises à défaut : registre WC_Emails natif uniquement (y compris déclarants WCS/Memberships/tiers chargés), pas d'historique d'envoi inventé ; pas de rendu d'email ; personnalisations via réglages natifs et plans Memberships. L'éditeur bloc expérimental, non qualifié par ce lot, est refusé explicitement au lieu de donner de faux « non personnalisé ». Les filtres arbitraires de texte, notifications directes wp_mail et services extérieurs ne sont pas inventés ; limites dans le mode d'emploi. Aucun arbitrage métier ni GO sur le réel.

Deux lignes ajoutées au mode d'emploi de l'audit `wp/tests/a02-audit/README.md`, tous les octets préexistants préservés. Contrat du lot : ses seules deux lignes exactes, présentes une seule fois ; autres lots indépendants ; aucun fichier partagé ou d'autre lot n'est épinglé par le manifeste A15. Dépendances A11/A12 inchangées.


## Contrôle Windows du 26 novembre 2026

Python natif **3.14.7**, deux rejeux complets : UTF-8 (`PYTHONIOENCODING=utf-8`, `PYTHONUTF8=1`) et console **cp1252** (`PYTHONIOENCODING=cp1252`, `PYTHONUTF8=0`), locale Windows cp1252 mesurée. Commandes, version et encodages mesurés : `preuves/final/windows-matrix.json`, `*-environment.json`. Les deux suites natives classic/HPOS et les tests Python propres au lot sont verts ; PHPCS strict et préparation T01 relancée code 0. Un seul paquet final ; essais et précédents hors dépôt.
