# Lot A-15 — L'inventaire des emails que le site envoie

**Voie** : 1. **Chantier** : A. **Délai** : trois heures. **Cahier des charges** : §3.8 (« Tous les emails partent du site, par Brevo, au nom d'Imagine, en français »).

## Pourquoi

Le cahier des charges refond les emails du cycle de vie. Avant de les réécrire, il faut savoir ce que le site actuel envoie déjà : quels emails de WooCommerce, de Subscriptions et de Memberships sont actifs, lesquels ont été personnalisés, par quoi ils partent. Aujourd'hui personne n'en a la liste. Ce lot fournit l'outil, prêt pour le staging d'Imagine vérifié.

**Ce lot ne décide d'aucun email à garder, à couper ou à réécrire, et n'en envoie aucun.**

## Ce qu'on veut

Un complément du script d'audit (A-02), en **lecture seule**, qui produit la liste des emails déclarés par le site :

- une ligne par email : identifiant, intitulé, extension qui le déclare, actif ou non, destinataire **par nature** (le client, ou l'administration), objet et contenu personnalisés ou non (oui ou non, pas le texte), gabarit surchargé par le thème ou non (nom du fichier) ;
- ce qui sert à l'envoi : extensions d'envoi présentes et actives (noms et versions), sans aucun réglage ;
- un résumé lisible : nombre d'emails actifs par extension, nombre de gabarits surchargés.

**Aucune adresse, aucun identifiant de connexion, aucune clé, aucun texte d'objet ou de contenu** ne sort de l'outil. Un destinataire interne personnalisé est signalé « personnalisé », sans son adresse.

Les emails sont lus dans les registres natifs, réellement chargés, comme A-12 l'a fait pour les types de contenu : réemploie son lanceur confiné et le chemin en lecture seule d'A-11. Aucun écrit en base, aucune tâche planifiée, aucun envoi : la garde contre les envois est éprouvée, pas supposée.

Si un email est envoyé par un service extérieur au site (les avis de la passerelle de paiement, par exemple), l'outil ne peut pas le voir : dis-le dans le mode d'emploi, en une phrase, plutôt que de laisser croire que la liste est complète.

## Preuve

Sur le banc fictif, classique et HPOS : un email désactivé, un gabarit surchargé, un destinataire interne personnalisé avec une adresse canari. Les comptes sont exacts, l'adresse canari est absente de toutes les sorties, aucun email n'est parti, l'empreinte de la base est identique avant et après. **Un seul paquet de preuves.**

## Livrables

Le script, ses tests, deux lignes dans le mode d'emploi de l'audit, `production/A-15/PRET`. Rapport court.
