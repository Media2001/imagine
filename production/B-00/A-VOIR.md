# B-00 — à ouvrir

Site **entièrement fictif**, pas une maquette finale. État intégré B00+B01+C08+C09+C10, registre `running`, thème **`imagine`** actif et langue **`fr_FR`**. Les dates et tarifs restent des fixtures, pas des choix métier validés.

| Adresse | Ce qu’on doit y voir |
|---|---|
| http://192.168.129.32:8085/ | L’accueil B01 « Imagine — démonstration fictive », l’avertissement « Aucune donnée réelle, aucun paiement ni email sortant », le dernier numéro, les cinq derniers articles et les trois thématiques. Le kiosque liste les cinq numéros ; agenda et partenaires sont accessibles par la navigation. |
| http://192.168.129.32:8085/numeros/demo-2026-t1/ | Le numéro fictif 1, couverture et date de sortie, PDF factice et sommaire de **six articles** : les quatre B00 (trois réservés et un ouvert) plus les deux fixtures réservées C08, IDs 81 et 82. |
| http://192.168.129.32:8085/demo-2026-t1-reserve-1/ | Le titre, l’extrait public et le bloc C08 de connexion ; aucun formulaire de mot de passe d’article. Après connexion avec le compte fictif C08 `actif`, le corps complet devient lisible. |
| http://192.168.129.32:8085/demo-2026-t1-ouvert/ | Un article fictif français complet, nettement plus long que son extrait. |
| http://192.168.129.32:8085/wp-admin/ | La connexion WordPress, puis le tableau de bord du compte fictif ; les identifiants sont dans le fichier hors dépôt ci-dessous. |
| http://192.168.129.32:8085/calendrier-fictif/ | Quinze parutions sur 2026–2028 : quatre trimestriels et un hors-série d’été par an, avec sortie et clôture de liste. |

Identifiants B00 et **27 comptes C09 conservés** : `C:\Users\Ced\.imagine-demo\identifiants.json` (`c09_accounts` pour les profils). Comptes de lecture C08 : `C:\Users\Ced\.imagine-demo\c08-identifiants.json`, entrée `accounts.actif`. Se connecter d’abord à `/wp-login.php`, puis revenir à l’article. **Ne recopier aucun de ces fichiers dans le dépôt.** L’ancienne clé `article_password` subsiste uniquement pour les tests du cookie historique : elle n’accorde aucun droit. Les mots de passe d’article sont retirés de la base dès que C08 est actif ; l’étanchéité appartient entièrement à C08.

C10 : http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-reglages, avec le profil fictif `E-ADMIN` de `c09_accounts` : huit champs « À confirmer par Imagine » et journal. B00 n’enregistre aucun réglage et préserve ses options, journal et bootstrap.

Preuves actuelles : `b00-reconstruction.json` (vrai CLI après le seed C08), `b00-final-verification.json`, `b00-verification-http-idempotence.json`, `tests/b00-integre-actuel.txt` et les réponses anonymes `http/`. Cinq URL publiques HTTP 200 ; `/wp-admin/` HTTP 302 vers la connexion, puis session administrateur fictif HTTP 200 sans sauvegarder son HTML. Les anciens résultats « 81/81 », captures TT25 et démonstrations par mot de passe sont **historiques**, conservés dans `historique/avant-corrections-23nov-16h30/`, et ne décrivent plus le site courant. Voir `verification.md` pour les limites de l’horloge des tests C09.
