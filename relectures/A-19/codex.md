# Relecture indépendante Codex — A-19

Date : 26 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine, grille, brief A-19, cahier des charges §4.3 et décisions du dépôt. Examen des sources A-19, de leurs dépendances de confinement et du paquet `production/A-19/preuves/final`. Le rapport de Claude n’a pas été lu. Aucun fichier autre que ce rapport n’a été modifié.

## 1. Conformité

Les indicateurs demandés sont présents : croisement par plan et états, absence de lien distinguée du lien pendant, comptes portant plusieurs actifs, références de paiement absentes ou inconnues, échéances dépassées, absence de commande payée et renouvellement manuel par passerelle. Les définitions accompagnent les nombres. Le lot ne corrige ni lien ni état et ne décide pas des droits. Les livrables et le paquet unique sont présents.

**A19-CX-01 — Important — La commande livrée dans le mode d’emploi de l’audit est systématiquement refusée.**

- **Localisation :** `wp/outils/bascule/a19/confine.py:16`.
- **Problème :** le contrôle des arguments impose `--as-of`. Or la commande d’intégration livrée dans `wp/tests/a02-audit/README.md:75` ne le fournit pas, et `wp/outils/bascule/a19/README.md:24` le décrit explicitement comme facultatif. Le défaut UTC prévu dans `Command.php` est donc inaccessible par le lanceur obligatoire.
- **Reproduction exécutée :** `python -B wp/outils/bascule/a19/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/coherence-date` termine avec le code 1 et uniquement `A19_USAGE` sur stderr. Le refus précède toute résolution de chemin : disposer d’une vraie copie vérifiée ne change pas le résultat.
- **Correction proposée :** rendre obligatoires les trois seuls arguments de chemins dans le lanceur et laisser le PHP fixer son instant UTC par défaut une seule fois. Ajouter un test du parcours sans `--as-of`, puis rejouer le parcours natif avec et sans date explicite. Conserver les refus des dates invalides et des arguments répétés.
- **Catégorie :** technique. **Défaut proposé :** appliquer le comportement facultatif déjà documenté et implémenté côté PHP ; aucune décision métier ni intervention de Ced nécessaire.

## 2. Exactitude métier

Le §4.3 impose la conservation des comptes, abonnements, moyens de paiement et historiques ; il ne donne pas d’exemple chiffré de cohérence. Les cas déroulés ci-dessous reprennent donc les situations exigées par le brief, sans inventer de règle d’accès.

1. **Couple cohérent et double abonnement.** Dans le banc fictif, un compte porte deux abonnements actifs, mais une seule adhésion est liée au premier. Le tableau croisé doit compter un lien actif/actif ; le second abonnement doit être compté sans adhésion ; le compte doit contribuer pour un, et non deux, au nombre de comptes à plusieurs abonnements actifs. C’est le résultat de la lecture de `Analysis.php` et des résultats classic/HPOS livrés. Les commandes parent et de renouvellement payées évitent de classer ces deux abonnements parmi les actifs sans paiement.
2. **Adhésion autonome et abonnement supprimé.** Une adhésion active sans lien contribue à `memberships_without_subscription`. Une autre dont le lien vise un abonnement supprimé contribue uniquement à `memberships_missing_subscription`, sans créer de couple dans le tableau croisé. Ces deux situations restent distinctes dans le code et dans les preuves.
3. **Échéance et référence inconnue.** À égalité exacte avec l’instant de référence, un prochain paiement n’est pas passé ; une date nulle ne l’est pas non plus. Une passerelle sans schéma ni jeton exploitable contribue aux références inconnues, pas aux références absentes. Ces frontières sont explicites dans le code et couvertes par les tests livrés. Le passage d’année utilise la comparaison d’instants UTC, sans calcul calendaire particulier.

Les interprétations sensibles sont signalées : état strictement actif, drapeau manuel enregistré, absence de rapprochement par identité et présence d’une référence distincte de sa validité. Aucun autre défaut de comptage établi à la lecture.

## 3. Tests

Exécutions effectuées durant cette relecture, sans création de fichiers de preuve :

