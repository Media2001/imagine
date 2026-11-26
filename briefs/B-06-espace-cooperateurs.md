# Lot B-06 — L'espace coopérateurs

**Voie** : 2. **Chantier** : B. **Délai** : une demi-journée. **Dépend de** : B-01, B-02, C-10. **Cahier des charges** : §3.9 (« Coopérateur : attribut du compte »), §3.12 (« Espace coopérateurs »), §4.2 (compte : « statut de coopérateur et source de ce statut »). Relis-les.

## Pourquoi

Le coopérateur est un public à part : son statut **n'ouvre pas les articles** (réunion du 10 septembre), il ouvre un espace réservé. La pose automatique du statut depuis CoopHub dépend d'une documentation qui n'est pas arrivée ; le cahier des charges prévoit alors la pose **par l'administration**. Cette voie-là ne dépend de personne : l'attribut, sa source et l'espace peuvent exister et être montrés à Ced. Le profil P-COOP de la recette attend ce lot.

## Ce qu'on veut

**Le standard d'abord.** Dis en dix lignes ce que WordPress et Memberships offrent pour réserver des pages à un attribut de compte qui n'est pas un abonnement, et choisis le plus simple. L'attribut ne doit jamais se confondre avec un droit de lecture des articles.

- **L'attribut** : « coopérateur » oui ou non sur le compte, avec sa **source** (aujourd'hui une seule valeur possible : l'administration) et sa date. Il se pose et se retire depuis la fiche du compte, par un rôle de l'administration, avec un jeton de sécurité ; chaque changement est daté au journal de l'administration, comme C-17.
- **L'espace** : une page « Espace coopérateurs » et quatre sous-pages vides de contenu, aux intitulés du cahier des charges (appels à bénévolat, lettre de missions, cadastre des compétences, relais des événements). Un coopérateur connecté les lit ; tout autre visiteur, abonné compris, reçoit une page qui dit que l'espace est réservé aux coopérateurs, sans rien de son contenu.
- **Dans « Mon compte »** : une ligne qui dit le statut, et le lien vers l'espace quand il est ouvert.
- **Étanchéité** : le contenu de l'espace est absent, pour un non-coopérateur, de la page, de l'interface REST, des flux, de la recherche interne et du plan de site.
- **Un point d'accroche nommé** pour la future synchronisation avec CoopHub, sans écouteur ; aucun appel extérieur.

Règles :

- **l'attribut n'entre pas dans la décision d'accès aux articles** : un coopérateur non abonné reçoit l'extrait, comme aujourd'hui (C-06, clos, ne change pas) ;
- l'attribut et sa source entrent dans l'export et l'effacement des données du compte (C-21) ;
- pas de compteurs de campagne, pas de formulaire de prise de parts, pas de lien vers CoopHub : le niveau d'intégration n'est pas arrêté ;
- qui, dans l'équipe, peut poser l'attribut et qui peut lire l'espace sans être coopérateur n'est pas décrit : défaut prudent, le plus fermé (un seul rôle de l'administration pose l'attribut ; seuls les coopérateurs et ce rôle lisent l'espace). Écris les questions fermées pour Imagine dans ton rapport ;
- aucun style inventé : le squelette de B-01.

## Preuve

Proportionnée. Le profil coopérateur du jeu de profils reçoit l'attribut par l'écran ; il lit l'espace et reçoit toujours l'extrait d'un article réservé ; un abonné actif non coopérateur ne lit pas l'espace ; le texte témoin d'une sous-page est absent des cinq voies pour un anonyme ; l'attribut retiré referme l'espace. Profils remis dans leur état de départ, sauf le profil coopérateur, qui garde son attribut : dis-le.

## Livrables

Le code, ses tests, `production/B-06/A-VOIR.md`, `PRET`. Rapport court.
