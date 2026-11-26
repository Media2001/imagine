<?php

declare(strict_types=1);

namespace Imagine\Site;

/** Trois écrans serveur dans le seul menu Imagine ; brouillon privé, non dans l'URL. */
final class CommandeAdmin
{
    public const PAGE = 'imagine-commandes';
    private static ?array $courant = null;

    private static function t(string $text): string
    {
        return __($text, 'imagine-site');
    }

    public static function autorise(): bool
    {
        return current_user_can('manage_options') || (current_user_can(EcheancesAdmin::CAP)
            && current_user_can('imagine_creer_compte_client'));
    }

    public static function register(): void
    {
        // Traiter les écritures avant admin-header.php : vrais statuts HTTP de refus.
        add_action('admin_init', static function (): void {
            global $pagenow;
            if ($pagenow !== 'admin.php' || ($_GET['page'] ?? '') !== self::PAGE
                || ($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
                return;
            }
            if (!self::autorise()) {
                self::refus();
            }
            nocache_headers();
            try {
                CommandeNative::garde();
                self::$courant = self::traiter();
            } catch (\Throwable) {
                wp_die(self::t('Saisie refusée ou résultat incomplet. Aucun paiement validé. Relire les objets natifs avant de recommencer.'), '', ['response' => 409]);
            }
        });
        add_action('admin_menu', static function (): void {
            if (self::autorise()) {
                add_submenu_page('imagine', self::t('Commande pour un client'), self::t('Commande pour un client'),
                    current_user_can('manage_options') ? 'manage_options' : EcheancesAdmin::CAP,
                    self::PAGE, [self::class, 'page']);
            }
        }, 115);
        add_filter('woocommerce_prevent_admin_access', static function (bool $prevent): bool {
            global $pagenow;
            // Inclure les refus POST : le contrôle de capacité ci-dessous rend le 403.
            return $pagenow === 'admin.php' && ($_GET['page'] ?? '') === self::PAGE ? false : $prevent;
        });
        add_action('admin_post_imagine_c16_creer', [self::class, 'refus']);
        add_action('admin_post_nopriv_imagine_c16_creer', [self::class, 'refus']);
    }

    public static function refus(): void
    {
        wp_die(self::t('Utiliser le parcours administratif sécurisé.'), '', ['response' => 403]);
    }

    private static function champ(string $key, string $label, string $value = '', bool $required = false): void
    {
        echo '<p><label for="c16-' . esc_attr($key) . '">' . esc_html(self::t($label)) . '</label><br><input id="c16-'
            . esc_attr($key) . '" name="' . esc_attr($key) . '" value="' . esc_attr($value) . '" type="text" class="regular-text"'
            . ($required ? ' required' : '') . '></p>';
    }

    private static function form(string $action, string $token = ''): void
    {
        echo '<form method="post" action="' . esc_url(admin_url('admin.php?page=' . self::PAGE)) . '">';
        echo '<input type="hidden" name="c16_action" value="' . esc_attr($action) . '">';
        echo '<input type="hidden" name="token" value="' . esc_attr($token) . '">';
        wp_nonce_field('imagine_c16_' . $action . ':' . $token);
    }

    private static function key(string $token): string
    {
        return 'imagine_c16_brouillon_' . get_current_user_id() . '_' . $token;
    }

    private static function draft(string $token): array
    {
        if (!preg_match('/^[a-f0-9]{32}$/D', $token)) {
            throw new \InvalidArgumentException('Brouillon invalide.');
        }
        $draft = get_transient(self::key($token));
        if (!is_array($draft) || $draft['qui'] !== get_current_user_id()) {
            throw new \InvalidArgumentException('Brouillon expiré ou étranger.');
        }
        return $draft;
    }

    private static function stocker(array $draft): void
    {
        set_transient(self::key($draft['token']), $draft, HOUR_IN_SECONDS);
        if (get_transient(self::key($draft['token'])) !== $draft) {
            throw new \RuntimeException('Brouillon non conservé.');
        }
    }

    private static function traiter(): ?array
    {
        $action = CommandeRegles::texte($_POST, 'c16_action');
        $token = CommandeRegles::texte($_POST, 'token');
        $nonce = $_POST['_wpnonce'] ?? null;
        if (!in_array($action, ['choisir', 'preparer', 'creer'], true) || !is_string($nonce)
            || !wp_verify_nonce($nonce, 'imagine_c16_' . $action . ':' . $token)) {
            wp_die(self::t('Jeton de sécurité invalide.'), '', ['response' => 403]);
        }
        if ($action === 'choisir') {
            $client = CommandeRegles::client(wp_unslash($_POST));
            $known = CommandeNative::clientExistant($client);
            // Résoudre l'email connu dès l'écran 1, sans réécriture du compte.
            if ($known && $client['mode'] !== 'direct') {
                $client = ['mode' => 'existant', 'id' => (int) $known->ID];
            }
            $draft = ['qui' => get_current_user_id(), 'token' => str_replace('-', '', wp_generate_uuid4()),
                'client' => $client, 'etape' => 2];
            self::stocker($draft);
            return $draft;
        }
        if ($action === 'preparer') {
            $draft = self::draft($token);
            if ($draft['etape'] !== 2) {
                throw new \LogicException('Ordre des écrans invalide.');
            }
            $data = CommandeRegles::commande(wp_unslash($_POST), $draft['client']['mode'] === 'direct');
            if ($data['adresse']['country'] !== '' && !isset(WC()->countries->get_countries()[$data['adresse']['country']])) {
                throw new \InvalidArgumentException('Pays inconnu.');
            }
            $p = CommandeNative::produits()[$data['produit']] ?? null;
            if (!$p) {
                throw new \InvalidArgumentException('Produit absent du catalogue fictif.');
            }
            $draft['commande'] = $data;
            $draft['empreinte'] = CommandeNative::empreinte($p);
            $draft['etape'] = 3;
            self::stocker($draft);
            return $draft;
        }
        if (($_POST['confirmer'] ?? '') !== 'oui') {
            throw new \InvalidArgumentException('Confirmation explicite requise.');
        }
        global $wpdb;
        $lock = 'imagine_c16_' . substr(hash('sha256', DB_NAME . ':' . self::key($token)), 0, 48);
        if ((string) $wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s, 5)', $lock)) !== '1') {
            throw new \RuntimeException('Brouillon en cours.');
        }
        try {
            // Aucune lecture avant GET_LOCK : le concurrent a pu finaliser pendant l'attente.
            // Le brouillon avec expiration est non autoloadé ; invalider ses deux caches natifs.
            $key = self::key($token);
            wp_cache_delete($key, 'transient');
            wp_cache_delete('_transient_' . $key, 'options');
            wp_cache_delete('_transient_timeout_' . $key, 'options');
            $draft = self::draft($token);
            if (isset($draft['resultat'])) {
                return $draft; // Double-clic / retour navigateur : même commande.
            }
            if ($draft['etape'] !== 3 || isset($draft['commence'])) {
                throw new \LogicException('Résultat incomplet : relire les objets natifs avant de recommencer.');
            }
            $draft['commence'] = true;
            self::stocker($draft); // Une interruption ne permet jamais une création aveugle en double.
            $draft['resultat'] = CommandeNative::creer($draft);
            self::stocker($draft);
            return $draft;
        } finally {
            $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)', $lock));
        }
    }

    public static function page(): void
    {
        if (!self::autorise()) {
            wp_die(self::t('Accès réservé au référent administratif.'), '', ['response' => 403]);
        }
        nocache_headers();
        try {
            CommandeNative::garde();
            $draft = self::$courant;
            if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'POST' && isset($_GET['token'])) {
                $draft = self::draft(CommandeRegles::texte($_GET, 'token'));
            }
        } catch (\Throwable $e) {
            wp_die(esc_html(self::t('Saisie refusée ou résultat incomplet. Aucun paiement validé. Relire la commande native avant de recommencer.')),
                '', ['response' => 409]);
        }
        $step = $draft['etape'] ?? 1;
        echo '<div class="wrap" data-imagine-etape="' . esc_attr((string) $step) . '"><h1>' . esc_html(self::t('Commande pour un client')) . '</h1><p>'
            . esc_html(self::t('Démonstration fictive hors ligne — 1. Client · 2. Commande · 3. Confirmation. Aucun email, aucun paiement validé, aucun accès accordé.')) . '</p>';
        if ($step === 1) {
            self::client();
        } elseif ($step === 2) {
            self::commande($draft);
        } else {
            self::confirmation($draft);
        }
        echo '<p>' . esc_html(self::t('Hors de ce lot : Don · Pack · Abonnement offert · Abonnement groupé — emplacements seulement.')) . '</p></div>';
    }

    private static function client(): void
    {
        echo '<h2>' . esc_html(self::t('1. Le client')) . '</h2><form method="get"><input type="hidden" name="page" value="' . esc_attr(self::PAGE) . '">';
        $query = isset($_GET['recherche']) ? CommandeRegles::texte(wp_unslash($_GET), 'recherche') : '';
        self::champ('recherche', 'Rechercher par nom, email ou localité', $query);
        submit_button(self::t('Rechercher'), 'secondary', '', false);
        echo '</form>';
        foreach (CommandeNative::recherche($query) as $user) {
            self::form('choisir');
            echo '<input type="hidden" name="mode" value="existant"><input type="hidden" name="client" value="' . esc_attr((string) $user->ID) . '"><p>'
                . esc_html($user->display_name . ' — ' . $user->user_email . ' — ' . get_user_meta($user->ID, 'shipping_city', true)) . '</p>';
            submit_button(self::t('Choisir ce client'), 'secondary', '', false);
            echo '</form>';
        }
        echo '<h3>' . esc_html(self::t('Créer un client (une adresse connue reprend le compte existant)')) . '</h3>';
        self::form('choisir');
        echo '<input type="hidden" name="mode" value="nouveau">';
        self::champ('nom', 'Nom du client fictif', '', true);
        self::champ('email', 'Adresse électronique (vide si sans email)');
        echo '<p><label><input type="checkbox" name="sans_email" value="1"> ' . esc_html(self::t('Sans email — adresse technique interne, exclue de tous les envois')) . '</label></p>';
        submit_button(self::t('Continuer'), 'primary', '', false);
        echo '</form><h3>' . esc_html(self::t('Vente sans identité')) . '</h3>';
        self::form('choisir');
        echo '<input type="hidden" name="mode" value="direct">';
        submit_button(self::t('Vente directe — compte générique fictif'), 'secondary', '', false);
        echo '</form>';
    }

    private static function commande(array $draft): void
    {
        $user = CommandeNative::clientExistant($draft['client']);
        echo '<h2>' . esc_html(self::t('2. La commande')) . '</h2><p>' . esc_html($user?->display_name ?? ($draft['client']['nom'] ?? self::t('Vente directe — fictif'))) . '</p>';
        self::form('preparer', $draft['token']);
        echo '<p><label for="c16-produit">' . esc_html(self::t('Produit fictif')) . '</label><br><select id="c16-produit" name="produit" required>';
        foreach (CommandeNative::produits() as $p) {
            echo '<option value="' . esc_attr((string) $p->get_id()) . '">' . esc_html($p->get_name() . ' — ' . $p->get_price() . ' ' . get_woocommerce_currency()) . '</option>';
        }
        echo '</select></p>';
        $fields = ['first_name' => 'Prénom', 'last_name' => 'Nom', 'address_1' => 'Adresse de livraison', 'address_2' => 'Complément',
            'postcode' => 'Code postal', 'city' => 'Localité', 'country' => 'Pays (code à deux lettres, BE / FR…)'];
        foreach ($fields as $key => $label) {
            $value = $user ? (string) get_user_meta($user->ID, 'shipping_' . $key, true) : '';
            self::champ($key, $label, $value, $draft['client']['mode'] !== 'direct' && $key !== 'address_2');
        }
        echo '<p><label for="c16-paiement">' . esc_html(self::t('Mode de paiement hors ligne')) . '</label><br><select id="c16-paiement" name="paiement"><option value="bacs">'
            . esc_html(self::t('Virement')) . '</option><option value="imagine_papier">' . esc_html(self::t('Mandat papier')) . '</option></select></p>';
        echo '<p>' . esc_html(self::t('Prix fictif du catalogue uniquement ; aucun port ni taxe Imagine inventé. Les coordonnées des comptes préexistants restent inchangées. Sans identité : adresse facultative.')) . '</p><p>'
            . esc_html(self::t(CommandeNative::adresseNouveau()
                ? 'Nouveau compte uniquement : adresse initialisée sur le compte à la confirmation, ainsi que sur la commande et la souscription. Réglage à confirmer par Imagine.'
                : 'Adresse sur la commande et la souscription seulement ; pas de recherche par localité pour ce nouveau compte. Réglage à confirmer par Imagine.')) . '</p>';
        submit_button(self::t('Vérifier la commande'), 'primary', '', false);
        echo '</form>';
    }

    private static function confirmation(array $draft): void
    {
        echo '<h2>' . esc_html(self::t('3. La confirmation')) . '</h2>';
        if (isset($draft['resultat'])) {
            $id = $draft['resultat']['commande'];
            echo '<p data-imagine-commande="' . esc_attr((string) $id) . '">' . esc_html(sprintf(self::t('Commande native #%d créée en attente de paiement. Aucun accès accordé par C16.'), $id)) . '</p><p><a href="'
                . esc_url(admin_url('admin.php?page=imagine-echeances&vue=virements')) . '">' . esc_html(self::t('Virements à valider — Échéances')) . '</a></p>';
        } else {
            $user = CommandeNative::clientExistant($draft['client']);
            $p = CommandeNative::produits()[$draft['commande']['produit']] ?? null;
            echo '<p>' . esc_html($user?->display_name ?? ($draft['client']['nom'] ?? self::t('Vente directe — fictif'))) . '</p><p>'
                . esc_html(($p?->get_name() ?? self::t('Produit disparu')) . ' — ' . ($p?->get_price() ?? '?') . ' ' . get_woocommerce_currency())
                . '</p><p>' . esc_html(implode(' · ', array_filter($draft['commande']['adresse']))) . '</p><p>'
                . esc_html($draft['commande']['paiement'] === 'bacs' ? self::t('Virement') : self::t('Mandat papier')) . '</p>';
            self::form('creer', $draft['token']);
            echo '<p><label><input type="checkbox" name="confirmer" value="oui" required> ' . esc_html(self::t('Je confirme cette saisie fictive, sans paiement reçu.')) . '</label></p>';
            submit_button(self::t('Créer la commande en attente'), 'primary', '', false);
            echo '</form>';
        }
        echo '<p><a href="' . esc_url(admin_url('admin.php?page=' . self::PAGE)) . '">' . esc_html(self::t('Recommencer ou abandonner sans créer')) . '</a></p>';
    }
}
