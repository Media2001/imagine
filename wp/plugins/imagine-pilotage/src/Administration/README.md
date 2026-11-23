# Adaptateur administratif C10

Point d’entrée dédié : `wp/plugins/imagine-pilotage/imagine-reglages.php`. Ce fichier ne remplace pas le bootstrap B00 `imagine-site.php`. Les trois anciens adaptateurs restent inchangés ; leurs menus ne sont pas branchés. La façade appelle leurs méthodes de lecture/validation, ajoute le refus strict des clés/choix Accès et des clés Paiement, et expose un groupe Settings API natif réservé à `manage_options`.

Options existantes : `imagine_acces_reglages`, `imagine_c05_reglages`, `imagine_envoi_colonnes_export`. Aucun réglage n’est exposé en REST. Nonce et capacité sont contrôlés par `options.php`, la page vérifie aussi sa capacité. Un domaine invalide conserve sa valeur précédente. Les changements des autres domaines valides ne sont pas annulés.

Journal : hooks `updated_option` et `added_option`, seulement après persistance effective. Un événement par option modifiée, avec qui/ID, quand UTC, avant et après ; les tableaux contiennent l’ensemble des valeurs du domaine. Une option `imagine_reglages_journal_<uuid>` distincte, non autoloadée, par événement. Les refus et les réenregistrements identiques ne produisent pas de faux changement. Les 50 derniers événements sont affichés, sans supprimer les précédents. Les valeurs sont échappées à l’affichage. Le journal n’est ni inviolable ni un substitut à la sauvegarde.

Défauts : Accès fermé aux contenus futurs, PDF robots en extrait, PDF antérieurs fermés ; Paiement marge vide (planification refusée), rejet restant dû, tarif figé au bloc, premier SEPA avec marge ; Envoi neuf colonnes `ExportCsv::COLONNES`. Les huit réglages restent affichés « À confirmer par Imagine » d’après les arbitrages et questions ouvertes ; aucune ouverture de droit implicite.

L’aperçu fictif C07 n’apparaît que sur `local` + `imagine-test-demo` ; il passe réellement le format relu au moteur CSV existant. Il n’envoie rien. Les raccords C08 et les modèles C05/C06/C07 ne sont pas modifiés.

Commandes depuis `C:/Users/Ced/imagine` :

```bash
python -m unittest discover -s wp/tests/demo -p test_c10_scope.py -v
python wp/outils/demo/c10.py
python wp/tests/demo/c10-verifier.py
python wp/tests/demo/c10-final.py
```

Le déploiement refuse toute autre cible et URL, ne crée ni ne redémarre de site, ne relance aucun seed, téléverse cinq fichiers d’administration et une recette, parse leur PHP puis relit leurs SHA-256 exacts. Les tests HTTP créent des sessions natives éphémères, sans mot de passe, réservées aux comptes de la démonstration ; ils les détruisent en fin de test et ne consignent ni cookies, ni tokens, ni nonces. Les réglages sont restaurés et les vrais événements de journal sont conservés.

Documentation de réception, limites et sources : `production/C-10/`.
