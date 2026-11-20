"""Worker tests: synthetic byte streams only; no Docker/network/site access."""
import importlib.util
import io
import struct
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('offline_worker', HERE / 'worker.py')
worker = importlib.util.module_from_spec(spec) if spec else None
if spec and spec.loader:
    try:
        spec.loader.exec_module(worker)
        sys.modules['worker'] = worker
    except FileNotFoundError:
        worker = None


def archive(*entries):
    return io.BytesIO(b''.join(struct.pack('255s14s12s4096s', n.encode(), str(len(b)).encode(), b'0', p.encode()) + b
                             for n, p, b in entries) + bytes(4377))


class ArchiveTests(unittest.TestCase):
    def test_database_is_decoded_without_extracting_imported_code(self):
        self.assertIsNotNone(worker, 'missing worker implementation')
        sql, count = worker.read_archive(archive(('database.sql', '', b'CREATE TABLE `odd_options` (`id` int);'),
                                                ('wp-config.php', '', b'<?php die("TRAP");')))
        self.assertEqual(sql, b'CREATE TABLE `odd_options` (`id` int);')
        self.assertEqual(count, 2)

    def test_paths_duplicates_truncation_and_limits_are_refused(self):
        self.assertIsNotNone(worker)
        for stream in [archive(('database.sql', '..', b'bad')), archive(('database.sql', '/etc', b'bad')),
                       archive(('database.sql', '', b'a'), ('database.sql', '', b'b')),
                       io.BytesIO(b'zip'), archive(('x', '', b'a')),
                       archive(('..', '', b'a')), archive(('database.sql', 'a\\b', b'bad'))]:
            with self.subTest(), self.assertRaises(worker.Refusal):
                worker.read_archive(stream)
        with self.assertRaises(worker.Refusal):
            worker.read_archive(archive(('database.sql', '', b'12345')), max_bytes=4)


class SqlTests(unittest.TestCase):
    def test_nondefault_prefix_and_literal_insert(self):
        result = worker.sql_plan(b"CREATE TABLE `odd_options` (`option_id` bigint unsigned NOT NULL, `option_name` varchar(191), `option_value` longtext) ENGINE=InnoDB; INSERT INTO `odd_options` VALUES (1,'home','https://production.invalid');")
        self.assertEqual(result['prefix'], 'odd_')
        self.assertEqual(len(result['statements']), 2)

    def test_executable_sql_refused(self):
        for sql in [b"SELECT LOAD_FILE('/etc/passwd');", b"CREATE TABLE `odd_options` (`id` int) ENGINE=InnoDB DATA DIRECTORY='/tmp';",
                    b"INSERT INTO `odd_options` VALUES (SLEEP(9));", b"CREATE DATABASE stolen;", b"/*!50000 DROP TABLE `x` */;",
                    b"INSERT INTO `odd_options` VALUES ('unterminated);", b"USE mysql;", b"CREATE TABLE `odd_options` LIKE mysql.user;"]:
            with self.subTest(sql=sql), self.assertRaises(worker.Refusal):
                worker.sql_plan(sql)


class RequestTests(unittest.TestCase):
    def request(self):
        return dict(protocol='staging-offline-v1', stage='verifier', slug='synthetic', environment='staging',
                    production_url='https://production.invalid', production_hosts=['production.invalid', 'www.production.invalid'],
                    staging_url='http://staging.invalid:8099', wordpress_path='/var/www/html',
                    database=dict(host='localhost', socket='/run/mysqld/mysqld.sock', name='wordpress_staging', user='wp', password='synthetic'))

    def test_decisions_accept_only_actions_and_column_identifiers(self):
        from runtime import validate
        r = self.request()
        validate(dict(r, table_decisions={'wp_synthetic': {'action': 'anonymiser', 'columns': ['email']}}), 'verifier')
        for value in ([], {'wp_synthetic': {'action': 'keep'}},
                      {'wp_synthetic': {'action': 'garder', 'private_value': 'not-allowed'}},
                      {'wp_synthetic': {'action': 'anonymiser', 'columns': ['email; DROP TABLE x']}},
                      {'../site': {'action': 'garder'}}):
            with self.subTest(value=value), self.assertRaises(worker.Refusal):
                validate(dict(r, table_decisions=value), 'verifier')

    def test_native_contract_validation_rejects_unsafe_database_target_and_admin(self):
        self.assertIsNotNone(worker)
        from runtime import validate
        r = self.request()
        validate(r, 'verifier')
        for key, value in [('database', dict(r['database'], name='wordpress')), ('staging_url', 'http://192.0.2.8:8099'),
                           ('production_hosts', ['staging.invalid']), ('wordpress_path', '/another'),
                           ('admin', {'login': 'staging-admin', 'password': 'x' * 24})]:
            with self.subTest(key=key), self.assertRaises(worker.Refusal):
                validate(dict(r, **{key: value}), 'verifier')
        for password in ['short', 'x' * 73, 'x' * 24 + '\n']:
            with self.assertRaises(worker.Refusal):
                validate(dict(r, stage='anonymiser', admin={'login':'imagine-test-admin','password':password}), 'anonymiser')


if __name__ == '__main__':
    unittest.main()
