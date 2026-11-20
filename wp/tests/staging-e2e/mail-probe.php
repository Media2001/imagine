<?php

declare(strict_types=1);

namespace Imagine\E2E;

// No real transport exists: detect whether WordPress reaches PHPMailer::send().
if (!defined('ABSPATH') || wp_get_environment_type() !== 'staging') {
    throw new \RuntimeException('Synthetic staging only');
}
require_once ABSPATH . WPINC . '/PHPMailer/Exception.php';
require_once ABSPATH . WPINC . '/PHPMailer/PHPMailer.php';
require_once ABSPATH . WPINC . '/PHPMailer/SMTP.php';
require_once ABSPATH . WPINC . '/class-wp-phpmailer.php';
$spy = new class(true) extends \WP_PHPMailer {
    public int $e2eCalls = 0;
    public function send()
    {
        ++$this->e2eCalls;
        return true; // In-memory spy only: no sendmail, SMTP, HTTP or external action.
    }
};
$GLOBALS['phpmailer'] = $spy;
$result = wp_mail('probe@example.org', 'E2E_ONLY', 'Synthetic non-delivered mail probe');
echo 'E2E_JSON=' . wp_json_encode(['wp_mail_return' => $result, 'mail_dispatch_calls' => $spy->e2eCalls,
    'environment' => wp_get_environment_type(), 'real_sends' => 0]) . "\n";
