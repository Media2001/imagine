"""Coverage guard for C-06 + closed lots (explicit owned config during parallel work)."""
import json
import pathlib
import sys
import xml.etree.ElementTree as ET


def check(path):
    root = ET.parse(path).getroot()
    suites = {suite.attrib['name']: suite for suite in root.find('testsuite').findall('testsuite')}
    expected = {'Acces', 'Numeros', 'Robots', 'Entreprise'}
    assert set(suites) == expected, f'Standard suite coverage: expected {expected}, got {set(suites)}'
    assert int(suites['Acces'].attrib['tests']) >= 50, 'Access suite was truncated'
    for suite in suites.values():
        for key in ('errors', 'failures', 'skipped'):
            assert int(suite.attrib[key]) == 0, (suite.attrib['name'], key)
    receipt = json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
    bounded = receipt['command'] == ('composer test -- --configuration tests/Acces/phpunit.xml '
                                      '--log-junit /tmp/result.xml')
    assert bounded or receipt['command'] == 'composer test -- --log-junit /tmp/result.xml'
    assert receipt['exit_code'] == 0
    log = path.with_suffix('.log').read_text(encoding='utf-8')
    configuration = '/work/tests/Acces/phpunit.xml' if bounded else '/work/phpunit.xml'
    assert 'Configuration: ' + configuration in log
    print(json.dumps({'composer_test': True, 'root_configuration': not bounded,
                      'bounded_closed_lots': bounded,
                      'suites': {name: {key: int(suite.attrib[key]) for key in ('tests', 'assertions')}
                                 for name, suite in suites.items()}}, indent=2))


if __name__ == '__main__':
    check(pathlib.Path(sys.argv[1]))
