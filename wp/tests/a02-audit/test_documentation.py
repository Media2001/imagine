"""Offline documentary acceptance; no source fetching or site access."""
import json
import pathlib
import unittest

REPO = pathlib.Path(__file__).resolve().parents[3]


class DocumentationEvidence(unittest.TestCase):
    def test_each_standard_claim_has_exact_verified_phrase(self):
        rows = json.loads((REPO / 'production/A-02/sources-officielles.json').read_text(encoding='utf8'))
        self.assertGreaterEqual(len(rows), 5)
        for row in rows:
            with self.subTest(url=row['url']):
                self.assertTrue(row.get('evidence'), 'EXACT_PHRASE_MISSING')
                self.assertEqual(row['status'], 200)
                for item in row['evidence']:
                    self.assertTrue(item['claim'])
                    self.assertTrue(item['exact_phrase'])
                    self.assertTrue(item['verified_in_source'])
                    self.assertGreaterEqual(item['normalized_text_offset'], 0)


if __name__ == '__main__':
    unittest.main()
