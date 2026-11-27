# Lot C-31 — Les adresses email jetables refusées à l'inscription

**Voie** : 2. **Chantier** : C. **Délai** : deux heures. **Dépend de** : C-10 (écran de réglages), C-12 (accès découverte), B-02 (Mon compte). **Cahier des charges** : §3.9 (« Accès découverte : un compte vérifié […] une seule fois par personne. […] Les adresses email jetables sont refusées à l'inscription »). Relis-le.

## Pourquoi

L'accès découverte s'ouvre une fois par personne. Une adresse jetable permet de le rouvrir autant de fois qu'on veut : le cahier des charges demande donc de les refuser à l'inscription. C'est une petite règle, et elle manque.

## Ce qu'on veut

**Le standard d'abord.** Trois lignes : par où passe la création d'un compte dans WordPress et dans WooCommerce (les points d'entrée natifs), et où un refus se pose une seule fois pour tous.

- **Une liste de domaines refusés, en réglage**, journalisé comme les autres : un domaine par ligne. Sur la démonstration, trois domaines manifestement fictifs. **Liste vide, rien n'est refusé.**
- À la création d'un compte, par tous les points d'entrée que la démonstration ouvre (formulaire d'inscription, création pendant une commande) : une adresse dont le domaine est dans la liste est refusée, avec un message clair qui ne dit pas « jetable » comme un reproche et propose d'utiliser une autre adresse.
- Comparaison sur le domaine exact, sans tenir compte de la casse ; dis ce que tu fais d'un sous-domaine, et prends le choix le plus simple.
- Le refus vaut pour l'inscription seulement : un compte existant n'est ni fermé ni modifié, et un changement d'adresse dans « Mon compte » suit la même règle.
- Les comptes créés par l'administration et la commande pour un client de C-16 ne sont pas concernés.

Règles :

- **aucune liste téléchargée, aucun service tiers, aucun appel sortant** : la liste est tenue par Imagine. D'où elle viendra est une question rangée pour Imagine ;
- l'adresse refusée n'est rangée nulle part, ni en base ni dans un journal ;
- aucun style inventé, aucun email envoyé.

## Preuve

Proportionnée. Une inscription avec un domaine de la liste est refusée par chaque point d'entrée, et aucun compte n'existe après ; avec un autre domaine, elle passe ; casse différente, refusée ; liste vide, tout passe ; un compte existant sur un domaine ajouté ensuite reste intact ; rien de l'adresse refusée en base ni dans le journal ; une mutation témoin sur le contrôle « aucun compte créé ». Comptes d'essai supprimés, réglage rendu dans son état de départ.

## Livrables

Le code, ses tests, la section du README, `production/C-31/A-VOIR.md`, `PRET`. Rapport court.
