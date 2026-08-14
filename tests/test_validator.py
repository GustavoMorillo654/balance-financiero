import pytest
from src.models.account import Account, AccountCategory
from src.services.validator import AccountingValidator


class TestAccountingValidator:

    def test_balanced_sheet(self):
        accounts = [
            Account(id_cuenta="1", nombre="Caja", categoria=AccountCategory.ACTIVO_CORRIENTE, saldo=15000.0),
            Account(id_cuenta="2", nombre="Terreno", categoria=AccountCategory.ACTIVO_NO_CORRIENTE, saldo=50000.0, depreciable=False, valor_neto=50000.0),
            Account(id_cuenta="3", nombre="Maquinaria", categoria=AccountCategory.ACTIVO_NO_CORRIENTE, saldo=30000.0, depreciable=True, depreciacion_acumulada=3000.0, valor_neto=27000.0),
            Account(id_cuenta="4", nombre="Proveedores", categoria=AccountCategory.PASIVO_CORRIENTE, saldo=12000.0),
            Account(id_cuenta="5", nombre="Prestamos LP", categoria=AccountCategory.PASIVO_NO_CORRIENTE, saldo=20000.0),
            Account(id_cuenta="6", nombre="Capital Social", categoria=AccountCategory.PATRIMONIO, saldo=60000.0),
        ]
        
        # Activo: 15,000 + 50,000 + 27,000 = 92,000
        # Pasivo: 12,000 + 20,000 = 32,000
        # Patrimonio: 60,000
        # Total Pasivo + Patrimonio = 92,000
        res = AccountingValidator.build_and_validate(accounts)
        
        assert res.is_valid is True
        assert len(res.alerts) == 0
        assert res.metrics_base.total_activo == 92000.0
        assert res.metrics_base.total_pasivo == 32000.0
        assert res.metrics_base.total_patrimonio == 60000.0
        assert res.metrics_base.activo_corriente == 15000.0
        assert res.metrics_base.pasivo_corriente == 12000.0

    def test_unbalanced_sheet_generates_alert(self):
        accounts = [
            Account(id_cuenta="1", nombre="Caja", categoria=AccountCategory.ACTIVO_CORRIENTE, saldo=20000.0),
            Account(id_cuenta="2", nombre="Proveedores", categoria=AccountCategory.PASIVO_CORRIENTE, saldo=10000.0),
            Account(id_cuenta="3", nombre="Capital Social", categoria=AccountCategory.PATRIMONIO, saldo=5000.0),
        ]
        # Activo = 20,000 vs Pasivo + Patrimonio = 15,000 (Diferencia = 5,000)
        res = AccountingValidator.build_and_validate(accounts)

        assert res.is_valid is False
        assert len(res.alerts) == 1
        assert "5000" in res.alerts[0] or "5,000" in res.alerts[0]
        assert "Descuadre contable detectado" in res.alerts[0]

    def test_with_income_and_expense_results(self):
        accounts = [
            Account(id_cuenta="1", nombre="Caja", categoria=AccountCategory.ACTIVO_CORRIENTE, saldo=30000.0),
            Account(id_cuenta="2", nombre="Proveedores", categoria=AccountCategory.PASIVO_CORRIENTE, saldo=10000.0),
            Account(id_cuenta="3", nombre="Capital Social", categoria=AccountCategory.PATRIMONIO, saldo=10000.0),
            Account(id_cuenta="4", nombre="Ventas", categoria=AccountCategory.INGRESO, saldo=25000.0),
            Account(id_cuenta="5", nombre="Costos", categoria=AccountCategory.EGRESO, saldo=15000.0),
        ]
        # Utilidad Neta = 25,000 - 15,000 = 10,000
        # Patrimonio = 10,000 (Capital) + 10,000 (Utilidad) = 20,000
        # Total Pasivo + Patrimonio = 10,000 + 20,000 = 30,000 == Total Activo (30,000)
        res = AccountingValidator.build_and_validate(accounts)
        
        assert res.is_valid is True
        assert res.metrics_base.total_patrimonio == 20000.0
        assert res.metrics_base.total_activo == 30000.0
