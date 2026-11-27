# Attendu indépendant C09 — scénario C29 contrôlé

Oracle écrit avant le branchement : `wp/tests/demo/c29-attendus.php`. Ce tableau ne provient pas de la fonction C29 ni des décisions d’accès C06. Les préférences de scénario sont temporaires, puis restaurées ; ce n’est pas une nouvelle inscription permanente des profils.

Tous les comptes éligibles choisissent la lettre fictive `principale` avec origine `lecteur`. A-CARTE porte une réponse fictive et le consentement distinct, les autres aucune réponse. `—` = fiche absente ou champ qui n’existe pas dans la fiche réduite, jamais « inconnu » fabriqué à la place d’une absence.

| Profil C09 | Statut de fiche attendu | Tarif attendu | Coopérateur | Raison / choix du scénario |
|---|---|---|---|---|
| V-DEC | non_abonne | inconnu | non | Choix lecteur |
| V-DEC-FIN | a_retirer | — | — | Désinscription de tout ; fiche strictement réduite au statut |
| V-INSCRIT | absente | — | — | Aucun choix |
| A-CARTE | abonne | normal-1 | non | Choix lecteur ; personnalisation fictive présente avec accord distinct |
| A-SEPA4 | abonne | normal-4 | non | Choix lecteur |
| A-PAYPAL | abonne | normal-1 | non | Choix lecteur |
| A-VIR | non_abonne | inconnu | non | pending, pas actif |
| A-PAPIER | abonne | normal-4 | non | Choix lecteur |
| A-GRACE | non_abonne | inconnu | non | on-hold, malgré l’accès numérique de grâce |
| A-SUSP | non_abonne | inconnu | non | on-hold |
| A-EXPIRE | non_abonne | inconnu | non | expired |
| A-NONRENOUV | non_abonne | inconnu | non | pending-cancel, malgré l’accès jusqu’au terme |
| A-ETRANGER | abonne | inconnu | non | Produit actif sans correspondance tarifaire |
| A-SANSMAIL | absente | — | — | Sans email recevable même avec choix préparé |
| A-ECHEANCE | abonne | inconnu | non | Produit actif sans correspondance tarifaire |
| P-OFFRANT | non_abonne | inconnu | non | Aucune souscription native |
| P-OFFERT | non_abonne | inconnu | non | Aucun lien de bénéficiaire natif installé dans C09 |
| P-GEST | non_abonne | inconnu | non | Aucune souscription native |
| P-BENEF | non_abonne | inconnu | non | Aucun lien de bénéficiaire natif installé dans C09 |
| P-PRO | non_abonne | inconnu | non | Pas de statut déduit d’une société |
| P-SOL-ATT | non_abonne | inconnu | non | Adhésion manuelle ≠ souscription active |
| P-SOL-OK | non_abonne | inconnu | non | Justificatif/adhésion ≠ tarif ni souscription active |
| P-NUMERO | non_abonne | inconnu | non | Achat d’un numéro ≠ souscription active |
| P-COOP | non_abonne | inconnu | oui | Attribut B06, pas un droit d’abonné |
| E-ADMIN | absente | — | — | Aucun choix ; le rôle ne crée aucune fiche |
| E-REDAC | absente | — | — | Aucun choix ; le rôle ne crée aucune fiche |
| E-ABO | absente | — | — | Aucun choix ; le rôle ne crée aucune fiche |

Variantes natives distinctes, sans modifier cet oracle :

- A-CARTE : attribut fictif présent, retrait du seul accord distinct → tableau `personnalisation=[]` ; mutant lisant les réponses brutes → contrôle d’absence refusé.
- P-OFFERT : ajout transactionnel d’un lien Gifting natif vers ce compte → statut et tarif `inconnu`, puis retrait/restauration.
- P-BENEF : attribution Memberships native liée à une souscription et un plan groupe → statut et tarif `inconnu`, jamais statut déduit du payeur ; restauration.
- Compte inexistant : pas de fiche, raison `compte_absent`.
- La matrice pure ajoute les autres états, inscription automatique seule, liste supprimée, fermeture tarifaire et conflit de tarifs. Les trois visiteurs sans compte de C09 ne sont pas inventés comme comptes.
