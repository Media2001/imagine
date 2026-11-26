# C-25 — corrections de la fusion de 00 h 02, 27 novembre 2026

## Résultat courant

Les quatre instructions sont appliquées, sans nouvelle fonction métier :

1. Raccord **C25 seul** aux hooks `added_option`/`updated_option` pour `imagine_retractation_reglages`, événement partagé avant/après, auteur et date UTC. Échec du journal : inverse de la préimage exacte ou de l’absence initiale, puis readback ; pas de journal de restauration. La préimage interne seule évite sa renormalisation par le sanitizer.
2. Bouchons corrigés **avant le rouge** : `add_comment_meta` déséchappe réellement et `wp_unslash` est récursif ; écriture de `wp_slash($record)` et comparaison avec l’original. Motif HTTP `C:\dossier\fichier` et doubles antislashs relus à l’identique dans la métadonnée et le callback enregistré de l’export natif C21.
3. Section C25 ajoutée au README du plugin : parcours, deux réglages, commandes hors ligne/live et limites.
4. Refus prudent de `delete_user` par `wp_die` en panne SQL persistante documenté ; aucun comportement de suppression ajouté.

C10/C21 sont restés clos, sans modification ; injection HTML actuelle conservée, **pas de hook neuf dans C10**. Borne finale incluse, trace anti-doublon dépersonnalisée et défaut 14 jours/paiement inchangés. Aucun délai légal ni obligation juridique validés. C23/C26 et les autres lots ne sont ni modifiés ni rescellés.

## Preuves actuelles (les précédentes restent historiques)

- `corrections-R2-red-V2.{json,log}` : vrai refus de la demande avec antislash, après correction des bouchons ; `corrections-R2-green-V2` : correction verte.
- `corrections-R1-red-V2.{json,log}` : création du réglage sans événement, défaut reproduit ; `corrections-R1-green-V2` : correction verte.
- `canonique-corrections002-V2.{json,log}` : **10 tests, 172 assertions**, zéro échec/erreur/ignoré ; nouveaux tests nommés dans le JUnit.
- `mutations-corrections002-V2.json` : **15/15 mutations détectées**, dont perte d’antislash, absence de journal, inverse supprimée et sanitizer de préimage retiré. Seulement des copies jetables hors réseau, aucune mutation du site pour ces témoins.
- `image-corrections002-V2.{json,log}` : véritable préparation officielle, image vérifiée après les nouveaux tests. Les lignes PowerShell `RemoteException` accompagnent ici la progression Docker sur stderr ; code final observé **0**, vérification d’image présente, ce ne sont pas des tests inventés.
- `regression-corrections002-V2.{json,log}` : **1151 tests, 36062 assertions**, zéro échec/erreur/ignoré ; **20 outils, 521 contrôles**, zéro échec. Isolation T01 et nettoyage du runner vérifiés.
- `recette-corrections002-V2.json` : **23 contrôles HTTP + 34 natifs = 57**, tous vrais. Vrais POST `options.php` : création, modification et deux pannes SQL distinctes d’INSERT du journal ; les valeurs persistées sont relues dans une autre exécution. Le groupe de la recette est volontairement restreint à la seule option C25 par un MU temporaire, afin de ne pas soumettre ni muter les réglages des autres lots ; le sanitizer, les hooks, le nonce et le cœur `options.php` restent natifs. La page C10 affiche les événements.
- Même recette : deux confirmations HTTP concurrentes et une seule note, abandon, titulaire/hors délai/nonce, état métier et accès conservés ; motif à antislash jusqu’à l’export C21 enregistré, panne du journal de demande avec **rollback effectif note+métadonnée**, panne SQL d’export puis reprise et effacement sans tiers.
- Préimages privées **durables avant sessions/mutations**, restaurées depuis leurs octets et SHA-256. Utilisateurs, métadonnées, commandes classiques/HPOS, notes, options métier et calendrier/actions métier relus identiques ; observateur MU et runtime de recette supprimés. Aucun remboursement, annulation ou fermeture d’accès ; aucun transport extérieur laissé passer.
- `livraison-corrections002-V2.json` lie les sources courantes, les reçus neufs, les documents et le seul contrat de section C25 du README partagé. `PRET` dépend du vérificateur, pas du simple achèvement du script.

## Commandes réellement exécutées

Depuis `C:/Users/Ced/imagine` :

```text
python -B wp/outils/demo/c25.py local canonique-corrections002-V2
python -B wp/outils/demo/c25-mutations.py mutations-corrections002-V2
python -B wp/outils/demo/c25.py gates prepare image-corrections002-V2
python -B wp/outils/demo/c25.py gates regression regression-corrections002-V2
python -B wp/outils/demo/c25-recette.py recette-corrections002-V2
python -B wp/outils/demo/c25-finaliser.py sceller
python -B wp/outils/demo/c25-finaliser.py verifier
```

Les reçus sont immuables : pour rejouer les générateurs, choisir une étiquette neuve. Les deux commandes `gates` invoquent réellement `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1` et `wp/tests/rejouer.ps1` respectivement. La dernière commande vérifie le paquet livré sans accès au site. Aucun Git ni installation sur l’hôte.

## Incident de harnais, sans préimage perdue

Le premier diagnostic a échoué au transport de l’inverse : la liste complète de **2552 noms d’options**, environ 143 ko, dépassait la taille d’argument du transport Linux. La sélection de nettoyage est désormais bornée par l’`option_id` maximal de la préimage et par le contenu C25 de l’événement ; aucun journal préalable n’est supprimé. La reprise depuis la préimage durable d’origine a ensuite omis les métadonnées admin dans son premier appel (portée `locals()` de l’appel de reprise) ; elles ont été restaurées explicitement depuis **la même préimage**, jamais reconstruites. Les deux reçus intermédiaires de reprise conservent leurs échecs.

Readback après cette reprise : état métier complet identique et toutes les lignes utilisateurs/options/commandes classiques/HPOS exactes. La comparaison trop large des tables Action Scheduler signalait uniquement le remplacement d’un `wcs_report_update_cache` technique (9119 → 9120), **aucune action métier** : le calendrier métier est strictement identique. Conformément à l’arbitrage de proportion du 26/11, aucun rejeu ni bricolage de cache n’a été entrepris pour cela. `recette-corrections002-diagnostic2-V2.json` puis la recette finale neuve ont réexécuté le parcours complet et restauré l’état métier avec tous leurs readbacks verts. Ces incidents ne sont pas requalifiés en premières passes vertes.

Le rapport historique `NOTE.md` décrit la livraison précédente ; le présent fichier et `A-VOIR.md` désignent les preuves courantes. Validation visuelle de Ced, choix métier et conseil juridique restent dus ; PRET n’est ni une clôture ni un GO sur le réel.
