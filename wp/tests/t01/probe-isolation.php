<?php

declare(strict_types=1);

$checks = [];
$checks['repository_read_only'] = @file_put_contents('/repo/wp/tests/t01/.forbidden-write', 'fiction') === false;
$checks['rootfs_read_only'] = @file_put_contents('/t01-forbidden-write', 'fiction') === false;
$temporary = '/tmp/t01-canary-' . bin2hex(random_bytes(8));
$checks['temporary_writable'] = file_put_contents($temporary, 'fiction') === 7 && unlink($temporary);
$socket = @stream_socket_client('tcp://1.1.1.1:443', $errno, $message, 1);
$checks['external_network_unreachable'] = $socket === false;
if (is_resource($socket)) {
    fclose($socket);
}
echo json_encode($checks, JSON_THROW_ON_ERROR) . "\n";
exit(in_array(false, $checks, true) ? 1 : 0);
