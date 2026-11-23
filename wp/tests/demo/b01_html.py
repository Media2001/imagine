"""Validation structurelle HTML5 locale ; pas une certification WCAG/W3C."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
for wheel in sorted((ROOT / 'production/B-01/validation').glob('*.whl')):
    sys.path.insert(0, str(wheel))
import html5lib
from bs4 import BeautifulSoup


def validate_html(text):
    parser = html5lib.HTMLParser(namespaceHTMLElements=False)
    parser.parse(text)
    errors = ['HTML5 ' + str(position) + ' ' + code + ' ' + str(data) for position, code, data in parser.errors]
    soup = BeautifulSoup(text, 'html.parser')
    def need(ok, label):
        if not ok:
            errors.append(label)
    for tag in ['html', 'head', 'body', 'title', 'main', 'h1']:
        need(len(soup.find_all(tag)) == 1, 'un seul ' + tag)
    need(bool(soup.html and soup.html.get('lang')), 'langue de page')
    need(bool(soup.find('header') and soup.find('nav') and soup.find('footer')), 'repères header/nav/footer')
    need(bool(soup.select('a[href="#imagine-main"]') and soup.select('main#imagine-main')), 'lien évitement et cible main')
    ids = [e.get('id') for e in soup.select('[id]')]
    need(len(ids) == len(set(ids)), 'identifiants uniques')
    for e in soup.select('[aria-labelledby]'):
        need(all(x in ids for x in e['aria-labelledby'].split()), 'aria-labelledby résolu')
    for image in soup.find_all('img'):
        need(image.has_attr('alt') and bool(image['alt'].strip()), 'image éditoriale avec texte alternatif')
    previous = 0
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        level = int(heading.name[1])
        need(level <= previous + 1, 'hiérarchie des titres : ' + heading.get_text(' ', strip=True))
        previous = level
    for link in soup.find_all('a'):
        need(bool(link.get('href')) and bool(link.get_text(' ', strip=True) or link.get('aria-label') or link.find('img')), 'lien nommé et adresse non vide')
    for element in soup.find_all(['input', 'textarea', 'select']):
        if element.get('type') in ['hidden', 'submit', 'button']:
            continue
        need(bool(element.get('aria-label') or soup.find('label', attrs={'for': element.get('id')}) or element.find_parent('label')), 'champ avec étiquette')
    need('squelette, sans habillage' in text, 'mention squelette sur chaque page')
    return errors
