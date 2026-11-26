# C-18 — Extractions : prêt technique, validation visuelle attendue

## À ouvrir

Seul site : **imagine-test-demo**, avec le compte fictif **e-abo**. Identifiants déjà présents hors dépôt dans `C:\Users\Ced\.imagine-demo\identifiants.json` ; aucun mot de passe dans ce document.

- `http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-extractions`
- Localité France : `http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-extractions&extraction=localite&pays=FR`
- Virement : `http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-extractions&extraction=mode&mode_paiement=bacs`
- Papier : remplacer `bacs` par `imagine_papier`.
- Échéance : choisir « Abonnés par date d’échéance » ; dates du jour à +30 jours proposées, modifiables. Bornes UTC inclusives.
- État : choisir actif, grâce, suspendu ou expiré. Tranche d’âge et étiquette restent grisées « à venir ».

Le menu **Imagine → Extractions** affiche un nombre réel avant le bouton CSV. Les filtres sont conservés dans le formulaire ; aucune identité d’abonné n’est affichée dans l’aperçu ou le journal. Capture Chromium réelle : `extractions-referent.png`, contrôlée sans chevauchement visible ; ce n’est pas la validation visuelle de Ced.

## Résultat réel du 26 novembre 2026, 01 h 59 CET

Neuf téléchargements HTTP ont été enregistrés **localement dans ce dossier de preuve**, puis rouverts avec `csv.DictReader` :

| Sélection | Lignes | Preuve |
|---|---:|---|
| France | 2 | `extraction-1_localite.csv` : A-ETRANGER est le seul profil C09 ; l’autre ligne est le témoin C13 existant |
| Virement | 1 | `extraction-2_mode.csv` : A-VIR uniquement |
| Mandat papier | 1 | `extraction-3_mode.csv` : A-PAPIER uniquement |
| Échéance dans les 30 jours | 10 | `extraction-4_echeance.csv` : A-ECHEANCE inclus, A-EXPIRE exclu |
| Grâce | 4 | `extraction-5_etat.csv` : A-GRACE inclus, A-SUSP exclu |
| Suspendu | 1 | `extraction-6_etat.csv` : A-SUSP, pas A-GRACE |
| Expiré | 1 | `extraction-7_etat.csv` : A-EXPIRE, pas A-CARTE |
| Actif | 9 | `extraction-8_etat.csv` : A-CARTE inclus, A-SUSP exclu |
| Toutes localités | 16 | `extraction-9_localite.csv` : A-SANSMAIL avec email vide |

Ces nombres décrivent l’état fictif observé, pas une statistique d’Imagine. Le contrôleur ne crée **aucun fichier serveur**, public ou privé : flux `php://output`, privé/no-store, pièce jointe, `nosniff`. Une réouverture dans Excel/LibreOffice n’est pas prétendue ; les vrais octets CSV et leurs colonnes ont été relus et analysés depuis les fichiers téléchargés. Les formules, virgules et guillemets sont aussi éprouvés sur le banc pur.

## Standard et décisions prises à défaut

- Réemploi du parent Imagine, de la capacité C09 `imagine_extraire_abonnes`, des API Woo/WCS, de `SansEmail::META`, de l’état B02 et du mode C15. Aucune nouvelle base d’abonnés, aucun rôle global ajouté.
- Une ligne par abonnement natif, tous états, donc plusieurs lignes possibles pour un titulaire. Livraison = celle de la souscription ; identité/email = titulaire du compte. Pas de bénéficiaire offert/groupé inventé.
- Échéance = minimum des dates natives non vides prochain paiement/fin, sans calendrier recalculé. Le mode vide reste inconnu ; l’exception fictive C15 existante identifie seulement A-VIR/A-PAPIER.
- Aperçu et POST relisent les mêmes filtres ; l’état peut changer entre les deux, ce que l’écran explique. Le nonce WordPress n’est pas à usage unique : chaque téléchargement autorisé produit sa propre ligne de journal.
- CSV sécurisé : réemploi direct de `Imagine\Connecteur\CsvProtection`, la primitive C13/C04, et projection sur colonnes fermées. Le journal contient seulement opérateur, date UTC, code d’extraction et nombre, jamais les filtres ni les lignes. Une panne du journal ferme l’export. Le journal atteste la préparation, pas la réception réseau complète.
- Une extraction est définie dans un seul fichier `wp/plugins/imagine-site/extractions/*.php` : colonnes, filtres, requête, prédicat. Aucun changement du noyau n’est nécessaire pour ajouter une extraction de cette source.

Documentation officielle consultée : `https://developer.wordpress.org/apis/security/nonces/` (capacité indépendante du nonce) et `https://developer.woocommerce.com/docs/best-practices/data-management/crud-objects/` (lecture par objets CRUD ; pas de sauvegarde dans ce lot). Le sur-mesure se limite au catalogue, au filtrage pur et à cet écran d’extraction demandé par le CDC §3.13.

## Preuves et rejeu ciblé

À la racine du dépôt, sans reset ni autre lot :

```powershell
python wp/tests/demo/c18-verifier.py
```

Réinstallation du seul code C18, préparation publique de l’image et suite canonique, si nécessaire :

```powershell
python wp/tests/demo/c18-verifier.py --prepare --deploy --canonical
```

Le rejeu ajoute neuf événements d’extraction au journal, pas des abonnements. Les refus et les aperçus n’ajoutent rien. Il ne rejoue aucun seed C09 et ne replanifie aucune action.

- `final.json` : empreintes exactes relues sur le site, colonnes/fichiers CSV rouverts, conservation native et succession du bootstrap partagé C17 → C18.
- `unit-final.json` : **17 tests / 24 assertions** ; `unit-root-final.json` : **98 / 523**, zéro échec.
- `runtime-final.json` : **14 contrôles natifs**, filtre SQL refusant toute écriture pendant la lecture, panne réelle de persistance du journal injectée sans données fabriquées.
- `http-final.json` : **95 contrôles**, dont capacité indépendante du jeton, anonyme/rédacteur/client refusés, nonce absent/invalide/tableau, liaison aux filtres/extraction, GET refusé, nombre/CSV/journal, état natif préservé.
- `preparer-image-final.log` et `rejouer-t01-final.log` : préparation exécutée, puis **1 062 tests / 34 271 assertions**, zéro échec/erreur/ignoré. T01 et ses fichiers restent inchangés. PSR12 : zéro erreur (`-n`).

## Limites conservées, pas de faux vert global

C09 natif reste **381/382**, code **1**, seul échec `A-PAPIER:action_native_planifiee_ou_absente_selon_statut`. L’action historique **8103**, annulée le 25 novembre à 20:38:22 UTC avant C16, n’est pas replanifiée par C18 et son état est inchangé. C18 ne modifie ni profils, paiements, échéances, droits, fichiers privés C17, ni ressources d’un autre site. Pas de données réelles ni d’email. La capture navigateur a bloqué l’avatar Gravatar demandé par l’administration WordPress.

Les modes C09 non raccordés, les liens offert/groupé et les champs âge/étiquette absents ne sont pas fabriqués. Pas de qualification volumétrique en production ; pagination native de 100 et constitution en mémoire sur cette démo. Bootstrap partagé et README ont des empreintes successeurs documentées, pas des historiques C16/C17 réécrits. Validation visuelle de Ced et relectures restent attendues ; ce PRET n’est pas une clôture ni un GO sur le réel.
