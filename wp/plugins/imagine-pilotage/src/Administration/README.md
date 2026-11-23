# Adaptateur administratif C10

Point d’entrée dédié : `wp/plugins/imagine-pilotage/imagine-reglages.php`. Il ne remplace pas `imagine-site.php`. Les anciens menus ne sont pas branchés. La façade réutilise les adaptateurs, impose les clés exactes Accès/Paiement et réserve le groupe Settings API à `manage_options`. L’adaptateur administratif Paiement expose son défaut unique et normalise aussi la lecture de la page ; une première saisie invalide ne retombe plus sur `[]`. Les bibliothèques closes restent inchangées.

Options existantes : `imagine_acces_reglages`, `imagine_c05_reglages`, `imagine_envoi_colonnes_export`. Aucun réglage n’est exposé en REST. Nonce et capacité sont contrôlés par `options.php`, la page vérifie aussi sa capacité. Un domaine invalide conserve sa valeur précédente. Les changements des autres domaines valides ne sont pas annulés.

Journal : hooks `updated_option` et `added_option`, seulement après persistance effective. Un événement par option modifiée, avec qui/ID, quand UTC, avant et après ; les tableaux contiennent l’ensemble des valeurs du domaine. Une option `imagine_reglages_journal_<uuid>` distincte, non autoloadée, par événement. Les refus et les réenregistrements identiques ne produisent pas de faux changement. Les 50 derniers événements sont affichés, sans supprimer les précédents. Les valeurs sont échappées à l’affichage. Le journal n’est ni inviolable ni un substitut à la sauvegarde.

Défauts : Accès fermé aux contenus futurs, PDF robots en extrait, PDF antérieurs fermés ; Paiement marge vide (planification refusée), rejet restant dû, tarif figé au bloc, premier SEPA avec marge ; Envoi neuf colonnes `ExportCsv::COLONNES`. Les huit réglages restent affichés « À confirmer par Imagine » d’après les arbitrages et questions ouvertes ; aucune ouverture de droit implicite.

Si l’insertion du journal échoue, le hook annule l’écriture métier et vérifie la restauration, sans journal récursif ; un message refuse explicitement la modification. Les trois options restent indépendantes. Les mentions ouvertes/tranchées sont pilotées par la table `REGLES_OUVERTES`, aujourd’hui huit règles ouvertes.

Le paywall C08 lit les trois réglages Accès par `deciderContenu()`, point commun article/PDF. Les deux choix PDF gouvernent une décision, pas un nouveau téléchargement protégé. Le choix futur agit effectivement sur l’article témoin. A-VIR est reconnu `virement_non_valide` ; le rôle `imagine_referent_abonnements` est reconnu comme équipe pour la lecture sans lui attribuer de capacité éditoriale. Paiement reste un raccord futur et l’écran l’annonce. L’aperçu fictif C07 utilise le vrai exporteur avec le format relu, sans rien envoyer.

Commandes depuis `C:/Users/Ced/imagine` :

```bash
python -B -m unittest discover -s wp/tests/demo -p test_c10_scope.py -v
python -B wp/tests/demo/c10-unit.py correction-final
python -B wp/outils/demo/c10.py
python -B wp/tests/demo/c10-verifier.py
python -B wp/tests/demo/c10-final.py
```

Le banc PHPUnit utilise exclusivement l’image T01 existante, sans réseau, montage, port ou installation. Voir `production/C-10/notes.md` pour sa création/suppression. La suite `Administration` est déclarée dans `phpunit.xml` : contrats de clés/choix, premier refus Paiement, journal après persistance, KO, no-op, CSV relu, droits et délégation nonce. Les nonces réels sont vérifiés en HTTP.

Le déploiement refuse toute autre cible/URL, ne crée ni ne redémarre de site, ne relance aucun seed B00/C08/C09. Huit fichiers PHP ciblés sont parsés et relus. Le script idempotent ajoute seulement les deux contenus témoins C10 ; l’option `imagine_c10_fixture` est relue et les marqueurs contrôlés. Le cliché protégé exclut ces seuls contenus C10 et le paywall explicitement autorisé, mais conserve les autres contenus, comptes, rôles et bibliothèques. Sessions natives éphémères détruites en fin de test ; aucun cookie, token ou nonce consigné. Réglages restaurés, événements de journal conservés.

Documentation de réception, limites et sources : `production/C-10/`.
