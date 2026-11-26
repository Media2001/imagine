"""Fourth-pass diagnostics: synthetic errors, never source values."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parents[2] / 'outils/staging-court'
sys.path.insert(0, str(TOOLS))


class DatabaseFailure(unittest.TestCase):
    def test_duplicate_error_keeps_coordinates_not_values(self):
        import diagnostics
        with tempfile.TemporaryDirectory() as tmp:
            sql = Path(tmp) / 'validated.sql'
            sql.write_bytes(b'CREATE TABLE `wp_options` (`id` bigint);\nINSERT INTO `wp_options` VALUES (1);\n')
            error = diagnostics.database_error(b"ERROR 1062 (23000) at line 2: Duplicate entry 'FICTION_PRIVATE@example.org' for key 'x'", sql)
            self.assertEqual({'errno': 1062, 'sqlstate': '23000', 'line': 2, 'statement': 'INSERT', 'table': 'wp_options'}, error)
            self.assertNotIn('FICTION', json.dumps(error))
            self.assertNotIn('Duplicate', json.dumps(error))

    def test_external_timeout_is_named_and_duration_recorded(self):
        import diagnostics
        with mock.patch.object(diagnostics.subprocess, 'run', side_effect=subprocess.TimeoutExpired(['fixture'], 17)):
            with self.assertRaises(diagnostics.CommandFailure) as caught:
                diagnostics.execute(['fixture'], stage='database_import', timeout=17)
        self.assertEqual('COMMAND_TIMEOUT', str(caught.exception))
        self.assertEqual({'stage': 'database_import', 'code': 'COMMAND_TIMEOUT', 'timeout_seconds': 17}, caught.exception.failure)

    def test_target_database_transfer_preserves_sanitized_error_metadata(self):
        import io
        import diagnostics
        import publish
        sender=mock.Mock(stdout=io.BytesIO(b''),stderr=io.BytesIO(b''),returncode=0)
        receiver=subprocess.CompletedProcess([],1,b'',b"ERROR 1062 (23000) at line 8: Duplicate entry 'PRIVATE' for key 'x'")
        with mock.patch.object(publish.subprocess,'Popen',return_value=sender), mock.patch.object(publish.subprocess,'run',return_value=receiver):
            with self.assertRaises(diagnostics.CommandFailure) as caught:
                publish.pipe_sanitized_database('fixture-runner','fixture-helper')
        self.assertEqual('target_database_import',caught.exception.failure['stage'])
        self.assertEqual(1062,caught.exception.failure['database']['errno'])
        self.assertNotIn('PRIVATE',json.dumps(caught.exception.failure))

    def test_untrusted_stderr_and_exception_never_escape(self):
        import diagnostics
        with mock.patch.object(diagnostics.subprocess, 'run', return_value=subprocess.CompletedProcess([], 2, b'FICTION', b'PRIVATE')):
            with self.assertRaises(diagnostics.CommandFailure) as caught:
                diagnostics.execute(['fixture'], stage='native_verifier')
        self.assertNotIn('PRIVATE', json.dumps(caught.exception.failure))
        self.assertEqual('native_verifier', caught.exception.failure['stage'])


class SQLCompatibility(unittest.TestCase):
    def test_mysql8_collation_mapping_is_explicit_and_does_not_touch_literals(self):
        import sql_compat
        tokens = [('word','COLLATE'),('symbol','='),('word','utf8mb4_0900_ai_ci'),('string',"'utf8mb4_0900_ai_ci'")]
        converted, changes = sql_compat.compatible_tokens(tokens)
        self.assertEqual('utf8mb4_unicode_520_ci', converted[2][1])
        self.assertEqual(tokens[3], converted[3])
        self.assertEqual([{'from':'utf8mb4_0900_ai_ci','to':'utf8mb4_unicode_520_ci'}], changes)


    def test_closed_compatibility_accepts_settings_row_format_json_and_generated(self):
        import diagnosis
        from sql_stream import validate_file
        ddl = (b"/*!40101 SET SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;"
               b'CREATE TABLE `wp_options` (`option_name` varchar(100),`option_value` longtext) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC;'
               b'CREATE TABLE `wp_fiction_generated` (`id` bigint,`amount` int,`doubled` int GENERATED ALWAYS AS (`amount` + 1) STORED,`payload` JSON,KEY `pref` (`payload`(16))) ENGINE=InnoDB;')
        with tempfile.TemporaryDirectory() as tmp:
            src,dst=Path(tmp)/'src',Path(tmp)/'dst'; src.write_bytes(ddl)
            plan=validate_file(src,diagnosis.parser_module(),dst)
            self.assertIn(b'UTF8MB4_UNICODE_520_CI',dst.read_bytes())
            self.assertTrue(plan['compatibility'])
            self.assertEqual('NO_AUTO_VALUE_ON_ZERO',plan['source_sql_mode'])

    def test_chunk_ending_inside_large_literal_has_bounded_time(self):
        code = "import sys;sys.path.insert(0,"+repr(str(TOOLS))+");from sql_stream import Framer;f=Framer(lambda x:None);f.feed(b\"INSERT INTO `wp_posts` VALUES ('\"+b'F'*1048576)"
        subprocess.run([sys.executable,'-c',code],capture_output=True,check=True,timeout=3)

    def test_executable_object_is_explicitly_refused_not_executed(self):
        import diagnosis
        from sql_stream import validate_file
        from archive import Refusal
        with tempfile.TemporaryDirectory() as tmp:
            src,dst=Path(tmp)/'src',Path(tmp)/'dst'
            src.write_bytes(b'CREATE DEFINER=`fiction`@`localhost` VIEW `wp_view` AS SELECT 1;')
            with self.assertRaisesRegex(Refusal,'SQL_EXECUTABLE_OBJECT_REFUSED'):
                validate_file(src,diagnosis.parser_module(),dst)


class DatabaseOnly(unittest.TestCase):
    def test_locator_reads_headers_and_sql_never_file_payloads(self):
        import io
        import struct
        import database_only
        def entry(name, body):
            return struct.pack('255s14s12s4096s',name,str(len(body)).encode(),b'0',b'')+body
        data = entry(b'private.csv', b'PRIVATE_PAYLOAD')+entry(b'database.sql', b'SELECT FICTION;')+bytes(4377)
        class Traced(io.BytesIO):
            def read(self, n=-1):
                at = self.tell()
                self.assert_range(at, n)
                return super().read(n)
            def assert_range(self, at, n):
                if at < 4377+len(b'PRIVATE_PAYLOAD') and at+n > 4377:
                    raise AssertionError('non-database payload read')
        stream = Traced(data)
        where = database_only.locate_database(stream)
        self.assertEqual(len(b'SELECT FICTION;'), where['length'])
        self.assertEqual(b'SELECT FICTION;', b''.join(database_only.database_chunks(stream, where)))


if __name__ == '__main__': unittest.main(verbosity=2)
