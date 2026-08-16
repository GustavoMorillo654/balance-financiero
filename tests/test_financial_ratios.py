from src.models.balance_sheet import MetricsBaseDTO
from src.services.financial_ratios import FinancialRatios


class TestFinancialRatios:

    def test_calculates_all_groups(self):
        metrics = MetricsBaseDTO(
            total_activo=100000.0,
            total_pasivo=40000.0,
            total_patrimonio=60000.0,
            activo_corriente=30000.0,
            pasivo_corriente=15000.0,
            inventario=10000.0,
            cuentas_por_cobrar=12000.0,
            ventas=120000.0,
            costos=60000.0,
            egresos=80000.0,
            utilidad_neta=40000.0,
            periodo_dias=365,
        )

        result = FinancialRatios.calculate(metrics)

        assert result.liquidez["razonCorriente"].valor == 2.0
        assert result.liquidez["pruebaAcida"].valor == 1.3333333333333333
        assert result.liquidez["capitalTrabajo"].valor == 15000.0
        assert result.apalancamiento["razonEndeudamiento"].valor == 0.4
        assert result.apalancamiento["pasivoPatrimonio"].valor == 0.6666666666666666
        assert result.apalancamiento["autonomiaFinanciera"].valor == 0.6
        assert result.apalancamiento["apalancamientoInterno"].valor == 1.5
        assert result.actividad["rotacionInventarios"].valor == 6.0
        assert result.actividad["rotacionActivos"].valor == 1.2
        assert result.actividad["rotacionCuentasPorCobrar"].valor == 10.0
        assert result.actividad["diasInventario"].valor == 365 / 6
        assert result.actividad["periodoCobro"].valor == 36.5
        assert result.rentabilidad["margenNeto"].valor == 1 / 3
        assert result.rentabilidad["roa"].valor == 0.4
        assert result.rentabilidad["roe"].valor == 2 / 3

        serialized = result.to_dict()
        assert serialized["liquidez"]["pruebaAcida"]["valor"] == 1.3333
        assert serialized["rentabilidad"]["margenNeto"]["valor"] == 0.3333

    def test_zero_denominators_are_unavailable_and_alerted(self):
        result = FinancialRatios.calculate(MetricsBaseDTO())

        assert result.liquidez["razonCorriente"].disponible is False
        assert result.liquidez["pruebaAcida"].valor is None
        assert result.apalancamiento["razonEndeudamiento"].valor is None
        assert result.actividad["rotacionInventarios"].valor is None
        assert result.rentabilidad["margenNeto"].valor is None
        assert result.alertas
        assert all("cero" in alert or "disponible" in alert for alert in result.alertas)

    def test_invalid_period_uses_default_and_reports_alert(self):
        metrics = MetricsBaseDTO(
            total_activo=100.0,
            activo_corriente=50.0,
            pasivo_corriente=25.0,
            periodo_dias=0,
        )

        result = FinancialRatios.calculate(metrics)

        assert result.periodo_dias == 365
        assert any("Período inválido" in alert for alert in result.alertas)
