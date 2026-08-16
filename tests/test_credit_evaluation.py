from src.models.balance_sheet import MetricsBaseDTO
from src.services.credit_evaluation import CreditEvaluation
from src.services.financial_ratios import FinancialRatios


def build_ratios(activo_corriente, pasivo_corriente, patrimonio, pasivo):
    return FinancialRatios.calculate(
        MetricsBaseDTO(
            total_activo=patrimonio + pasivo,
            total_pasivo=pasivo,
            total_patrimonio=patrimonio,
            activo_corriente=activo_corriente,
            pasivo_corriente=pasivo_corriente,
        )
    )


class TestCreditEvaluation:

    def test_excellent_credit(self):
        # X1 = 2.0, X2 = 1.5, Z = 1.7
        result = CreditEvaluation.calculate(build_ratios(20, 10, 60, 40))

        assert result.disponible is True
        assert result.x1 == 2.0
        assert result.x2 == 1.5
        assert result.z_score == 1.7
        assert result.categoria == "Crédito excelente"

    def test_normal_credit_at_both_boundaries(self):
        # X1 = 2.0, X2 = 1.0, Z = 1.4 exactly
        upper_boundary = CreditEvaluation.calculate(build_ratios(20, 10, 10, 10))
        assert upper_boundary.z_score == 1.4
        assert upper_boundary.categoria == "Crédito de riesgo normal"

        # X1 = 0.0, X2 = 1.1, Z = 0.66 exactly
        lower_boundary = CreditEvaluation.calculate(build_ratios(0, 10, 11, 10))
        assert lower_boundary.z_score == 0.66
        assert lower_boundary.categoria == "Crédito de riesgo normal"

    def test_bad_credit_below_lower_boundary(self):
        # X1 = 1.0, X2 = 0.0, Z = 0.4
        result = CreditEvaluation.calculate(build_ratios(10, 10, 0, 10))

        assert result.z_score == 0.4
        assert result.categoria == "Crédito malo"

    def test_unavailable_when_required_index_has_zero_denominator(self):
        result = CreditEvaluation.calculate(build_ratios(10, 10, 10, 0))

        assert result.disponible is False
        assert result.z_score is None
        assert result.categoria == "No evaluable"
        assert "X2" in result.alertas[0]

    def test_unavailable_for_unbalanced_balance(self):
        result = CreditEvaluation.calculate(build_ratios(20, 10, 60, 40), balance_is_valid=False)

        assert result.disponible is False
        assert result.z_score is None
        assert "descuadre" in result.alertas[0]
