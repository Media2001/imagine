<?php

declare(strict_types=1);

namespace Imagine\Site;

use DateTimeImmutable;
use DateTimeZone;
use Imagine\Pilotage\Acces\Moteur;
use Imagine\Pilotage\Robots;
use WP_Post;

/** Adaptateur WordPress uniquement : aucune table de droits métier dupliquée. */
final class Paywall
{
    /** Mémoire PHP de cette requête seulement, jamais de transient/cache partagé. */
    private static array $decisions = [];
    private static ?DateTimeImmutable $requestInstant = null;
    private static string $readContext = '';

    public static function invalidate(): void
    {
        self::$decisions = [];
        // L'instant reste identique même si un droit est révoqué dans la requête.
    }

    private static function context(): string
    {
        global $wp_filter;
        $hooks = [];
        foreach ($wp_filter as $name => $hook) {
            if (preg_match('/^(get_(post|user)_metadata|(?:pre_)?option_imagine_acces_|woocommerce_subscription_get_|wc_memberships_user_membership_get_)/', $name)) {
                foreach ($hook->callbacks as $priority => $callbacks) {
                    $hooks[$name][$priority] = array_map(static fn (array $callback): int => $callback['accepted_args'], $callbacks);
                }
            }
        }
        return hash('sha256', serialize([$hooks, $_SERVER['HTTP_USER_AGENT'] ?? '', $_SERVER['REMOTE_ADDR'] ?? '']));
    }

    public static function managed(?WP_Post $post): bool
    {
        // Tous les articles natifs sont gouvernés : absence des deux métadonnées
        // n'est jamais assimilée à « ouvert ». L'ouverture doit être explicite.
        return $post && $post->post_type === 'post';
    }

    /** Aucun droit n'est inféré d'un cookie de mot de passe, UA ou en-tête de proxy. */
    public static function decision(WP_Post $post): array
    {
        try {
            $now = self::$requestInstant ??= new DateTimeImmutable(gmdate('Y-m-d H:i:s'), new DateTimeZone('UTC'));
            $context = self::context();
            if ($context !== self::$readContext) {
                self::invalidate();
                self::$readContext = $context;
            }
            $userId = get_current_user_id();
            $key = get_current_blog_id() . ':' . $post->ID . ':' . $userId;
            if (isset(self::$decisions[$key])) {
                return self::$decisions[$key];
            }
            $flag = get_post_meta($post->ID, 'imagine_reserve', true);
            $number = (int) get_post_meta($post->ID, 'imagine_numero_id', true);
            $issue = get_post($number);
            if (!metadata_exists('post', $post->ID, 'imagine_reserve')
                || !in_array($flag, ['', '0', '1', false, true, 0, 1], true)
                || !$issue || $issue->post_type !== 'imagine_numero') {
                throw new \RuntimeException('Métadonnées de contenu invalides.');
            }
            $date = (string) get_post_meta($number, 'imagine_sortie', true);
            $release = DateTimeImmutable::createFromFormat('!Y-m-d', $date, wp_timezone());
            if (!$release || $release->format('Y-m-d') !== $date) {
                throw new \RuntimeException('Date éditoriale invalide.');
            }
            $userId = get_current_user_id();
            $visitor = ['identifie' => $userId > 0, 'droits' => $userId ? self::rights($userId, $now) : []];
            $decision = self::deciderContenu(
                ['reserve' => in_array($flag, ['1', true, 1], true), 'numero' => (string) $number, 'type' => 'article',
                    'sortie' => $release, 'decouverte' => false],
                $visitor,
                self::robot($now),
                $now
            );
            return self::$decisions[$key] = ['complet' => $decision->complet, 'motif' => $decision->motif->value, 'bloc' => $decision->bloc->value];
        } catch (\Throwable) {
            $closed = ['complet' => false, 'motif' => 'adaptateur_indisponible', 'bloc' => 'abonnement'];
            if (isset($key)) {
                self::$decisions[$key] = $closed;
            }
            return $closed;
        }
    }

