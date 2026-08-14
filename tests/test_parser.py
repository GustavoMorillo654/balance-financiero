import pytest
from src.services.csv_parser import CSVParser


class TestCSVParser:

    def test_sanitize_amount_standard(self):
        assert CSVParser.sanitize_amount("15000") == 15000.0
        assert CSVParser.sanitize_amount("15000.50") == 15000.50
        assert CSVParser.sanitize_amount(25000) == 25000.0

    def test_sanitize_amount_currencies_and_separators(self):
        assert CSVParser.sanitize_amount("$ 1,500.50") == 1500.50
        assert CSVParser.sanitize_amount("€ 1.500,50") == 1500.50
        assert CSVParser.sanitize_amount("Bs. 50,000.00") == 50000.00
        assert CSVParser.sanitize_amount("BsF 120.000,00") == 120000.00

    def test_sanitize_amount_negatives_and_empty(self):
        assert CSVParser.sanitize_amount("(1,200.00)") == -1200.00
        assert CSVParser.sanitize_amount("-500.50") == -500.50
        assert CSVParser.sanitize_amount("") == 0.0
        assert CSVParser.sanitize_amount(None) == 0.0
        assert CSVParser.sanitize_amount("  ") == 0.0

    def test_sanitize_useful_life(self):
        assert CSVParser.sanitize_useful_life("10") == 10.0
        assert CSVParser.sanitize_useful_life("20.5") == 20.5
        assert CSVParser.sanitize_useful_life("") is None
        assert CSVParser.sanitize_useful_life(None) is None
        assert CSVParser.sanitize_useful_life("0") is None
        assert CSVParser.sanitize_useful_life("-5") is None

    def test_detect_delimiter(self):
        csv_comma = "id,nombre,monto\n1,Caja,100"
        csv_semicolon = "id;nombre;monto\n1;Caja;100"
        csv_tab = "id\tnombre\tmonto\n1\tCaja\t100"
        csv_pipe = "id|nombre|monto\n1|Caja|100"

        assert CSVParser.detect_delimiter(csv_comma) == ","
        assert CSVParser.detect_delimiter(csv_semicolon) == ";"
        assert CSVParser.detect_delimiter(csv_tab) == "\t"
        assert CSVParser.detect_delimiter(csv_pipe) == "|"

    def test_parse_content_tolerant(self):
        content = """id;descripcion;tipo;saldo;vida_util
1;Efectivo en Caja;Liquidez;$ 10,000.00;
2;Maquinaria;Inversion;50.000,00 €;10
"""
        records = CSVParser.parse_content(content)
        assert len(records) == 2
        assert records[0]["nombre"] == "Efectivo en Caja"
        assert records[0]["monto"] == 10000.0
        assert records[0]["vida_util_anios"] is None

        assert records[1]["nombre"] == "Maquinaria"
        assert records[1]["monto"] == 50000.0
        assert records[1]["vida_util_anios"] == 10.0