| Vérification | Résultat |
|---|---|
| `python -B wp/tests/a19/verify.py production/A-19/preuves/final` | Code 0 ; tous les contrôles passent, dont correspondance exacte des sources et manifeste du paquet |
| `python -B wp/tests/a19/test_launcher.py`, avec `PYTHONUTF8=0` et `PYTHONIOENCODING=cp1252` | 3 tests réussis, code 0 |
| Même suite avec `PYTHONUTF8=1` et `PYTHONIOENCODING=utf-8` | 3 tests réussis, code 0 |
| Commande du mode d’emploi de l’audit, sans date | Refus reproduit : `A19_USAGE`, code 1 — A19-CX-01 |

**Limite du rejeu indépendant :** `wp/tests/a19/run.py:28` crée obligatoirement un dossier de sortie et écrit ensuite plusieurs fichiers ; `unit.php:57` écrit également son résultat. Pour respecter strictement l’écriture limitée à ce rapport, je n’ai pas relancé le banc PHP/WordPress ni la préparation d’image. Les résultats natifs suivants sont ceux du paquet fourni, contrôlé en lecture seule, et non ceux d’un nouveau banc exécuté par Codex : par contexte, 9 assertions PHP, 98 assertions natives classic/HPOS et 7 contrôles du lanceur, tous annoncés réussis.

Les preuves couvrent notamment le rejeu identique, les empreintes des tables et fichiers, les canaris, les refus de configuration/drop-ins/liens symboliques et les tentatives d’écriture ou de communication. Les attentes de comptage sont explicites et ne sont pas calculées par la fonction testée. Le parcours documenté sans date est absent : les invocations natives fournissent toutes `--as-of`, ce qui explique A19-CX-01 malgré la suite verte.

## 4. Sécurité et données

Aucun secret ni donnée personnelle réelle repéré dans les fichiers du lot examinés. Les comptes de test portent des noms manifestement fictifs et des adresses `@example.org`. Les sorties examinées contiennent des agrégats, états, identifiants de plans et de passerelles ; les identifiants internes de comptes, abonnements et commandes ne sont pas projetés.

Le lanceur réutilise le confinement A12 et le démarrage en lecture seule A11. Les codes d’exception PHP sont limités à une liste littérale ; les détails de refus A11 n’exposent que les noms techniques fermés des drop-ins. Les fichiers de rapport sont créés avec les permissions privées prévues. L’égalité des empreintes avant/après est vérifiée dans le paquet livré, avec la limite de rejeu indiquée en section 3.

Pas d’interface Web ajoutée : nonces, échappement HTML et contrôle du paywall ne sont pas des parcours de ce lot. Aucun accès à un site, une base, un compte ou une API externe durant cette relecture.

## 5. Doctrine

Le calcul est isolé en PHP pur dans `Analysis.php`, et la projection native dans `Inventory.php`. Les fichiers PHP du lot déclarent les types stricts ; les classes de production utilisent l’espace de noms `Imagine`. Le README présente le standard et les limites. Aucun correctif d’extension tierce, mécanisme de paiement ou règle de droits parallèle n’est introduit. Le contrôle de style fourni est vert et rattaché aux sources actuelles par le vérificateur.

Pas de question métier ouverte ni de choix touchant au réel à soumettre. La correction technique proposée pour A19-CX-01 suffit à traiter le défaut établi.

## 6. Études (lots sans code)

Non applicable comme catégorie de lot : A-19 livre du code. Les dix lignes demandées sur le standard sont présentes et renvoient à une page officielle ainsi qu’à des méthodes du code installé. `sources-officielles.json` conserve une URL et des empreintes, mais pas les passages documentaires ni le code tiers correspondant. **Doute documentaire limité :** cette relecture locale ne confirme pas indépendamment le contenu de ces sources externes ; aucun site n’a été consulté.

## Verdict

**À corriger.**

- **Bloquant :** aucun défaut de ce niveau établi.
- **Important :** **A19-CX-01**, argument `--as-of` imposé par le lanceur, rendant inutilisable la commande fournie dans le mode d’emploi de l’audit.
- **Mineur :** aucun point supplémentaire retenu.

Ce verdict repose sur la lecture du code, les tests Python rejoués et le contrôle du paquet fourni ; le banc natif n’a pas été réexécuté indépendamment. **Ce verdict n’est pas un GO.**