    /** Raccord C11 : même identité native que C08, contrat PDF exact du moteur C06. */
    public static function decisionPdf(WP_Post $issue): array
    {
        try {
            if ($issue->post_type !== 'imagine_numero' || $issue->post_status !== 'publish') {
                throw new \RuntimeException('Numéro indisponible.');
            }
            $date = get_post_meta($issue->ID, 'imagine_sortie', true);
            $release = is_string($date) ? DateTimeImmutable::createFromFormat('!Y-m-d', $date, wp_timezone()) : false;
            if (!$release || $release->format('Y-m-d') !== $date) {
                throw new \RuntimeException('Date éditoriale invalide.');
            }
            $now = new DateTimeImmutable(gmdate('Y-m-d H:i:s'), new DateTimeZone('UTC'));
            $userId = get_current_user_id();
            $decision = self::deciderContenu(
                ['reserve' => true, 'numero' => (string) $issue->ID, 'type' => 'pdf',
                    'sortie' => $release, 'decouverte' => false],
                ['identifie' => $userId > 0, 'droits' => $userId ? self::rights($userId, $now) : []],
                self::robot($now),
                $now
            );
            return ['complet' => $decision->complet, 'motif' => $decision->motif->value, 'bloc' => $decision->bloc->value];
        } catch (\Throwable) {
            return ['complet' => false, 'motif' => 'adaptateur_indisponible', 'bloc' => 'abonnement'];
        }
    }

    /** Point de décision commun articles/PDF ; aucun droit PDF n'est inventé par le raccord. */
    public static function deciderContenu(
        array $contenu,
        array $visiteur,
        Robots\Decision $robot,
        DateTimeImmutable $instant
    ): \Imagine\Pilotage\Acces\Decision {
        return (new Moteur())->decider(
            $contenu,
            $visiteur,
            $robot,
            $instant,
            null,
            (new \Imagine\Pilotage\Acces\AdministrationReglages())->lire()
        );
    }

    private static function date(mixed $value, bool $unlimited = false): DateTimeImmutable
    {
        if (($value === null || $value === '' || $value === '0') && $unlimited) {
            return new DateTimeImmutable('9999-12-31 00:00:00', new DateTimeZone('UTC'));
        }
        if (!is_string($value)) {
            throw new \RuntimeException('Date native absente.');
        }
        $date = DateTimeImmutable::createFromFormat('!Y-m-d H:i:s', $value, new DateTimeZone('UTC'));
        if (!$date || $date->format('Y-m-d H:i:s') !== $value) {
            throw new \RuntimeException('Date native invalide.');
        }
        return $date;
    }

