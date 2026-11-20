# Lot A-01 — reprise : un staging fidèle, pas un site stérilisé

**Date** : 20/11/2026. **Remplace** les exigences de `prompts/2026-11-19-staging-imagine.md` là où elles se contredisent.
**Délai** : une demi-journée de travail. Au-delà, écris où tu en es, dépose ce qui fonctionne et passe au lot suivant.

## Ce qui ne va pas dans la version actuelle

Le travail est rigoureux et le rapport est honnête : c'est noté. Mais l'approche par listes fermées donne un résultat inutilisable pour le projet :

- seules trois extensions restent actives, seules 23 options sont conservées, toute table inconnue fait refuser l'import, tout le réseau est coupé ;
- sur le vrai site, soit l'import est refusé d'entrée, soit il produit un site vidé de sa configuration.

Or ce staging sert à **vérifier que le site existant continue de fonctionner** quand on le met à jour (chantier A), puis à poser le nouveau thème et le code sur mesure dessus. Il doit ressembler à la production. L'exigence « aucune clé restante dans toute la base » du premier prompt était trop large : c'est corrigé ici.

## Le nouveau principe

**Garder le site tel quel. Ne retirer que ce qui est dangereux. Signaler ce qu'on ne connaît pas.**

### Ce qui reste comme aujourd'hui

- Aucune ouverture de la sauvegarde réelle par un agent ; tests sur sites jetables.
- Traitement avant le premier démarrage de WordPress, copie sans port web ni sortie réseau jusqu'à la vérification.
- Le mu-plugin de verrouillage (emails, tâches planifiées, lanceur d'Action Scheduler, mode staging de Subscriptions, indexation).
- L'anonymisation des comptes, adresses, commandes, abonnements, commentaires et notes.
- La suppression des jetons de paiement, des identifiants Stripe et PayPal, des sessions, des clés d'API WooCommerce.
- La suppression de l'archive `ai1wm-backups` et des sauvegardes, exports et dumps présents dans la copie.
- Le compte administrateur de test créé après la restauration, mot de passe par l'entrée standard.
- Les deux statuts distincts, « importé » et « vérifié ».

### Ce qui change

| Sujet | Avant | Maintenant |
|---|---|---|
| Extensions | Trois gardées actives | **Toutes gardées dans leur état**, sauf une liste nommée de celles qui envoient vers l'extérieur ou gênent un staging : envoi d'emails et SMTP, Brevo et autres outils d'emailing, sauvegarde, statistiques et pixels, cache de pages. La liste est un fichier de configuration lisible ; le rapport dit ce qui a été désactivé. |
| Options | 23 gardées, le reste supprimé | **Toutes gardées.** On vide uniquement les champs secrets connus (clés Stripe, PayPal, Brevo, SMTP, webhooks) en conservant le reste du réglage, et on bascule les passerelles en mode test sans clé. |
| Tables inconnues | Refus | **Gardées et listées** dans le rapport : nom, colonnes, nombre de lignes, jamais de valeur. Une table inconnue dont une colonne évoque une donnée personnelle (email, téléphone, nom, adresse, IP) bloque le statut « vérifié » **tant que Ced n'a pas tranché** dans un fichier de décisions (`garder`, `vider`, ou `anonymiser` telles colonnes). Les autres ne bloquent pas. |
| Types de contenu inconnus | Refus | Gardés, listés. |
| mu-plugins et drop-ins de la production | Tous supprimés | mu-plugins gardés et listés ; seuls les drop-ins de cache (`object-cache.php`, `advanced-cache.php`) sont retirés. |
| Réseau, une fois « vérifié » | Tout bloqué | Bloqué, **sauf** les hôtes nécessaires aux mises à jour : `*.wordpress.org` et `*.woocommerce.com` (`WP_ACCESSIBLE_HOSTS`, et le filtre du mu-plugin aligné). Rien d'autre sans consigne. |
| Passerelles de paiement | Masquées | Masquées pour l'instant. Le mode test de Stripe sera ouvert par un lot ultérieur, sur consigne. |
| Vues, déclencheurs, moteur de table | Refus | Signalés, non bloquants. |

### Ce qui bloque le statut « vérifié » — cinq points, pas plus

1. Une adresse email hors `@example.org` dans les comptes, les commandes ou les abonnements.
2. Une clé de service au motif connu (`sk_live`, `pk_live`, `rk_live`, `whsec_`, `xkeysib-` et équivalents), où qu'elle soit.
3. Un identifiant Stripe ou PayPal de client ou de moyen de paiement.
4. L'envoi d'email non coupé (preuve par exécution).
5. Subscriptions présent et pas en mode staging.

Plus : une table inconnue à colonne personnelle, non tranchée (voir tableau).

Tout le reste va dans le rapport comme **avertissement**, avec assez d'information pour que Ced décide, sans jamais afficher de valeur.

## Livrables

1. Les scripts corrigés, et la chaîne complète qui passe sur les deux sites jetables (classique et HPOS) : cas propre accepté, chaque piège refusé.
2. Sur un site jetable enrichi de deux ou trois extensions gratuites courantes (un formulaire, un outil de référencement, un constructeur de champs) : la preuve qu'après traitement **le site démarre, ses extensions sont actives et leurs réglages sont intacts**. C'est le test qui manquait.
3. La commande unique pour Ced, et ce qu'il verra : le rapport, la liste des tables à trancher, le statut.
4. `production/A-01/notes.md` mis à jour, puis `production/A-01/PRET`.

Subscriptions et Memberships : toujours sans licence sur les sites jetables. Écris leurs traitements d'après la documentation, liste ce qui n'est pas testé, et **dépose `PRET` quand même** : le premier import réel, lancé par Ced, servira de test, et son rapport de vérification sera relu avant toute ouverture.

## À ne pas faire

- Pas de nouvelle couche d'abstraction. Si une partie de l'intégration à l'outil de staging n'est pas nécessaire pour obtenir la commande unique, laisse-la de côté et dis-le.
- Ne modifie pas l'outil de staging partagé au-delà de ce profil, et pas sans le dire.
- Ne relance pas l'ancien staging d'Imagine.
