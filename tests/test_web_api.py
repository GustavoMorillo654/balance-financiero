from pathlib import Path

from fastapi.testclient import TestClient

from src.web import app


client = TestClient(app)


BALANCED_CSV = b"""id_cuenta,descripcion_cuenta,tipo_saldo,monto,vida_util_anios
1,Caja y Bancos,liquidez,15000,
2,Terreno,inversion,50000,
3,Maquinaria,inversion,30000,10
4,Proveedores,pasivo_corriente,12000,
5,Prestamos Bancarios LP,pasivo_no_corriente,20000,
6,Capital Social,patrimonio,60000,
"""


class TestWebApi:

    def test_static_frontend_and_health_are_served(self):
        page = client.get("/")
        health = client.get("/api/health")

        assert page.status_code == 200
        assert 'id="analysis-form"' in page.text
        assert health.status_code == 200
        assert health.json() == {"status": "ok"}

    def test_analyze_csv_returns_complete_contract(self):
        response = client.post(
            "/api/analyze?period_days=360",
            files={"file": ("balance.csv", BALANCED_CSV, "text/csv")},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["isValid"] is True
        assert result["metrics_base"]["periodoDias"] == 360
        assert result["financial_ratios"]["liquidez"]["razonCorriente"]["valor"] == 1.25
        assert result["credit_evaluation"]["categoria"] == "Crédito excelente"

    def test_smoke_upload_for_included_datasets(self):
        root = Path(__file__).resolve().parent.parent
        for path in (root / "data" / "dataset_cuentas_ejemplo.csv", root / "datos.csv"):
            response = client.post(
                "/api/analyze",
                files={"file": (path.name, path.read_bytes(), "text/csv")},
            )

            assert response.status_code == 200
            assert "financial_ratios" in response.json()
            assert "credit_evaluation" in response.json()

    def test_datos_csv_uses_temporary_reconciliation_when_requested(self):
        root = Path(__file__).resolve().parent.parent
        response = client.post(
            "/api/analyze?balance_mode=conciliacion",
            files={"file": ("datos.csv", (root / "datos.csv").read_bytes(), "text/csv")},
        )

        assert response.status_code == 200
        result = response.json()
        assert result["isValid"] is True
        assert result["balance_adjustment"]["monto"] == 30000.0
        assert result["credit_evaluation"]["zScore"] == 1.8767

    def test_rejects_invalid_uploads(self):
        wrong_extension = client.post(
            "/api/analyze",
            files={"file": ("balance.txt", BALANCED_CSV, "text/plain")},
        )
        empty_file = client.post(
            "/api/analyze",
            files={"file": ("balance.csv", b"", "text/csv")},
        )

        assert wrong_extension.status_code == 400
        assert "extensión" in wrong_extension.json()["detail"]
        assert empty_file.status_code == 400
        assert "vacío" in empty_file.json()["detail"]