    private static function rights(int $userId, DateTimeImmutable $now): array
    {
        if (!function_exists('wc_memberships_get_user_memberships') || !function_exists('wcs_get_subscription')) {
            throw new \RuntimeException('Extensions de droits indisponibles.');
        }
        $rights = [];
        $user = get_userdata($userId);
        if ($user && array_intersect(['administrator', 'editor', 'imagine_referent_abonnements'], $user->roles)) {
            $rights[] = ['type' => 'equipe', 'role' => in_array('administrator', $user->roles, true) ? 'administration' : 'redaction'];
        }
        $plans = get_option('imagine_acces_plans', []);
        if (!is_array($plans)) {
            throw new \RuntimeException('Plans de lecture non configurés.');
        }
        foreach (wc_memberships_get_user_memberships($userId, ['status' => 'any']) ?? [] as $membership) {
            $type = $plans[$membership->get_plan_id()] ?? null;
            if (!in_array($type, ['abonnement', 'offert', 'groupe'], true)) {
                continue;
            }
            if ($membership->get_user_id() !== $userId) {
                throw new \RuntimeException('Propriétaire Memberships incohérent.');
            }
            $start = self::date($membership->get_start_date());
            // Ne pas utiliser l'allongement automatique de fin lié à une pause Memberships.
            $end = self::date($membership->get_end_date('mysql', false), true);
            $status = $membership->get_status();
            $state = match ($status) {
                'active', 'complimentary' => 'actif',
                'expired', 'cancelled' => 'expire',
                'pending', 'delayed' => 'virement_non_valide',
                default => 'suspendu',
            };
            $subscriptionId = (int) get_post_meta($membership->get_id(), '_subscription_id', true);
            if ($subscriptionId) {
                $integration = wc_memberships()->get_integrations_instance()->get_subscriptions_instance();
                $subscription = $integration->get_subscription_from_membership($membership->get_id());
                if (!$subscription || (int) $subscription->get_customer_id() !== $userId) {
                    throw new \RuntimeException('Lien natif Subscriptions incohérent.');
                }
                $start = max($start, self::date($subscription->get_date('start', 'gmt')));
                $end = min($end, self::date($subscription->get_date('end', 'gmt'), true));
                $subStatus = $subscription->get_status();
                if ($subStatus === 'on-hold' && in_array($status, ['paused', 'active'], true)) {
                    $from = $subscription->get_meta('_imagine_acces_grace_debut');
                    $until = $subscription->get_meta('_imagine_acces_grace_fin');
                    // Sans fenêtre explicite, un on-hold est fermé. Pas de grâce automatique.
                    if ($from !== '' && $until !== '') {
                        $graceStart = self::date($from);
                        $graceEnd = self::date($until);
                        if ($graceStart < $graceEnd && $graceStart <= $now && $now < $graceEnd) {
                            $state = 'grace';
                            $end = min($end, $graceEnd);
                        } else {
                            $state = 'suspendu';
                        }
                    } else {
                        $state = 'suspendu';
                    }
                } elseif ($subStatus === 'pending'
                    || ($subStatus === 'on-hold' && in_array($status, ['pending', 'delayed'], true))) {
                    // Première commande en attente : pas une suspension d'un abonnement actif.
                    $state = 'virement_non_valide';
                } elseif (!in_array($subStatus, ['active', 'pending-cancel'], true)) {
                    $state = in_array($subStatus, ['expired', 'cancelled'], true) ? 'expire' : 'suspendu';
                }
            }
            $rights[] = ['type' => $type, 'etat' => $state, 'debut' => $start, 'fin' => $end];
        }
        return $rights;
    }

    private static function robot(DateTimeImmutable $now): Robots\Decision
    {
        // Hors ligne B00 : pas de DNS bloquant non borné ni appel externe caché.
        $dns = new class implements Robots\Dns {
            public function inverse(string $ip, int $delaiMs): array
            {
                throw new \RuntimeException('Résolution DNS désactivée sur la démonstration hors ligne.');
            }
            public function directe(string $nom, int $delaiMs): array
            {
                throw new \RuntimeException('Résolution DNS désactivée sur la démonstration hors ligne.');
            }
        };
        $clock = new class implements Robots\HorlogeMonotone {
            public function millisecondes(): int
            {
                return (int) (hrtime(true) / 1000000);
            }
        };
        $configuration = new Robots\Configuration([
            new Robots\Robot('google', ['Googlebot'], Robots\Methode::Dns, ['googlebot.com']),
            new Robots\Robot('bing', ['bingbot'], Robots\Methode::Dns, ['search.msn.com']),
        ]);
        $verifier = new Robots\Verificateur($configuration, $dns, new Robots\CacheMemoire(), $clock);
        return $verifier->verifier((string) ($_SERVER['HTTP_USER_AGENT'] ?? ''), (string) ($_SERVER['REMOTE_ADDR'] ?? ''), $now);
    }

    /** L'extrait est une donnée éditoriale publique; jamais une découpe du corps réservé. */
    public static function excerpt(WP_Post $post): string
    {
        $text = trim(wp_strip_all_tags(strip_shortcodes($post->post_excerpt)));
        $limit = get_option('imagine_acces_extrait_caracteres', 320);
        $limit = is_numeric($limit) ? max(40, min(1000, (int) $limit)) : 320;
        return $text === '' ? __('Cet article est réservé aux abonnés.', 'imagine-site') : mb_substr($text, 0, $limit);
    }

