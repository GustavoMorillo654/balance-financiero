import pytest
from src.models.account import Account, AccountCategory
from src.services.depreciation import DepreciationEngine


class TestDepreciationEngine:

    def test_straight_line_formula(self):
        # 100,000 / 10 años = 10,000 anual -> valor neto 90,000
        dep_acum, v_neto = DepreciationEngine.calculate_straight_line(
            costo_historico=100000.0,
            vida_util_anios=10.0,
            valor_residual=0.0,
            periodos_transcurridos=1.0
        )
        assert dep_acum == 10000.0
        assert v_neto == 90000.0

    def test_straight_line_with_residual_value(self):
        # (100,000 - 10,000) / 10 = 9,000 anual -> valor neto 91,000
        dep_acum, v_neto = DepreciationEngine.calculate_straight_line(
            costo_historico=100000.0,
            vida_util_anios=10.0,
            valor_residual=10000.0,
            periodos_transcurridos=1.0
        )
        assert dep_acum == 9000.0
        assert v_neto == 91000.0

    def test_terreno_never_depreciates(self):
        """
        REGLA DE NEGOCIO ESTRICTA:
        Terreno es el único activo fijo que NO se deprecia.
        Su depreciación acumulada debe ser 0 y su valor neto igual a su saldo.
        """
        terreno = Account(
            id_cuenta="108",
            nombre="Terreno (Sede Principal)",
            categoria=AccountCategory.ACTIVO_NO_CORRIENTE,
            saldo=120000.0,
            vida_util_anios=20.0,  # Incluso si por error viene vida util
            depreciable=True,
            depreciacion_acumulada=0.0,
            valor_neto=120000.0
        )
        
        accounts, total_dep = DepreciationEngine.apply_depreciation([terreno])
        
        assert accounts[0].depreciable is False
        assert accounts[0].depreciacion_acumulada == 0.0
        assert accounts[0].valor_neto == 120000.0
        assert total_dep == 0.0

    def test_fixed_assets_depreciation(self):
        maquinaria = Account(
            id_cuenta="102",
            nombre="Maquinaria y Equipos",
            categoria=AccountCategory.ACTIVO_NO_CORRIENTE,
            saldo=80000.0,
            vida_util_anios=10.0
        )
        vehiculo = Account(
            id_cuenta="103",
            nombre="Vehiculo de Reparto",
            categoria=AccountCategory.ACTIVO_NO_CORRIENTE,
            saldo=20000.0,
            vida_util_anios=5.0
        )
        
        accounts, total_dep = DepreciationEngine.apply_depreciation([maquinaria, vehiculo])
        
        # Maquinaria: 80,000 / 10 = 8,000 dep, neto 72,000
        assert accounts[0].depreciable is True
        assert accounts[0].depreciacion_acumulada == 8000.0
        assert accounts[0].valor_neto == 72000.0

        # Vehiculo: 20,000 / 5 = 4,000 dep, neto 16,000
        assert accounts[1].depreciable is True
        assert accounts[1].depreciacion_acumulada == 4000.0
        assert accounts[1].valor_neto == 16000.0

        assert total_dep == 12000.0
