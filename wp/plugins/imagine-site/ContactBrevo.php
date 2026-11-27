<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Lecture native à la demande ; ni cache persistant ni transport. */
final class ContactBrevo
{
    public const PAGE = 'imagine-contact-brevo';
    public const TARIFS = 'imagine_brevo_tarifs';

    public static function register(): void
    {
        add_action('admin_init', [self::class, 'reglages']);
        add_action(
            'admin_menu',
            static function (): void {
                add_options_page(
                    __('Tarifs de la fiche Brevo', 'imagine-site'),
                    __('Tarifs de la fiche Brevo', 'imagine-site'),
                    'manage_options',
                    'imagine-brevo-tarifs',
                    [self::class, 'pageReglages']
                );
                if (TableauBordAdmin::autorise()) {
                    add_submenu_page(
                        'imagine',
                        __('Ce qui partirait vers Brevo', 'imagine-site'),
                        __('Ce qui partirait vers Brevo', 'imagine-site'),
                        current_user_can('manage_options') ? 'manage_options' : TableauBordAdmin::CAP,
                        self::PAGE,
                        [self::class, 'page']
                    );
                }
            },
            121
        );
        add_action(
            'admin_init',
            static function (): void {
            if (($_GET['page'] ?? null) === self::PAGE) {
                self::verifier();
            }
            }
        );
        add_filter(
            'woocommerce_prevent_admin_access',
            static function (bool $prevent): bool {
            global $pagenow;
            return $pagenow === 'admin.php' && ($_GET['page'] ?? null) === self::PAGE
                && TableauBordAdmin::autorise() ? false : $prevent;
            }
        );
    }

    /** Réglage autonome : jamais soumis par l'écran de projection ni avec le groupe C10. */
    public static function reglages(): void
    {
        register_setting(
            'imagine_brevo_tarifs',
            self::TARIFS,
            [
                'type' => 'array',
                'default' => [],
                'show_in_rest' => false,
                'sanitize_callback' => [self::class, 'nettoyerTarifs'],
            ]
        );
    }

    public static function nettoyerTarifs(mixed $value): array
    {
        if (is_string($value)) {
            $value = json_decode($value, true);
        }
        return self::tarifs($value);
    }

    public static function pageReglages(): void
    {
        if (!current_user_can('manage_options')) {
            wp_die(esc_html__('Réglage réservé à l’administration.', 'imagine-site'), '', ['response' => 403]);
        }
        echo '<div class="wrap"><h1>' . esc_html__('Tarifs de la fiche Brevo', 'imagine-site') . '</h1><p>'
            . esc_html__('Réglage distinct de la consultation. Liste fermée JSON : identifiant natif de produit ou variation vers clé interne. Vide ou invalide : inconnu. Ne définit aucun prix ni droit. Aucun tarif réel n’est prérempli.', 'imagine-site') . '</p><form method="post" action="options.php">';
        settings_fields('imagine_brevo_tarifs');
        echo '<label for="imagine-brevo-tarifs">' . esc_html__('Correspondance fermée', 'imagine-site') . '</label><br><textarea id="imagine-brevo-tarifs" name="'
            . esc_attr(self::TARIFS) . '" rows="10" cols="70">' . esc_textarea(wp_json_encode((object)self::tarifs(get_option(self::TARIFS, [])), JSON_PRETTY_PRINT)) . '</textarea>';
        submit_button();
        echo '</form></div>';
    }

    private static function verifier(): void
    {
        if (!TableauBordAdmin::autorise()) {
            wp_die(esc_html__('Fiches réservées au Référent abonnements.', 'imagine-site'), '', ['response' => 403]);
        }
        if (!in_array($_SERVER['REQUEST_METHOD'] ?? 'GET', ['GET', 'HEAD'], true)) {
            header('Allow: GET, HEAD');
            wp_die(esc_html__('Écran en lecture seule.', 'imagine-site'), '', ['response' => 405]);
        }
    }