    public static function sanitizePosts(array $posts): array
    {
        foreach ($posts as $i => $post) {
            if (!$post instanceof WP_Post || !self::managed($post) || self::decision($post)['complet']) {
                continue;
            }
            // Le cache objet natif reste intact : seul le clone retourné à cette requête change.
            $safe = clone $post;
            $safe->post_excerpt = self::excerpt($post);
            $safe->post_content = '<p>' . esc_html($safe->post_excerpt) . '</p>';
            $safe->post_content_filtered = '';
            $posts[$i] = $safe;
        }
        return $posts;
    }

    public static function content(string $content): string
    {
        $post = get_post();
        return self::managed($post) && !self::decision($post)['complet']
            ? '<p>' . esc_html(self::excerpt($post)) . '</p>' : $content;
    }

    public static function rest($response, WP_Post $post)
    {
        if (self::managed($post) && !self::decision($post)['complet']) {
            $data = $response->get_data();
            $text = self::excerpt($post);
            foreach (['content', 'excerpt'] as $field) {
                if (isset($data[$field])) {
                    $data[$field] = ['rendered' => '<p>' . esc_html($text) . '</p>', 'protected' => true];
                }
            }
            unset($data['password']);
            $response->set_data($data);
        }
        return $response;
    }

    public static function cacheHeaders(array $headers): array
    {
        foreach (array_keys($headers) as $key) {
            if (in_array(strtolower($key), ['etag', 'last-modified', 'cache-control', 'expires', 'vary'], true)) {
                unset($headers[$key]);
            }
        }
        return $headers + [
            'Cache-Control' => 'no-cache, no-store, private, must-revalidate, max-age=0',
            'Expires' => 'Wed, 11 Jan 1984 05:00:00 GMT', 'Vary' => 'Cookie, Authorization, User-Agent',
        ];
    }

    public static function share(): void
    {
        $post = get_queried_object();
        if (!$post instanceof WP_Post || !self::managed($post)) {
            return;
        }
        $text = self::excerpt($post);
        echo '<meta name="description" content="' . esc_attr($text) . '">' . "\n";
        echo '<meta property="og:description" content="' . esc_attr($text) . '">' . "\n";
        echo '<meta name="twitter:description" content="' . esc_attr($text) . '">' . "\n";
        if (!metadata_exists('post', $post->ID, 'imagine_reserve')
            || !in_array(get_post_meta($post->ID, 'imagine_reserve', true), ['', '0', false, 0], true)) {
            $schema = ['@context' => 'https://schema.org', '@type' => 'NewsArticle', 'headline' => get_the_title($post),
                'description' => $text, 'isAccessibleForFree' => false,
                'hasPart' => ['@type' => 'WebPageElement', 'isAccessibleForFree' => false, 'cssSelector' => '.imagine-paywall-body']];
            echo '<script type="application/ld+json">' . wp_json_encode($schema, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT) . '</script>' . "\n";
        }
    }

    /** Masque le corps SQL avant appariement ET classement, pas seulement au rendu. */
    public static function searchSql(string $sql, \WP_Query $query): string
    {
        global $wpdb;
        if ($sql === '' || (string) $query->get('s') === '') {
            return $sql;
        }
        $allowed = [];
        try {
            // Pas de WP_Query récursif, pas de liste persistante de droits.
            $ids = $wpdb->get_col("SELECT ID FROM {$wpdb->posts} WHERE post_type = 'post'");
            if ($wpdb->last_error !== '') {
                throw new \RuntimeException('Inventaire de recherche indisponible.');
            }
            foreach ($ids as $id) {
                $post = get_post((int) $id);
                if ($post instanceof WP_Post && self::decision($post)['complet']) {
                    $allowed[] = (int) $id;
                }
            }
        } catch (\Throwable) {
            $allowed = []; // Tout corps d'article fermé si la préparation échoue.
        }
        $column = $wpdb->posts . '.post_content';
        $grant = $allowed ? ' OR ' . $wpdb->posts . '.ID IN (' . implode(',', $allowed) . ')' : '';
        $safe = '(CASE WHEN ' . $wpdb->posts . ".post_type <> 'post'" . $grant
            . ' THEN ' . $column . " ELSE '' END)";
        // Ne jamais remplacer un identifiant ressemblant dans une chaîne SQL citée
        // (le terme utilisateur est déjà échappé par WP_Query / wpdb::prepare).
        $pattern = "~'(?:[^'\\\\\\\\]|\\\\\\\\.|'')*'|(?<![a-zA-Z0-9_])"
            . preg_quote($column, '~') . "\\b~s";
        return preg_replace_callback($pattern, static fn (array $m): string =>
            $m[0][0] === "'" ? $m[0] : $safe, $sql) ?? ' AND 1=0 ';
    }

