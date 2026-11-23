# B-00 — à ouvrir

Site **entièrement fictif**, pas une maquette finale. Statut vérifié : `running`. Thème provisoire Twenty Twenty-Five ; B-01 n’existe pas encore.

| Adresse | Ce qu’on doit y voir |
|---|---|
| http://192.168.129.32:8085/ | L’avertissement « DÉMONSTRATION ENTIÈREMENT FICTIVE », cinq numéros, trois thématiques, deux événements et deux partenaires inventés. |
| http://192.168.129.32:8085/numeros/demo-2026-t1/ | Le numéro fictif 1, sa couverture générée, les dates de fixture, trois articles réservés, un ouvert et un lien vers son PDF factice. |
| http://192.168.129.32:8085/demo-2026-t1-reserve-1/ | Le titre et un extrait, puis le formulaire de protection native provisoire ; aucun corps complet n’est envoyé anonymement. |
| http://192.168.129.32:8085/demo-2026-t1-ouvert/ | Un article fictif français complet, nettement plus long que son extrait. |
| http://192.168.129.32:8085/wp-admin/ | La connexion WordPress, puis le tableau de bord du compte fictif ; les identifiants sont dans le fichier hors dépôt ci-dessous. |
| http://192.168.129.32:8085/calendrier-fictif/ | Quinze parutions sur 2026–2028 : quatre trimestriels et un hors-série d’été par an, avec sortie et clôture de liste. |

Identifiants de test : `C:\Users\Ced\.imagine-demo\identifiants.json` (`admin_user`, `admin_password`, `editor_user`, `editor_password`, `article_password`). **Ne pas recopier ce fichier dans le dépôt.** Le mot de passe d’article sert uniquement à voir le corps complet fictif en attendant C-08 ; ce n’est pas un accès abonné.

Preuves : `production/B-00/b00-construction.json` et `b00-reconstruction.json` ; `b00-verification-http-idempotence.json` ; réponses anonymes HTTP sous `production/B-00/http/`. L’administration renvoie normalement HTTP 302 vers la connexion ; son formulaire et sa session fictive ont aussi été vérifiés en HTTP 200, sans enregistrer de cookie ni de nonce.
