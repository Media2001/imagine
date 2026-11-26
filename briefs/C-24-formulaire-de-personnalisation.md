# Lot C-24 — Le formulaire de personnalisation

**Voie** : 2. **Chantier** : C. **Délai** : une demi-journée. **Dépend de** : B-02, C-10, C-21, C-22. **Cahier des charges** : §3.7 (« Formulaire de personnalisation »), §3.10 (« Étiquettes de persona »), §4.2 (compte : « étiquettes de persona et consentement »), §4.4 (« consentement distinct pour les étiquettes de personnalisation »). Relis-les.

## Pourquoi

Le tunnel ne pose aucune question de profil : la personnalisation vient après, par un court formulaire facultatif dont les réponses deviennent des étiquettes sur le compte. Ces étiquettes serviront à Brevo, aux extractions et au tableau de bord. Les questions elles-mêmes ne sont pas arrêtées (elles le seront pendant l'étude, à partir des personas d'Imagine) : elles sont donc une donnée, comme la liste des newsletters de C-22. Le formulaire, lui, peut exister et être montré à Ced.

## Ce qu'on veut

- **Les questions sont une donnée, pas du code** : un réglage dans l'écran de C-10 (identifiant de la question, intitulé, liste de choix avec leur identifiant, un ou plusieurs choix possibles). Sur la démonstration : quatre questions **manifestement fictives**, une par famille citée au §3.7 (profession ou situation, centres d'intérêt, tranche d'âge, localité). Ajouter une question dans le réglage la fait apparaître, sans toucher au code.
- **Dans « Mon compte »**, une rubrique « Personnalisez ce que vous recevez » : le lecteur répond, modifie, efface ses réponses. Chaque réponse est une étiquette sur le compte, datée. Rien n'est obligatoire ; ne pas répondre ne bloque rien, nulle part.
- **Un consentement distinct** : une case séparée, non cochée, « J'accepte que ces réponses servent à personnaliser les envois que je reçois ». Elle est enregistrée et datée à part des étiquettes, et à part du choix des newsletters. Sans elle, les étiquettes restent sur le site.
- **Un point d'accroche nommé** pour le connecteur vers Brevo, qui ne transmettra les étiquettes que si le consentement est donné **et** si le lecteur est inscrit à au moins une newsletter (§3.10). Aucun écouteur, aucun appel.

Règles :

- **Rien ne part.** Aucun appel à Brevo, aucun email : le rappel du formulaire par email (§3.7) viendra avec les emails.
- La proposition du formulaire « après l'inscription ou l'achat » attend le tunnel : un emplacement nommé, rien de plus.
- **Choix fermés seulement, pas de champ libre** : défaut prudent, on ne recueille pas plus qu'une étiquette. Si une question d'Imagine demande un texte libre (la localité ?), c'est une question fermée à écrire dans ton rapport.
- Un identifiant de question ou de choix déjà employé, même retiré, est réservé et refusé : la leçon de C-22 vaut ici. Une question retirée du réglage n'apparaît plus ; ses anciennes réponses ne sont pas réattribuées.
- Les étiquettes et le consentement entrent dans l'export et l'effacement des données du compte (C-21), contrôlés sur le résultat.
- Un compte « sans email » : dis ce que tu fais et pourquoi (défaut : la rubrique existe, la case de consentement n'apparaît pas, puisque ce compte est exclu de tous les envois).
- Les extractions par étiquette (C-18) et la répartition des étiquettes au tableau de bord (C-19) ne sont pas dans ce lot.
- Aucun style inventé : le squelette de B-01.

## Preuve

Proportionnée. Un profil répond, modifie, efface, recharge : l'état est le bon et il est daté ; le consentement se donne et se retire sans toucher aux étiquettes ; un lecteur ne modifie pas les réponses d'un autre ; une cinquième question ajoutée dans le réglage apparaît puis est retirée, son identifiant ne se réutilise pas ; aucun appel sortant ni email pendant le parcours ; l'export contient les étiquettes et le consentement, l'effacement les retire. Profils remis dans leur état de départ.

## Livrables

Le code, ses tests, `production/C-24/A-VOIR.md`, `PRET`. Rapport court.
