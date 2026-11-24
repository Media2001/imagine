<?php
declare(strict_types=1);
require '/subject/files.php';
$root = '/scratch/native-file-policy-' . bin2hex(random_bytes(6));
mkdir($root . '/wp-content/uploads/2026/11', 0755, true);
mkdir($root . '/wp-content/uploads/woocommerce_uploads', 0755, true);
file_put_contents($root . '/.imagine-staging-offline', "OFFLINE_COPY\n");
file_put_contents($root . '/wp-content/uploads/2026/11/issue.zip', 'FICTION DATED ARCHIVE');
file_put_contents($root . '/wp-content/uploads/woocommerce_uploads/archive-issue.pdf', '%PDF FICTION');
file_put_contents($root . '/wp-content/uploads/woocommerce_uploads/private.csv', 'FICTION EXPORT');
$files = new \Imagine\Staging\Files($root);
$files->purge();
if (!is_file($root . '/wp-content/uploads/2026/11/issue.zip')
    || !is_file($root . '/wp-content/uploads/woocommerce_uploads/archive-issue.pdf')
    || is_file($root . '/wp-content/uploads/woocommerce_uploads/private.csv')) {
    throw new RuntimeException('DATED_MEDIA_POLICY_FAILED');
}
$files->verify();
echo "NATIVE_FILE_POLICY_PASS\n";
