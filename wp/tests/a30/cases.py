"""Extend exact closed A13 fixtures in disposable input directories, never repo."""
import csv
import io
from pathlib import Path


def five_issues_bytes(clean):
    rows = list(csv.reader(io.StringIO(clean.decode('utf-8')), delimiter=';'))[:26]
    for number, row in enumerate(rows[1:], 1):
        if 11 <= number <= 15:
            row[6] = ''
        if 16 <= number <= 20:
            row[7] = 'type-a-decider-fictif'
        if 21 <= number <= 25:
            row[9] = 'illisible-fictif'
    stream = io.StringIO(newline='')
    csv.writer(stream, delimiter=';', lineterminator='\n').writerows(rows)
    return stream.getvalue().encode('utf-8')


EXPECTED_LINES = {'compte_a_creer': list(range(2, 7)), 'compte_existant': list(range(7, 12)),
                  'sans_email': list(range(12, 17)), 'type_a_decider': list(range(17, 22)),
                  'refuse_a13': list(range(22, 27))}

# Every native payload stays in memory or inside its own disposable site.
CHANNELS = {
    'direct_stdout': "fwrite(STDOUT, 'A30_STDOUT_PRIVATE_CANARY');",
    'direct_stderr': "fwrite(STDERR, 'A30_STDERR_PRIVATE_CANARY');",
    'display_exit': "echo 'A30_DISPLAY_PRIVATE_CANARY'; exit(0);",
    'shutdown_stdout': "register_shutdown_function(static function () { fwrite(STDOUT, 'A30_SHUTDOWN_PRIVATE_CANARY'); });",
    'shutdown_stderr': "register_shutdown_function(static function () { fwrite(STDERR, 'A30_SHUTDOWN_PRIVATE_CANARY'); });",
    'shutdown_display': "register_shutdown_function(static function () { echo 'A30_SHUTDOWN_PRIVATE_CANARY'; });",
    'silent_exit': 'exit(0);',
    'forged_success': 'fwrite(STDOUT, "A30_OK\\n"); exit(0);',
    'invalid_utf8': 'fwrite(STDERR, chr(255));',
    'oversize': "fwrite(STDOUT, str_repeat('A30_PRIVATE_CANARY', 8192));",
}
TARGET = "foreach ($_SERVER['argv'] as $arg) { if (str_starts_with($arg, '--output=')) { $dir=substr($arg,9); } }"
CHANNELS.update({
    'shutdown_valid_json': "register_shutdown_function(static function () { " + TARGET
        + " $p=$dir.'/result.json'; $d=json_decode(file_get_contents($p),true); $d['rows'][0]['issue']='compte_existant'; file_put_contents($p,json_encode($d)); });",
    'shutdown_extra_string': "register_shutdown_function(static function () { " + TARGET
        + " $p=$dir.'/result.json'; $d=json_decode(file_get_contents($p),true); $d['private']='A30_JSON_PRIVATE_CANARY'; file_put_contents($p,json_encode($d)); });",
    'shutdown_extra_file': "register_shutdown_function(static function () { " + TARGET
        + " file_put_contents($dir.'/extra.txt', 'A30_FILE_PRIVATE_CANARY'); });",
    'shutdown_partial': "register_shutdown_function(static function () { " + TARGET + " unlink($dir.'/result.json'); });",
})
