import pytest
from src.models.account import AccountCategory
from src.services.classifier import AccountClassifier


class TestAccountClassifier:

    def test_classify_by_explicit_type(self):
        assert AccountClassifier.classify_single("Caja General", "liquidez") == AccountCategory.ACTIVO_CORRIENTE
        assert AccountClassifier.classify_single("Camion de reparto", "inversion") == AccountCategory.ACTIVO_NO_CORRIENTE
        assert AccountClassifier.classify_single("Deuda con Banco", "deuda_corto") == AccountCategory.PASIVO_CORRIENTE
        assert AccountClassifier.classify_single("Hipoteca", "deuda_largo") == AccountCategory.PASIVO_NO_CORRIENTE
        assert AccountClassifier.classify_single("Aportes", "propietarios") == AccountCategory.PATRIMONIO
        assert AccountClassifier.classify_single("Venta de productos", "ingreso") == AccountCategory.INGRESO
        assert AccountClassifier.classify_single("Gastos de luz", "egreso") == AccountCategory.EGRESO

    def test_classify_by_keywords(self):
        # Activo Corriente
        assert AccountClassifier.classify_single("Caja y Bancos") == AccountCategory.ACTIVO_CORRIENTE
        assert AccountClassifier.classify_single("Cuentas por Cobrar Clientes") == AccountCategory.ACTIVO_CORRIENTE
        assert AccountClassifier.classify_single("Inventario de Mercaderías") == AccountCategory.ACTIVO_CORRIENTE

        # Activo No Corriente
        assert AccountClassifier.classify_single("Terreno Sede Norte") == AccountCategory.ACTIVO_NO_CORRIENTE
        assert AccountClassifier.classify_single("Maquinaria y Equipos Industriales") == AccountCategory.ACTIVO_NO_CORRIENTE
        assert AccountClassifier.classify_single("Edificio Central") == AccountCategory.ACTIVO_NO_CORRIENTE

        # Pasivo Corriente
        assert AccountClassifier.classify_single("Cuentas por Pagar Proveedores") == AccountCategory.PASIVO_CORRIENTE
        assert AccountClassifier.classify_single("Impuestos por Pagar") == AccountCategory.PASIVO_CORRIENTE
        assert AccountClassifier.classify_single("Prestamo Bancario a 6 meses") == AccountCategory.PASIVO_CORRIENTE

        # Pasivo No Corriente
        assert AccountClassifier.classify_single("Hipoteca Inmobiliaria a 10 anos") == AccountCategory.PASIVO_NO_CORRIENTE
        assert AccountClassifier.classify_single("Prestamos Bancarios a Largo Plazo") == AccountCategory.PASIVO_NO_CORRIENTE

        # Patrimonio
        assert AccountClassifier.classify_single("Capital Social Aportado") == AccountCategory.PATRIMONIO
        assert AccountClassifier.classify_single("Utilidades Acumuladas") == AccountCategory.PATRIMONIO
        assert AccountClassifier.classify_single("Reserva Legal") == AccountCategory.PATRIMONIO

    def test_classify_records_marks_depreciable(self):
        records = [
            {"id_cuenta": "1", "nombre": "Terreno (Sede)", "monto": 100000.0, "vida_util_anios": None},
            {"id_cuenta": "2", "nombre": "Maquinaria", "monto": 50000.0, "vida_util_anios": 10},
            {"id_cuenta": "3", "nombre": "Caja y Bancos", "monto": 20000.0, "vida_util_anios": None}
        ]
        accounts = AccountClassifier.classify_records(records)
        
        # Terreno NO debe ser depreciable por regla de negocio
        assert accounts[0].nombre == "Terreno (Sede)"
        assert accounts[0].categoria == AccountCategory.ACTIVO_NO_CORRIENTE
        assert accounts[0].depreciable is False

        # Maquinaria SI es depreciable
        assert accounts[1].nombre == "Maquinaria"
        assert accounts[1].categoria == AccountCategory.ACTIVO_NO_CORRIENTE
        assert accounts[1].depreciable is True

        # Caja no es depreciable
        assert accounts[2].categoria == AccountCategory.ACTIVO_CORRIENTE
        assert accounts[2].depreciable is False
