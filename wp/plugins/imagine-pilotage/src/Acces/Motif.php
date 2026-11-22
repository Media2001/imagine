<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Acces;

enum Motif: string
{
    case EntreeInvalide = 'entree_invalide';
    case ContenuOuvert = 'contenu_ouvert';
    case ContenuFuturFermeParReglage = 'contenu_futur_ferme_par_reglage';
    case ContenuFuturEquipeParReglage = 'contenu_futur_equipe_par_reglage';
    case RobotVerifie = 'robot_verifie';
    case PdfRobotExtraitParReglage = 'pdf_robot_extrait_par_reglage';
    case Anonyme = 'anonyme';
    case SansDroit = 'sans_droit';
    case AbonnementActif = 'abonnement_actif';
    case OffertActif = 'offert_actif';
    case GroupeActif = 'groupe_actif';
    case DelaiGrace = 'delai_grace';
    case Suspendu = 'suspendu';
    case Expire = 'expire';
    case VirementNonValide = 'virement_non_valide';
    case AbonnementPasCommence = 'abonnement_pas_commence';
    case PdfAnterieurFermeParReglage = 'pdf_anterieur_ferme_par_reglage';
    case Equipe = 'equipe';
    case NumeroAchete = 'numero_achete';
    case AchatPasCommence = 'achat_pas_commence';
    case AutreNumero = 'autre_numero';
    case CooperateurSansAbonnement = 'cooperateur_sans_abonnement';
    case DecouverteDuree = 'decouverte_duree';
    case DecouverteArticles = 'decouverte_articles';
    case DecouverteEpuisee = 'decouverte_epuisee';
    case DecouvertePasCommencee = 'decouverte_pas_commencee';
    case DecouverteHorsPerimetre = 'decouverte_hors_perimetre';
    case CompteNonVerifie = 'compte_non_verifie';
}
