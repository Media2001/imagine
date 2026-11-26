# C-22 — inventaire ajouté aux outils natifs C21

| Donnée | Stockage | Export WordPress | Effacement WordPress |
|---|---|---|---|
| Choix de chaque newsletter, y compris retirée du catalogue | Méta utilisateur `imagine_newsletters_preferences`, indexée par identifiant stable : `choix` booléen, `date_utc`, `origine` (`lecteur` ou `defaut_creation`) | Exporteur C21 `imagine-site`, groupe existant `imagine-meta` ; la valeur contient identifiants, états, dates et origines | Effaceur C21 `imagine-site` supprime la méta et relit son absence ; suppression native du compte passe aussi par C21 |
| Catalogue public des lettres | Option `imagine_newsletters_catalogue` : identifiant, titre, présentation, principale | Pas une donnée personnelle du lecteur | Non supprimé avec le lecteur |
| Politique de création du compte | Option `imagine_newsletters_creation`, `non` par défaut ou `oui` | Pas une donnée personnelle du lecteur | Non modifiée à l'effacement |
| Modification administrative du catalogue/réglage | Journal C10 déjà existant : opérateur, instant UTC, option, avant/après | Le journal entre déjà dans l'inventaire C21 lorsqu'il concerne l'opérateur | C21 neutralise déjà identité/login de l'opérateur effacé ; catalogue/réglage restent des données générales, aucune liste de lecteurs dans ce journal |

Aucune adresse copiée dans les préférences, aucun jeton Brevo, statut de confirmation, attribut persona ni historique parallèle. Les dates sont celles du choix observé, pas des dates de consentement présumées. L'origine de création automatique est déclarée comme telle et ne vaut pas consentement explicite. Une sauvegarde identique conserve sa date, sauf confirmation volontaire d'un état qui venait uniquement du réglage de création.

La seule modification de C21 est l'ajout de cette méta à son inventaire `META`. Ses hooks natifs, sa pagination, ses contrôles d'échec et son effacement à suppression du compte sont réemployés sans outil parallèle. Aucun réglage de conservation Woo/WordPress modifié. La recette C22 vérifie les callbacks natifs réellement enregistrés, puis rollbacke la transaction et relit les empreintes depuis un autre processus.

Références standard consultées (HTTP 200, reçu `sources-officielles.json`) : WordPress **Settings API**, hooks **wp_privacy_personal_data_exporters**, **wp_privacy_personal_data_erasers**. Woo fournit le dashboard et la connexion existants ; il ne fournit pas ce catalogue métier local et ses choix datés. Le sur-mesure se limite aux règles pures, au formulaire de préférences et aux raccords Settings API/confidentialité.