    public static function bilan(array $ids, array $contexte): array
    {
        $totaux = ['abonne' => 0, 'non_abonne' => 0, 'inconnu' => 0, 'a_retirer' => 0, 'absent' => 0];
        foreach (array_unique($ids) as $id) {
            $result = self::fiche((int)$id, $contexte);
            $totaux[$result['fiche']['statut'] ?? 'absent']++;
        }
        return $totaux;
    }

    public static function page(): void
    {
        self::verifier();
        nocache_headers();
        header('Cache-Control: private, no-store, no-cache, must-revalidate, max-age=0');
        echo '<div class="wrap" data-imagine-brevo><h1>' . esc_html__('Ce qui partirait vers Brevo', 'imagine-site') . '</h1><p>'
            . esc_html__('Lecture seule, calcul à la demande. Rien ne part, rien n’est enregistré. Aucun droit d’accès n’est modifié. Clés internes, correspondance Brevo à définir.', 'imagine-site') . '</p>';
        $raw = $_GET['compte'] ?? '';
        $id = is_string($raw) && preg_match('/^[1-9][0-9]*$/D', $raw) && (string)(int)$raw === $raw ? (int)$raw : 0;
        echo '<form method="get" action="' . esc_url(admin_url('admin.php')) . '"><input type="hidden" name="page" value="' . esc_attr(self::PAGE)
            . '"><label for="imagine-brevo-compte">' . esc_html__('Identifiant du compte', 'imagine-site') . '</label> <input type="number" min="1" id="imagine-brevo-compte" name="compte" value="'
            . esc_attr($id ? (string)$id : '') . '"> <button type="submit">' . esc_html__('Voir la fiche', 'imagine-site') . '</button></form>';
        try {
            $contexte = self::contexte();
            $totaux = self::bilan(get_users(['fields' => 'ID']), $contexte);
            $result = $id ? self::fiche($id, $contexte) : null;
            echo '<h2>' . esc_html__('Nombre de fiches par statut', 'imagine-site') . '</h2><table class="widefat striped"><tbody>';
            $labels = [
                'abonne' => __('Abonné', 'imagine-site'),
                'non_abonne' => __('Non-abonné', 'imagine-site'),
                'inconnu' => __('Inconnu', 'imagine-site'),
                'a_retirer' => __('À retirer', 'imagine-site'),
                'absent' => __('Sans fiche', 'imagine-site'),
            ];
            foreach ($labels as $key => $label) {
                echo '<tr><th scope="row">' . esc_html($label) . '</th><td data-brevo-total="' . esc_attr($key) . '">' . esc_html((string)$totaux[$key]) . '</td></tr>';
            }
            echo '</tbody></table>';
            if ($result !== null) {
                $reasons = [
                    'compte_absent' => __('Compte absent.', 'imagine-site'),
                    'email_non_recevable' => __('Compte sans email recevable.', 'imagine-site'),
                    'aucun_choix_lecteur' => __('Aucune newsletter choisie par le lecteur.', 'imagine-site'),
                    'desinscrit_de_tout' => __('Désinscrit de toutes les newsletters : à retirer.', 'imagine-site'),
                    'eligible' => __('Compte éligible.', 'imagine-site'),
                ];
                echo '<h2>' . esc_html__('Fiche du compte', 'imagine-site') . '</h2><p data-brevo-raison="' . esc_attr($result['raison']) . '">'
                    . esc_html($reasons[$result['raison']]) . '</p>';
                if ($result['fiche'] !== null) {
                    echo '<pre data-brevo-fiche>' . esc_html(wp_json_encode($result['fiche'], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE)) . '</pre>';
                }
            } else {
                echo '<p>' . esc_html__('Choisissez un identifiant de compte valide.', 'imagine-site') . '</p>';
            }
        } catch (\Throwable) {
            echo '<p data-brevo-indisponible>' . esc_html__('Lecture native indisponible : aucun nombre ni fiche de remplacement.', 'imagine-site') . '</p>';
        }
        echo '<p>' . esc_html__('Seul l’état actif signifie abonné, pas l’accès numérique. Bénéficiaire offert ou groupé : statut inconnu. Tarif absent, hors liste ou contradictoire : inconnu. Les attributs personnels viennent directement de C24 et de son consentement distinct.', 'imagine-site') . '</p></div>';
    }

