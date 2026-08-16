import json
import pytest
from src.index import process_balance_content, process_balance_file


class TestPipeline:

    def test_example_dataset_pipeline(self):
        result = process_balance_file("data/dataset_cuentas_ejemplo.csv")

        # Comprobar claves principales del contrato JSON
        assert "isValid" in result
        assert "alerts" in result
        assert "balance" in result
        assert "metrics_base" in result
        assert "financial_ratios" in result

        # Dataset de ejemplo debe cuadrar perfectamente
        assert result["isValid"] is True
        assert len(result["alerts"]) == 0

        # Validar estructura de balance
        bal = result["balance"]
        assert "activo" in bal
        assert "pasivo" in bal
        assert "patrimonio" in bal

        assert "corriente" in bal["activo"]
        assert "noCorriente" in bal["activo"]
        assert "totalActivo" in bal["activo"]

        # Validar activos no corrientes y regla del terreno
        cuentas_no_corr = bal["activo"]["noCorriente"]["cuentas"]
        terreno_cuenta = next(c for c in cuentas_no_corr if "Terreno" in c["nombre"])
        assert terreno_cuenta["depreciable"] is False
        assert terreno_cuenta["depreciacionAcumulada"] == 0.0
        assert terreno_cuenta["valorNeto"] == terreno_cuenta["saldo"]

        # Validar que maquinaria sí se depreció
        maquinaria_cuenta = next(c for c in cuentas_no_corr if "Maquinaria" in c["nombre"])
        assert maquinaria_cuenta["depreciable"] is True
        assert maquinaria_cuenta["depreciacionAcumulada"] == 3000.0
        assert maquinaria_cuenta["valorNeto"] == 27000.0

        # Validar métricas base
        mb = result["metrics_base"]
        assert mb["totalActivo"] == mb["totalPasivo"] + mb["totalPatrimonio"]
        assert mb["totalActivo"] == 92000.0
        assert mb["inventario"] == 0.0
        assert result["financial_ratios"]["liquidez"]["razonCorriente"]["valor"] == 1.25
        assert result["financial_ratios"]["apalancamiento"]["razonEndeudamiento"]["valor"] == round(32000 / 92000, 4)
        assert result["credit_evaluation"]["disponible"] is True
        assert result["credit_evaluation"]["x1"] == 1.25
        assert result["credit_evaluation"]["x2"] == 1.875
        assert result["credit_evaluation"]["zScore"] == 1.625
        assert result["credit_evaluation"]["categoria"] == "Crédito excelente"

    def test_datos_csv_pipeline(self):
        result = process_balance_file("datos.csv")

        # Verificar que el contrato es válido y serializable a JSON
        json_str = json.dumps(result)
        assert json_str is not None

        assert "isValid" in result
        assert "balance" in result
        assert "metrics_base" in result
        assert "financial_ratios" in result

        # Validar que Terreno en datos.csv no fue depreciado
        cuentas_no_corr = result["balance"]["activo"]["noCorriente"]["cuentas"]
        terreno = next(c for c in cuentas_no_corr if "Terreno" in c["nombre"])
        assert terreno["depreciable"] is False
        assert terreno["depreciacionAcumulada"] == 0.0
        assert terreno["valorNeto"] == 120000.0

    def test_new_csv_content_recalculates_dashboard(self):
        first_csv = """id,nombre,tipo,monto
1,Caja,liquidez,1000
2,Proveedores,pasivo_corriente,500
3,Capital Social,patrimonio,500
"""
        second_csv = """id,nombre,tipo,monto
1,Caja,liquidez,2000
2,Proveedores,pasivo_corriente,500
3,Capital Social,patrimonio,1500
"""

        first = process_balance_content(first_csv)
        second = process_balance_content(second_csv)

        assert first["financial_ratios"]["liquidez"]["razonCorriente"]["valor"] == 2.0
        assert second["financial_ratios"]["liquidez"]["razonCorriente"]["valor"] == 4.0

    def test_unbalanced_pipeline_does_not_issue_credit_verdict(self):
        csv = """id,nombre,tipo,monto
1,Caja,liquidez,20000
2,Proveedores,pasivo_corriente,10000
3,Capital Social,patrimonio,5000
"""

        result = process_balance_content(csv)

        assert result["isValid"] is False
        assert result["credit_evaluation"]["disponible"] is False
        assert result["credit_evaluation"]["categoria"] == "No evaluable"
