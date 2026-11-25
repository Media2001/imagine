"""A01/3: closed table policy and literal fidelity, synthetic inputs only."""
import io
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/staging-court'))
import diagnosis
from archive import Findings
from sql_diagnostic import SQLAnalysis
from sql_stream import validate_file


def base():
    return (b'CREATE TABLE `wp_options` (`option_name` varchar(100),`option_value` text) ENGINE=InnoDB;'
            b"INSERT INTO `wp_options` VALUES ('home','fiction'),('siteurl','fiction');" +
            b''.join(('CREATE TABLE `wp_' + t + '` (`id` bigint) ENGINE=InnoDB;').encode()
                     for t in ('users','usermeta','posts','postmeta','comments')))


class ArchiveReelle3(unittest.TestCase):
    def analyze(self, sql, decisions=None):
        findings = Findings(); a = SQLAnalysis(findings, decisions or {})
        for p in range(0, len(sql), 13): a.feed(sql[p:p+13])
        a.finish()
        return findings.report(), a

    def test_unknown_email_and_dated_families_default_structure_only(self):
        sql = base()
        for t in ('fiction_email', 'matomo_archive_blob_2024_01', 'matomo_archive_blob_2024_07'):
            sql += ('CREATE TABLE `wp_' + t + '` (`email` text,`payload` blob) ENGINE=InnoDB;').encode()
            sql += ('INSERT INTO `wp_' + t + '` VALUES ').encode() + b"('FICTION_PRIVATE@example.org',_binary'\xff\\\' ; NEVER_VALUE');"
        report, a = self.analyze(sql)
        self.assertEqual([], report['blockers'])
        self.assertNotIn('TABLE_INCONNUE_CONSERVEE', [r['code'] for r in report['rules']])
        self.assertEqual(3, sum(r['count'] for r in a.table_summary if r['action'] == 'videe'))
        self.assertEqual(['wp_fiction_email'], a.unclassified)
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp)/'src', Path(tmp)/'dst'; src.write_bytes(sql)
            plan = validate_file(src, diagnosis.parser_module(), dst)
            self.assertNotIn(b'FICTION_PRIVATE', dst.read_bytes())
            self.assertEqual('vider', plan['table_decisions']['wp_fiction_email']['action'])

    def test_override_keep_blob_hex_and_escapes(self):
        sql = base() + b'CREATE TABLE `wp_fiction_blob` (`id` bigint,`payload` blob) ENGINE=InnoDB;'
        sql += b"INSERT INTO `wp_fiction_blob` VALUES (1,_binary'\x00\xff\\0\\n\\r\\Z\\\\\\\'\";'),(2,0x00ff27),(3,X'00FF27');"
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp)/'src', Path(tmp)/'dst'; src.write_bytes(sql)
            plan = validate_file(src, diagnosis.parser_module(), dst, decisions={'wp_fiction_blob':{'action':'garder'}})
            self.assertIn(b'INSERT INTO `wp_fiction_blob`', dst.read_bytes())
            self.assertEqual('garder', plan['table_decisions']['wp_fiction_blob']['action'])

    def test_explicit_keep_personal_still_requires_resolution(self):
        sql = base() + b'CREATE TABLE `wp_fiction_email` (`email` text) ENGINE=InnoDB;'
        report, _ = self.analyze(sql, {'wp_fiction_email':{'action':'garder'}})
        self.assertIn('TABLE_PERSONNELLE_A_TRANCHER', report['blockers'])
        report, _ = self.analyze(sql, {'wp_fiction_email':{'action':'anonymiser','columns':['email']}})
        self.assertEqual([], report['blockers'])

    def test_discarded_huge_literal_has_bounded_framer(self):
        from sql_stream import Framer, Validator
        v = Validator(diagnosis.parser_module())
        f = Framer(v.statement, limit=1024)
        f.feed(base() + b'CREATE TABLE `wp_matomo_archive_blob_2024_01` (`payload` blob) ENGINE=InnoDB;')
        f.feed(b"INSERT INTO `wp_matomo_archive_blob_2024_01` VALUES (_binary'")
        for _ in range(400): f.feed(b'\xff' * 8192)
        f.feed(b"');"); f.finish(); v.finish()
        self.assertLess(f.peak, 20000)
        self.assertEqual(1, v.skipped_inserts)

    def test_two_uploads_excluded(self):
        import archive
        for folder in ('memberships_profile_fields','download-manager-files'):
            self.assertTrue(archive.excluded('uploads/'+folder+'/index.php'))

    def test_negative_numbers_in_discarded_rows_and_chunk_boundaries(self):
        from sql_stream import Framer, Validator
        source = base() + b'CREATE TABLE `wp_fiction_drop` (`id` bigint,`payload` blob) ENGINE=InnoDB;'
        source += b"INSERT INTO `wp_fiction_drop` VALUES (-1,_binary'\xff;\\\'a\\\\''b');"
        for cut in range(len(source)):
            v = Validator(diagnosis.parser_module())
            f = Framer(v.statement)
            f.feed(source[:cut]); f.feed(source[cut:]); f.finish(); v.finish()
            self.assertEqual(1, v.skipped_inserts)

    def test_bad_decisions_and_invalid_encoding_stay_closed(self):
        sql = base() + b'CREATE TABLE `wp_fiction_drop` (`email` text) ENGINE=InnoDB;'
        for invalid in (None, 'garder', {'action':'anything'}, {'action':'anonymiser','columns':['missing']}):
            report, _ = self.analyze(sql, {'wp_fiction_drop':invalid})
            self.assertIn('DECISION_INVALIDE', report['blockers'])
        report, _ = self.analyze(base()+b'CREATE TABLE `wp_fiction` (`id` bigint DEFAULT \xff) ENGINE=InnoDB;')
        self.assertTrue(report['blockers'])

    def test_summary_families_and_space(self):
        report={'status':'NO_STATIC_BLOCKER','rules':[], 'table_families':[{'family':'matomo_*','count':185,'action':'videe'}],
                'unclassified_tables':['wp_fiction'], 'disk_space':{'required_bytes':1234,'available_bytes':5678}}
        text=diagnosis.format_summary(report)
        for s in ('matomo_*','185','videe','1234','5678','wp_fiction'): self.assertIn(s,text)


if __name__ == '__main__': unittest.main(verbosity=2)
