# Lot B-13 — Le menu principal et le menu étendu des thématiques

**Voie** : 2. **Chantier** : B. **Délai** : une demi-journée. **Dépend de** : B-01 (squelette du thème), B-04 (thématiques), B-08 et B-09 (entrées déjà posées dans les menus). **Cahier des charges** : §3.1 (« Menu principal », « Un menu étendu présente les thématiques avec, pour chacune, une sélection d'articles illustrés »). Relis-le.

## Pourquoi

Le menu est sur toutes les pages. Le cahier des charges en fixe les huit entrées et leur ordre, et demande un menu étendu qui montre les thématiques avec quelques articles. Sa forme (panneau latéral ou grand menu déroulant) sera choisie sur maquette : on livre le contenu et la structure, pas la forme.

## Ce qu'on veut

**Le standard d'abord.** Cinq lignes : ce que les menus natifs de WordPress font seuls, et ce qu'il faut ajouter pour une liste d'articles par thématique.

- **Le menu principal**, dans cet ordre : Nos numéros · Thématiques · Nos newsletters · Nos événements · Notre coopérative · Soutenir · S'abonner · Connexion. Pas d'« Espace digital ». Tu pars du menu existant sans le recréer ni doubler une entrée ; une entrée dont la page n'existe pas encore (« S'abonner ») pointe vers une page d'attente déclarée telle. Ce que devient « Connexion » pour un lecteur connecté : garde ce que B-01 fait, et écris-le.
- **Le menu étendu**, sous « Thématiques » : la liste des thématiques et, pour chacune, une sélection d'articles : titre, image à la une, lien. Par défaut, les plus récents ; leur nombre est un réglage (trois sur la démonstration). Choisir à la main est une question rangée pour Imagine : ne la construis pas.
- **Structure seule** : des listes imbriquées, utilisables au clavier, lisibles sans JavaScript. Aucun style inventé, aucune animation.
- **Rien de réservé** : seuls le titre, l'image et le lien sortent, comme dans les listes de B-04. Ni extrait, ni texte.
- Le menu est construit une fois et gardé en cache ; dis ce qui le renouvelle (publication, dépublication, changement de thématique).

Une thématique sans article reste dans la liste, sans sélection.

## Preuve

Proportionnée. Les huit entrées dans l'ordre, une seule fois chacune, sur l'accueil, un article réservé et une page numéro ; le menu étendu avec les thématiques de la démonstration ; un article dépublié en sort après renouvellement. Étanchéité : les témoins de C-26 sont absents du menu pour un anonyme sur ces trois pages, sans étendre la matrice (un contrôle qui trouve d'abord le titre attendu, puis l'absence des témoins). Menus rendus dans leur état de départ si un essai les modifie.

## Livrables

Le code, ses tests, la section du README, `production/B-13/A-VOIR.md` avec une capture, `PRET`. Rapport court.
