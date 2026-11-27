# B-09 — corrections prioritaires du 27 novembre 2026

Les instructions 1 à 5 de `corrections/B-09.md` sont appliquées, sans élargir le lot. Tous les parcours natifs ci-dessous ciblent exclusivement `imagine-test-demo`.

## R1 — reprise après marqueur, avant option

- `b09-seed.php` recherche directement tous les `post_id` portant `imagine_b09_menu_item`, même détachés et hors option. Il vérifie le type, une seule valeur de marqueur connue, l'absence de rattachement étranger, les conflits d'ID avec l'option et les clés déjà rencontrées ; une ambiguïté est refusée.
- `corrections-red-seed.json` : arrêt réel `exit(73)` dans `added_post_meta`, au marqueur du contact, **avant** l'écriture de l'option et le rattachement. L'ancien code recrée un autre ID ; contrôles `id_marque_hors_option_reutilise=false` et `aucun_orphelin_ni_doublon=false`. État initial restauré.
- `corrections-green-seed.json` : même interruption, reprise dans un nouveau processus, ID marqué conservé, exactement cinq IDs et cinq clés, tous rattachés au seul footer, deuxième rejeu identique. Quatre contrôles verts, restauration des lignes métier (dont l'item initial) et retrait du runner vérifiés.
- `corrections-structure.json` : 21 contrôles verts, dont type étranger, marqueur inconnu, doublon, rattachement étranger et marqueurs multiples. `corrections-mutation-scan.json` retire le scan seulement dans le runner temporaire : les cinq contrôles nouveaux deviennent rouges ; rollback, retrait et état métier relus.

## R2 — suppression partielle et nettoyage reprenable

- `ContactConfidentialite::effacer()` relève les IDs et écrit **avant suppression** un témoin non autoloadé `imagine_contact_effacement_<sha256(adresse normalisée)>`, relu à l'identique ; valeur = seuls IDs à reprendre. Aucune copie du texte ou de l'adresse dans cette option. Une écriture non relue interdit la suppression.
- Après chaque tentative, lecture SQL directe des clés `imagine_contact_*` de l'ID, sans jointure sur le post et sans dépendre du cache. Post absent mais méta présente : `done=false`, `items_retained=true`, pas de succès pour cet item. Une erreur de lecture reste un échec, jamais une liste vide.
- Au prochain appel pour la même adresse, les IDs en attente sont repris même si la méta email a disparu ; seuls les champs `imagine_contact_*` du contact connu sont nettoyés. Le témoin n'est retiré qu'après absence vérifiée ; aucun tiers n'est parcouru. Tranches de 50 conservées.
- `corrections-red-partielle.log` : vrai PHPUnit rouge, 7 tests / 194 assertions / 1 échec, précisément « Une méta personnelle orpheline interdit done ». Le post et l'email ont disparu, le texte survit.
- `corrections-final-unit.log` : 7 tests / 203 assertions verts, dont suppression partielle, nettoyage refusé puis repris, tiers préservé et témoin retiré. `corrections-final-mutant-meta.log` retire seulement la relecture des métas : le même test échoue réellement, sans erreur PHP.
- `corrections-effacement-natif.json` : le vrai cœur WordPress supprime le post et les autres métas, mais un filtre de test court-circuite la suppression de la seule méta texte. Résultat incomplet observé ; un deuxième processus refuse son nettoyage ; un troisième réussit, sans retrouver l'email supprimé. Cinq contrôles verts ; aucune méta ni option de reprise restante, préimage métier restaurée.

## R3 et défauts techniques

Espaces après casts sur les fichiers B-09 neufs, y compris ses doubles de test. Aucun reformatage de lot clos. Duplication Contact/Sujet et succès par comparaison de chaîne **laissés tels quels**, conformément aux deux défauts techniques de la fusion ; aucun fichier Sujet modifié.

## Recette et limites

- `corrections-recette.json` : 31 contrôles HTTP/natifs verts ; vrais POST, antislash jusqu'au détail et à l'export, effacement ciblé, mutation REST/recherche détectée et inversée, aucun transport du contact. Nettoyage et restauration relus.
- `corrections-stable.json` : deux rejeux du seed sur le squelette livré, mêmes IDs/lignes et état métier. Les IDs de pages 3314–3318, footer 38, principal 22 sont conservés.
- Les preuves de première création `pages-reprise-finale.json` sont **historiques** et ne sont plus présentées comme exécution du seed corrigé. La preuve actuelle de la fenêtre retenue est `corrections-green-seed.json` ; il n'est pas nécessaire de recréer les pages livrées.
- Image réellement préparée par `wp/tests/preparer-image.ps1` (`corrections-preparation.json/.log`). Dernier rejeu : `corrections-final-regression.json/.log`, compteurs exacts dans `A-VOIR.md` et `PRET`.
- Nouveau paquet : `corrections-final-V2.json`, commande parent inchangée `python -B production/B-09/verifier.py`. Les anciens reçus et `final-V2.json` restent historiques, sans faux resceau.
- Aucun compte réel, email sortant, paiement, production ou autre site. Pas de texte légal, d'anti-spam, de purge automatique ni de factorisation entre lots. La nouvelle option de reprise est une donnée technique à vider lors d'une future copie : l'import clos n'est pas rouvert ici.
