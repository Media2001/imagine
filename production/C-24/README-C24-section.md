## C-24 — personnalisation facultative locale

`PersonnalisationRegles` valide les questions et choix fermés, les réponses datées et la conjonction de transmission en PHP pur. `Personnalisation` raccorde trois formulaires distincts au dashboard WooCommerce : réponses, effacement, consentement. `PersonnalisationReglages` ajoute les questions au formulaire Settings API **C10 existant**, sous son bouton sans déplacement, réserve définitivement les identifiants et journalise les changements. `PersonnalisationConfidentialite` ajoute les callbacks natifs d'export/effacement sans modifier C21.

Réglage : `imagine_personnalisation_questions` (identifiant, titre, choix simple/multiple, liste JSON de choix fermés). Métadonnées : `imagine_personnalisation_reponses` (choix et `date_utc` par question), `imagine_personnalisation_consentement` (`accord`, `date_utc`), séparées des préférences newsletters. Répondre ne vaut pas consentir. Compte sans email : réponses locales possibles, aucune case de consentement et projection fermée. Les réserves techniques d'identifiants survivent à l'effacement.

`Personnalisation::attributsConnecteur($id)` est la seule projection prévue pour le futur connecteur : consentement distinct explicite **ET** au moins une newsletter active choisie avec `origine=lecteur` **ET** compte admissible à l'email. `defaut_creation`, origine absente ou inconnue ne comptent jamais. `imagine_personnalisation_attributs_modifies` est émis après sauvegarde admissible, sans écouteur livré ; `imagine_personnalisation_apres_inscription_achat` reste un emplacement nommé non raccordé. Aucun transport Brevo, email ou tâche planifiée nouvelle.

En cas d'échec réel d'insertion du journal C10, seule la préimage interne validée, sous drapeau privé et égalité stricte de valeur, évite la validation des identifiants réservés. L'option restaurée est relue ; une nouvelle saisie réservée reste refusée. Les tests retirent séparément une question puis un choix avec refus SQL du journal, et contrôlent préimage persistée et absence de 500, aussi par deux vrais POST `options.php`.

Depuis la racine du dépôt, contrôle local hors réseau, sans site ni mutation :

```bash
PYTHONIOENCODING=utf-8 python -B production/C-24/verifier-fusion2050-V2.py
python -B wp/outils/demo/c24-gates.py prepare nouvelle-preparation-V2
python -B wp/outils/demo/c24-gates.py regression nouvelle-regression-V2
```

Recettes **nécessitant le seul site fictif gardé `imagine-test-demo`**, données métier restaurées et snapshots durables privés avant les sessions/mutations ; choisir des étiquettes neuves terminées par `-V2` :

```bash
python -B wp/outils/demo/c24.py rules nouvelles-regles-V2
python -B wp/outils/demo/c24.py runtime nouveau-natif-V2
python -B wp/outils/demo/c24-corrections.py journal-question nouveau-journal-question-V2
python -B wp/outils/demo/c24-corrections.py journal-choix nouveau-journal-choix-V2
python -B wp/outils/demo/c24-corrections.py newsletter nouvelle-origine-V2
python -B wp/tests/demo/c24-http.py nouveau-parcours-V2
python -B wp/outils/demo/c24-mutations.py nouvelles-gardes-V2
```

`c24.py rules` utilise seulement le conteneur local hors réseau ; les autres recettes de ce second bloc accèdent à la démonstration. Le parcours HTTP rend la vraie page C10 et vérifie la section entre ouverture/fermeture de son formulaire ; sa mutation témoin retire uniquement l'injection C24 de la requête d'essai. Les scripts historiques de récupération ne font pas partie du rejeu. Questions rangées : localité fermée par défaut, inscription par défaut exclue de la transmission, emplacement visuel à valider par Ced. Preuves courantes et limites : `production/C-24/{A-VOIR.md,TRANSMISSION.md,manifest-fusion2050-V2.json}`. PRET technique ne vaut ni clôture, ni validation visuelle, ni GO sur le réel.