    /** Liste fermée produit/variation natif => clé interne ; vide/invalide = tout inconnu. */
    public static function tarifs(mixed $value): array
    {
        if (!is_array($value)) {
            return [];
        }
        foreach ($value as $id => $code) {
            if (!preg_match('/^[1-9][0-9]*$/D', (string)$id)
                || !is_string($code) || !preg_match('/^[a-z][a-z0-9_-]{0,63}$/D', $code)) {
                return [];
            }
        }
        return $value;
    }

    /** WCS non mis en cache persistant, contrairement à get_users_subscriptions. */
    public static function contexte(): array
    {
        if (!function_exists('wcs_get_subscriptions') || !function_exists('wc_memberships_get_user_membership')) {
            throw new \RuntimeException('Source native indisponible.');
        }
        $tarifs = self::tarifs(get_option(self::TARIFS, []));
        $data = ['abonnements' => [], 'beneficiaires' => [], 'tarifs' => $tarifs];
        $seen = [];
        for ($page = 1; ; $page++) {
            $rows = wcs_get_subscriptions(
                [
                'subscriptions_per_page' => 100,
                'paged' => $page,
                'subscription_status' => 'any',
                'orderby' => 'ID',
                'order' => 'ASC',
                ]
            );
            if (!is_array($rows)) {
                throw new \RuntimeException('Abonnements illisibles.');
            }
            foreach ($rows as $sub) {
                if (!$sub instanceof \WC_Subscription || isset($seen[$sub->get_id()])) {
                    throw new \RuntimeException('Abonnement incohérent.');
                }
                $seen[$sub->get_id()] = true;
                $codes = [];
                foreach ($sub->get_items() as $item) {
                    $product = $item->get_variation_id() ?: $item->get_product_id();
                    $codes[] = $tarifs[$product] ?? '';
                }
                $data['abonnements'][(int)$sub->get_customer_id()][] = ['etat' => $sub->get_status(), 'tarifs' => $codes];
                // Réutilisation du contrat de lecture C13 : aucune déduction par email ou par droits C06.
                $relation = EnvoiRelations::beneficiaires($sub);
                if (in_array($relation['origine'], ['offert', 'groupe'], true)) {
                    $people = $relation['origine'] === 'groupe'
                        ? $relation['relation_native'] : $relation['beneficiaires'];
                    foreach ($people as $person) {
                        $id = (int)($person[$relation['origine'] === 'groupe' ? 'user_id' : 'id'] ?? 0);
                        if ($id > 0 && $id !== (int)$sub->get_customer_id() && get_userdata($id)) {
                            $data['beneficiaires'][$id] = true;
                        }
                    }
                }
            }
            if (count($rows) < 100) {
                break;
            }
        }
        return $data;
    }

    public static function fiche(int $id, ?array $contexte = null): array
    {
        $user = $id > 0 ? get_userdata($id) : false;
        $contexte ??= self::contexte();
        $coop = get_user_meta($id, Cooperateurs::META, true);
        return ContactBrevoRegles::fiche(
            [
            'existe' => (bool)$user, 'email_recevable' => $user && Newsletters::admissible($id),
            'email' => $user ? $user->user_email : '', 'catalogue' => array_column(Newsletters::catalogue(), 'id'),
            'preferences' => Newsletters::preferences($id), 'abonnements' => $contexte['abonnements'][$id] ?? [],
            'beneficiaire' => isset($contexte['beneficiaires'][$id]),
            'cooperateur' => is_array($coop) && ($coop['cooperateur'] ?? false) === true,
            'tarifs_autorises' => array_values($contexte['tarifs']),
            'personnalisation' => Personnalisation::attributsConnecteur($id),
            ]
        );
    }
}
