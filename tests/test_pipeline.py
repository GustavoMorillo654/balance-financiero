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

    def test_datos_csv_pipeline(self):
        result = process_balance_file("datos.csv")

        # Verificar que el contrato es válido y serializable a JSON
        json_str = json.dumps(result)
        assert json_str is not None

        assert "isValid" in result
        assert "balance" in result
        assert "metrics_base" in result

        # Validar que Terreno en datos.csv no fue depreciado
        cuentas_no_corr = result["balance"]["activo"]["noCorriente"]["cuentas"]
        terreno = next(c for c in cuentas_no_corr if "Terreno" in c["nombre"])
        assert terreno["depreciable"] is False
        assert terreno["depreciacionAcumulada"] == 0.0
        assert terreno["valorNeto"] == 120000.0