    public static function register(): void
    {
        foreach (['added_post_meta', 'updated_post_meta', 'deleted_post_meta',
            'added_user_meta', 'updated_user_meta', 'deleted_user_meta',
            'added_option', 'updated_option', 'deleted_option', 'clean_post_cache',
            'clean_user_cache', 'switch_blog', 'set_user_role', 'add_user_role', 'remove_user_role',
            'woocommerce_after_order_object_save', 'woocommerce_subscription_status_updated',
            'wc_memberships_user_membership_status_changed'] as $hook) {
            add_action($hook, [self::class, 'invalidate'], PHP_INT_MAX, 0);
        }
        if (!defined('DONOTCACHEPAGE')) {
            define('DONOTCACHEPAGE', true);
        }
        // Évite qu'un flux se termine en 304 avant l'émission des en-têtes privés.
        unset($_SERVER['HTTP_IF_MODIFIED_SINCE'], $_SERVER['HTTP_IF_NONE_MATCH']);
        add_filter('posts_search', [self::class, 'searchSql'], PHP_INT_MAX, 2);
        add_filter('posts_orderby', [self::class, 'searchSql'], PHP_INT_MAX, 2);
        add_filter('wp_headers', [self::class, 'cacheHeaders'], PHP_INT_MAX);
        add_filter('rest_post_dispatch', static function ($response) {
            $response->set_headers(self::cacheHeaders($response->get_headers()));
            return $response;
        }, PHP_INT_MAX);
        add_filter('the_posts', static function (array $posts): array {
            return is_admin() || (defined('WP_CLI') && WP_CLI) ? $posts : self::sanitizePosts($posts);
        }, PHP_INT_MAX);
        // Arbitrage B00 du 23/11 : aucun second verrou natif sur les articles C08.
        add_filter('wp_insert_post_data', static function (array $data): array {
            if (($data['post_type'] ?? '') === 'post') {
                $data['post_password'] = '';
            }
            return $data;
        }, PHP_INT_MAX);
        add_filter('post_password_required', static function (bool $required, WP_Post $post): bool {
            // Le résultat dépend exclusivement de la décision C08, jamais d'un secret natif.
            return self::managed($post) ? !self::decision($post)['complet'] : $required;
        }, PHP_INT_MAX, 2);
        foreach (['the_content', 'the_content_feed'] as $hook) {
            add_filter($hook, [self::class, 'content'], PHP_INT_MAX);
        }
        foreach ([1, PHP_INT_MAX] as $priority) {
            add_filter('get_the_excerpt', static fn (string $text, WP_Post $post): string =>
                self::managed($post) ? self::excerpt($post) : $text, $priority, 2);
        }
        add_filter('rest_prepare_post', [self::class, 'rest'], PHP_INT_MAX, 2);
        add_filter('oembed_response_data', static function (array $data, WP_Post $post): array {
            if (self::managed($post)) {
                $data['html'] = '<blockquote><a href="' . esc_url(get_permalink($post)) . '">' . esc_html(get_the_title($post))
                    . '</a><p>' . esc_html(self::excerpt($post)) . '</p></blockquote>';
            }
            return $data;
        }, PHP_INT_MAX, 2);
        // API historique sans garde content systématique : désactivée sur ce squelette.
        add_filter('xmlrpc_methods', static fn (array $methods): array => [], PHP_INT_MAX);
        add_action('wp_head', [self::class, 'share'], 5);
    }
}
