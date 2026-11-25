# Contrôler un export CSV hors ligne — A-13

**Python 3.10 ou supérieur, bibliothèque standard uniquement.** Aucun site, compte,
import, connexion réseau ni dépendance à installer. Seul Ced contrôle un export réel,
sur le NUC et hors du dépôt ; les agents n'ouvrent que les fixtures fictives.

## Lancer le contrôle

Copier `wp/outils/bascule/a13/correspondance.exemple.json` dans le dossier de travail
**hors du dépôt**, adapter les noms de colonnes à l'en-tête exact du CSV, puis lancer
à la racine du dépôt (chemins d'exemple à remplacer, aucun vrai fichier fourni) :

```text
python wp/outils/bascule/controler-export "D:/controle-imagine/export.csv" --correspondance "D:/controle-imagine/correspondance.json"
```

L'outil ne modifie pas le CSV. Il crée à côté de celui-ci `export.controle-resume.txt`
et `export.controle-rejets.csv` (UTF-8, séparateur `;`, colonnes `ligne;motif`). Une
ligne de rejet contient **uniquement** le numéro de ligne physique d'origine
(en-tête = 1, champ multiligne = ligne de début) et un motif français, jamais les
valeurs du contact. Pour corriger, l'administration consulte cette ligne dans son
export, puis relance sur une nouvelle copie. Les sorties existantes ne sont jamais
écrasées : les déplacer ou les supprimer explicitement avant un rejeu. Les sorties
dans ce dépôt, y compris par un chemin symbolique résolu vers lui, sont refusées.

Codes : **0** = aucun rejet ; **1** = contrôlé, rejets à corriger ; **2** = refus,
format/configuration/lecture/écriture à corriger. Un IBAN suspect bloque tout le
fichier : seules sa position de colonne et une consigne sont affichées, **aucune
valeur, aucun résumé, aucun fichier de rejets**. La totalité du fichier, y compris
les colonnes non utilisées et la dernière ligne, est précontrôlée avant toute
analyse métier et toute écriture. La détection vise une ressemblance, sans checksum
bancaire ni vérification en ligne : un faux IBAN peut donc bloquer volontairement.
Si le CSV est cassé, la colonne peut ne pas être déterminable : réparer le format
hors du dépôt, jamais ignorer l'alerte ou importer le fichier.

## Adapter la correspondance

Conserver toutes les clés de l'exemple et la version `1`. `colonnes` associe les
champs logiques aux en-têtes **exacts**, sans renommer automatiquement une colonne.
Un champ facultatif absent (`email`, `prenom`, `reference_mandat`, ou un champ non
obligatoire de contact/type/statut) peut être associé à `null`. Les champs utilisés
pour la date, les numéros dus, le paiement et l'adresse postale doivent être mappés.
`obligatoires` choisit les champs à renseigner ; l'email ne peut jamais en faire
partie. Sans email, la ligne n'est pas rejetée pour ce motif et est comptée à part ;
aucune adresse n'est inventée (création future selon CDC §3.13, hors de cet outil).

- `encodage` : `auto` accepte un BOM UTF-8/UTF-16 ou du UTF-8 strictement valide,
  et l'annonce dans le résumé ; aucun repli silencieux sur un encodage ancien.
  Sinon déclarer `cp1252`, `iso-8859-1`, `utf-8`, `utf-8-sig` ou `utf-16` (avec BOM).
  Un BOM contradictoire ou un contenu illisible est refusé.
- `separateur` : `auto` exige un seul candidat structurel cohérent parmi `;`, `,`,
  `\t`, `|`, sur **tout** le CSV. Deux candidats ou aucun = refus explicite.
  Déclarer au besoin le caractère (`"\t"` en JSON pour la tabulation).
- `format_date` : `%Y-%m-%d` par défaut ; `%d/%m/%Y` et `%d-%m-%Y` sont admis.
  Aucun format n'est deviné. Date passée = avant la date locale du contrôle ; une
  date du jour est admise. `--au 2026-11-25` fixe cette date pour reproduire une preuve.
- `modes_paiement` : liste déclarée ; `modes_mandat_papier` : sous-liste demandant
  une référence de mandat. Aucune liste Access n'est présumée dans le code.
- `types_abonnement_autorises` : `[]` par défaut, filtre **désactivé**. Le remplir
  est une option de contrôle uniquement ; aucune correspondance vers un produit,
  règle de coopérateur, décision d'import des échus ou écriture comptable.

Adresse complète = rue, code postal, ville, pays renseignés ; pas de géocodage.
Email = contrôle syntaxique ASCII usuel (domaines internationalisés en punycode),
aucun test de délivrabilité. Les doublons portent sur l'email, sur le nom complet
(nom et prénom si fourni) + adresse complète, ou sur la référence de mandat.
Casse, accents et espaces sont normalisés pour les comparaisons uniquement.
**Tous** les membres d'un doublon sont signalés, pas seulement le deuxième.
Le résumé distingue lignes rejetées et motifs : une ligne peut porter plusieurs
motifs ; « lignes en doublon » compte les lignes uniques concernées.

## Rejouer les preuves fictives

```text
python -m unittest discover -s wp/tests/a13 -v
python wp/tests/a13/verifier_livraison.py --preuve production/A-13/verification.json
```

Les trois fixtures `a13-export-*-fictif.csv` ont chacune trente lignes. La suite et
le vérificateur les copient dans un dossier temporaire hors du dépôt, y exécutent
réellement la CLI, puis nettoient ce dossier. Ne pas lancer le contrôleur directement
sur une fixture du dépôt : il doit refuser ses sorties. Le lot ajoute une suite ;
le parent doit aussi rejouer `wp/tests/preparer-image.ps1` avant de déposer `PRET`.
