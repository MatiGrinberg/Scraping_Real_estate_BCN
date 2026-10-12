import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from scripts.property_details import OPTIONAL_COLUMNS, parse_used_details
from scripts import scrapers

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = '''<div class="details-property"><div class="details-property-feature-one">
<h2>Características básicas</h2><div class="details-property_features"><ul>
<li>90 m² construidos, 85 m² útiles</li><li>3 habitaciones</li><li>1 baño</li>
<li>Balcón</li><li>Segunda mano/buen estado</li><li>Orientación sur</li>
<li>Construido en 1966</li><li>No dispone de calefacción</li></ul></div>
<h2>Edificio</h2><div><ul><li>3ª planta exterior</li><li>Con ascensor</li></ul></div></div>
<div class="details-property-feature-two"><h2>Certificado energético</h2><div><ul>
<li><span>Consumo: </span><span class="icon-energy-c-e">80 kWh/m² año</span></li>
<li><span>Emisiones: </span><span class="icon-energy-c-g">35 kg CO2/m² año</span></li>
<div><span class="left-e" data-value-left-cee="80.0"></span>
<span class="right-g" data-value-right-cee="35.0"></span></div></ul></div></div></div>'''


def notebook_sources():
    return [''.join(c.get('source', [])) for c in json.loads((ROOT / 'nb/Analytics.ipynb').read_text())['cells']]


class OptionalDetailsTests(unittest.TestCase):
    def test_example(self):
        self.assertEqual(parse_used_details(SAMPLE), dict(zip(OPTIONAL_COLUMNS, [85, 'sur', 1966, 'E', 80, True])))

    def test_absent_and_emissions_only(self):
        for html in ['', '<li>90 m² construidos</li>', '<li>Emisiones: <span class="icon-energy-c-g">35 kg CO2/m² año</span></li>']:
            self.assertTrue(all(v is None for v in parse_used_details(html).values()))

    def test_decimal_and_heating(self):
        d = parse_used_details('<li>85,5 m² útiles</li><li>Calefacción individual: Gas natural</li><li>Consumo: 79,5 kWh/m² año</li>')
        self.assertEqual(d['Useful area (m²)'], 85.5)
        self.assertEqual(d['Energy consumption (kWh/m² year)'], 79.5)
        self.assertIs(d['No heating'], False)
        self.assertIsNone(parse_used_details('<li>Calefacción no indicada</li>')['No heating'])

    def test_consumption_ticket_fallback(self):
        d = parse_used_details('<span class="left-e" data-value-left-cee="80.0"></span>')
        self.assertEqual((d['Energy rating'], d['Energy consumption (kWh/m² year)']), ('E', 80))

    def test_failed_driver_keeps_row(self):
        with patch.object(scrapers, 'initialize_driver', side_effect=RuntimeError('test')), patch.object(scrapers.time, 'sleep'):
            records, count = scrapers.get_used_details_for_links(['example'], log_callback=lambda x: None)
        self.assertEqual(count, 1)
        self.assertEqual(records[0]['Location'], 'Unknown')
        self.assertTrue(all(records[0][c] is None for c in OPTIONAL_COLUMNS))

    def test_routing_only_buy_used(self):
        for op, kind in [('Buy', 'Used'), ('Rent', 'Used'), ('Buy', 'Chalet'), ('Buy', 'Reform'), ('Buy', 'Land'), ('Buy', 'New')]:
            with patch.object(scrapers, '_scrape_old_runner') as old, patch.object(scrapers, '_scrape_new_runner'):
                scrapers.run_scraper(op, kind, 100000, 240000, 75, 120, '', 'test', log_callback=lambda x: None)
                if old.called:
                    self.assertEqual(old.call_args.kwargs.get('collect_used_details', False), op == 'Buy' and kind == 'Used')

    def test_csv_fields_aligned_and_null_roundtrip(self):
        def listing(data, url):
            data.extend([{'Link': 'first', 'Price (€)': 200000, 'Area (m²)': 90, 'Hab': 3},
                         {'Link': 'second', 'Price (€)': 210000, 'Area (m²)': 95, 'Hab': 3}])
            return True
        records = [{'Location': 'A', **parse_used_details(SAMPLE)}, {'Location': 'B', **dict.fromkeys(OPTIONAL_COLUMNS)}]
        with tempfile.TemporaryDirectory() as tmp, patch.object(scrapers, '_get_search_metadata', return_value=(1, '2')), patch.object(scrapers, 'scrape_list_page_details', side_effect=listing), patch.object(scrapers, 'get_used_details_for_links', return_value=(records, 2)):
            path = Path(tmp) / 'out.csv'
            scrapers._scrape_old_runner('example', str(path), lambda x: None, collect_used_details=True)
            d = pd.read_csv(path)
            self.assertEqual(d.Link.tolist(), ['first', 'second'])
            self.assertEqual(d.loc[0, 'Useful area (m²)'], 85)
            self.assertTrue(d.loc[1, list(OPTIONAL_COLUMNS)].isna().all())


class NotebookFiltersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = {'pd': pd, 'np': np}
        exec(next(s for s in notebook_sources() if 'def filter_buy_rows' in s), cls.env)

    def data(self):
        return pd.DataFrame({'Link': ['a','b','c','d'], 'Location': ['X']*4,
            'Price (€)': [200000]*4, 'Area (m²)': [100]*4, 'Hab': [3]*4, 'Price/SqM': [2000]*4,
            'Useful area (m²)': [79,80,81,None], 'Construction year': [1979,1980,1981,None],
            'Energy consumption (kWh/m² year)': [79,80,81,None],
            'Energy rating': ['D','E','F',None], 'Orientation': ['sur','norte','sur, este',None],
            'No heating': [True,False,None,None]})

    def filtered(self, d=None, **kwargs):
        return self.env['filter_buy_rows'](self.data() if d is None else d, **kwargs).Link.tolist()

    def test_defaults_and_old_csv(self):
        self.assertEqual(self.filtered(), ['a','b','c','d'])
        old = self.data().drop(columns=list(OPTIONAL_COLUMNS))
        self.assertEqual(self.filtered(old, energy_consumption=('<',80), orientation=['sur'], no_heating=False), ['a','b','c','d'])

    def test_numeric_boundaries_and_missing(self):
        for field in ['energy_consumption', 'useful_area']:
            self.assertEqual(self.filtered(**{field: ('<',80)}), ['a','d'])
            self.assertEqual(self.filtered(**{field: ('<=',80)}), ['a','b','d'])
            self.assertEqual(self.filtered(**{field: ('>=',80)}), ['b','c','d'])
        self.assertEqual(self.filtered(construction_year=('>=',1980)), ['b','c','d'])

    def test_categorical_boolean_and_combination(self):
        self.assertEqual(self.filtered(orientation=['SUR']), ['a','d'])
        self.assertEqual(self.filtered(energy_rating=['d','E']), ['a','b','d'])
        self.assertEqual(self.filtered(no_heating=False), ['b','c','d'])
        self.assertEqual(self.filtered(no_heating=True), ['a','c','d'])
        self.assertEqual(self.filtered(energy_consumption=('<',80), no_heating=False), ['d'])

    def test_cleaning_keeps_optional_nulls(self):
        source = next(s for s in notebook_sources() if '#  CARGAR Y LIMPIAR DATOS' in s)
        for old_format in [False, True]:
            d = self.data()
            for column in OPTIONAL_COLUMNS:
                d[column] = None
            if old_format:
                d = d.drop(columns=list(OPTIONAL_COLUMNS))
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'test_buy_used.csv'
                d.to_csv(path, index=False)
                env = {'pd':pd,'np':np,'CSV_FILENAME':str(path),'base_name':'test_buy_used','display':lambda *a:None}
                with contextlib.redirect_stdout(io.StringIO()):
                    exec(source, env)
                self.assertEqual(len(env['df']), 4)
                self.assertTrue(env['df'][list(OPTIONAL_COLUMNS)].isna().all().all())


if __name__ == '__main__':
    unittest.main()
