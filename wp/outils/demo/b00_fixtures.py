"""Jeu de démonstration fixe, sans source ni image réelle."""
from datetime import date, timedelta
import struct
import zlib


def fixture_data():
    calendar = []
    for year in (2026, 2027, 2028):
        for quarter, month in enumerate((1, 4, 7, 10), 1):
            release = date(year, month, 15)
            calendar.append({'code': f'DEMO-{year}-T{quarter}', 'type': 'regulier',
                             'sortie': release.isoformat(), 'cloture': (release - timedelta(days=10)).isoformat()})
        release = date(year, 8, 15)
        calendar.append({'code': f'DEMO-{year}-HS', 'type': 'hors-serie',
                         'sortie': release.isoformat(), 'cloture': (release - timedelta(days=10)).isoformat()})
    calendar.sort(key=lambda row: row['sortie'])
    colors = ['#234E70', '#32664D', '#8B4232', '#594770', '#826321']
    issues = [{**row, 'slug': row['code'].lower(), 'label': ('HS' if row['type'] == 'hors-serie' else row['code'][-1]),
               'color': colors[i]} for i, row in enumerate(calendar[:5])]
    return {'calendar': calendar, 'issues': issues,
            'themes': ['Terres imaginaires', 'Solidarités inventées', 'Futurs fictifs'],
            'events': ['Rencontre au village Imaginaire', 'Atelier des possibles inventés'],
            'partners': ['Association des Nuages fictifs', 'Coopérative des Horizons inventés']}


def cover_png(label, color):
    """Aplat PNG RGB 480 × 640 et numéro bitmap, aucun média tiers."""
    glyphs = {
        '1': ['00100','01100','00100','00100','00100','00100','01110'],
        '2': ['01110','10001','00001','00010','00100','01000','11111'],
        '3': ['11110','00001','00001','01110','00001','00001','11110'],
        '4': ['00010','00110','01010','10010','11111','00010','00010'],
        'H': ['10001','10001','10001','11111','10001','10001','10001'],
        'S': ['01111','10000','10000','01110','00001','00001','11110'],
    }
    width, height, scale = 480, 640, 24
    background = bytes.fromhex(color.lstrip('#'))
    pixels = bytearray(background * width * height)
    left = (width - (len(label) * 6 - 1) * scale) // 2
    top = (height - 7 * scale) // 2
    for i, char in enumerate(label):
        for row, bits in enumerate(glyphs[char]):
            for col, bit in enumerate(bits):
                if bit == '1':
                    for y in range(top + row * scale, top + (row + 1) * scale):
                        start = (y * width + left + (i * 6 + col) * scale) * 3
                        pixels[start:start + scale * 3] = b'\xff\xff\xff' * scale
    raw = b''.join(b'\x00' + pixels[y * width * 3:(y + 1) * width * 3] for y in range(height))
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b'')


def dummy_pdf(label):
    text = f'BT /F1 20 Tf 60 760 Td (IMAGINE - DEMONSTRATION FICTIVE) Tj 0 -50 Td (Numero {label} - PDF factice sans contenu reel.) Tj ET'.encode('ascii')
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
               b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
               b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
               b'<< /Length ' + str(len(text)).encode() + b' >>\nstream\n' + text + b'\nendstream']
    pdf = b'%PDF-1.4\n'
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf += str(i).encode() + b' 0 obj\n' + obj + b'\nendobj\n'
    xref = len(pdf)
    pdf += b'xref\n0 6\n0000000000 65535 f \n' + b''.join(f'{off:010d} 00000 n \n'.encode() for off in offsets[1:])
    return pdf + f'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()
