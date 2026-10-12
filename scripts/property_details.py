"""Optional features from the details-property block of a resale listing."""
from html.parser import HTMLParser
import re

OPTIONAL_COLUMNS = (
    'Useful area (m²)', 'Orientation', 'Construction year',
    'Energy rating', 'Energy consumption (kWh/m² year)', 'No heating',
)


class _DetailsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []
        self.current = None
        self.consumption_ticket = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'li':
            self.current = {'text': [], 'classes': []}
        if self.current is not None:
            self.current['classes'].extend(attrs.get('class', '').split())
        if 'data-value-left-cee' in attrs:
            self.consumption_ticket = attrs

    def handle_data(self, data):
        if self.current is not None:
            self.current['text'].append(data)

    def handle_endtag(self, tag):
        if tag == 'li' and self.current is not None:
            self.items.append(self.current)
            self.current = None


def _number(text):
    text = text.strip().replace(' ', '')
    if ',' in text:
        text = text.replace('.', '').replace(',', '.')
    elif re.fullmatch(r'\d{1,3}(?:\.\d{3})+', text):
        text = text.replace('.', '')
    try:
        return float(text)
    except (ValueError, TypeError):
        return None


def parse_used_details(html):
    """Return blank (None) for absent or unrecognized optional values."""
    result = dict.fromkeys(OPTIONAL_COLUMNS)
    parser = _DetailsParser()
    parser.feed(html or '')
    for item in parser.items:
        text = re.sub(r'\s+', ' ', ' '.join(item['text'])).strip()
        match = re.search(r'([\d.,]+)\s*m[²2]\s*útiles', text, re.I)
        if match:
            result['Useful area (m²)'] = _number(match.group(1))
        match = re.search(r'^Orientación\s+(.+)', text, re.I)
        if match:
            result['Orientation'] = match.group(1).strip().lower()
        match = re.search(r'\bConstruido en\s+(\d{4})\b', text, re.I)
        if match:
            result['Construction year'] = int(match.group(1))
        if re.search(r'\bNo dispone de calefacción\b', text, re.I):
            result['No heating'] = True
        elif (re.match(r'^(?:Calefacción\s+(?:individual|central)|Dispone de calefacción|Con calefacción)\b', text, re.I)
              and result['No heating'] is None):
            result['No heating'] = False
        if re.match(r'^Consumo\s*:', text, re.I):
            match = re.search(r'Consumo\s*:\s*([\d.,]+)\s*kWh', text, re.I)
            if match:
                result['Energy consumption (kWh/m² year)'] = _number(match.group(1))
            for css_class in item['classes']:
                match = re.fullmatch(r'icon-energy-c-([a-g])', css_class, re.I)
                if match:
                    result['Energy rating'] = match.group(1).upper()
    # Consumption uses the LEFT ticket. The right ticket is emissions.
    ticket = parser.consumption_ticket
    if result['Energy consumption (kWh/m² year)'] is None and ticket:
        try:
            result['Energy consumption (kWh/m² year)'] = float(ticket['data-value-left-cee'])
        except (ValueError, TypeError):
            pass
    if result['Energy rating'] is None:
        for css_class in ticket.get('class', '').split():
            match = re.fullmatch(r'left-([a-g])', css_class, re.I)
            if match:
                result['Energy rating'] = match.group(1).upper()
    return result
