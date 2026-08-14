import unicodedata
from typing import Any, Dict, List, Tuple
from src.models.account import Account, AccountCategory


class AccountClassifier:
    """Clasificador dinámico de partidas contables por liquidez, exigibilidad y reglas semánticas."""

    # Mapeo de tipos explícitos (ej. columna tipo_saldo en CSV)
    TYPE_EXPLICIT_MAP = {
        # Activo Corriente
        "liquidez": AccountCategory.ACTIVO_CORRIENTE,
        "disponible": AccountCategory.ACTIVO_CORRIENTE,
        "caja": AccountCategory.ACTIVO_CORRIENTE,
        "bancos": AccountCategory.ACTIVO_CORRIENTE,
        "derecho_cobro": AccountCategory.ACTIVO_CORRIENTE,
        "exigible": AccountCategory.ACTIVO_CORRIENTE,
        "almacen": AccountCategory.ACTIVO_CORRIENTE,
        "realizable": AccountCategory.ACTIVO_CORRIENTE,
        "inventario": AccountCategory.ACTIVO_CORRIENTE,
        "activo_corriente": AccountCategory.ACTIVO_CORRIENTE,
        "activo_circulante": AccountCategory.ACTIVO_CORRIENTE,
        "circulante": AccountCategory.ACTIVO_CORRIENTE,

        # Activo No Corriente
        "inversion": AccountCategory.ACTIVO_NO_CORRIENTE,
        "activo_no_corriente": AccountCategory.ACTIVO_NO_CORRIENTE,
        "activo_fijo": AccountCategory.ACTIVO_NO_CORRIENTE,
        "fijo": AccountCategory.ACTIVO_NO_CORRIENTE,
        "propiedad_planta_equipo": AccountCategory.ACTIVO_NO_CORRIENTE,
        "intangible": AccountCategory.ACTIVO_NO_CORRIENTE,
        "no_corriente": AccountCategory.ACTIVO_NO_CORRIENTE,

        # Pasivo Corriente
        "deuda_corto": AccountCategory.PASIVO_CORRIENTE,
        "pasivo_corriente": AccountCategory.PASIVO_CORRIENTE,
        "pasivo_circulante": AccountCategory.PASIVO_CORRIENTE,
        "corto_plazo": AccountCategory.PASIVO_CORRIENTE,
        "obligacion_corto": AccountCategory.PASIVO_CORRIENTE,

        # Pasivo No Corriente
        "deuda_largo": AccountCategory.PASIVO_NO_CORRIENTE,
        "pasivo_no_corriente": AccountCategory.PASIVO_NO_CORRIENTE,
        "largo_plazo": AccountCategory.PASIVO_NO_CORRIENTE,
        "obligacion_largo": AccountCategory.PASIVO_NO_CORRIENTE,

        # Patrimonio
        "propietarios": AccountCategory.PATRIMONIO,
        "patrimonio": AccountCategory.PATRIMONIO,
        "capital": AccountCategory.PATRIMONIO,
        "capital_social": AccountCategory.PATRIMONIO,
        "reservas": AccountCategory.PATRIMONIO,
        "superavit": AccountCategory.PATRIMONIO,

        # Cuentas de Resultados
        "ingreso": AccountCategory.INGRESO,
        "ingresos": AccountCategory.INGRESO,
        "ventas": AccountCategory.INGRESO,
        "egreso": AccountCategory.EGRESO,
        "egresos": AccountCategory.EGRESO,
        "costo": AccountCategory.EGRESO,
        "gasto": AccountCategory.EGRESO,
    }

    # Catálogo de palabras clave por nombre de cuenta
    KEYWORDS_MAP = [
        # 1. Pasivo No Corriente (Largo Plazo primero para evitar colisión con 'prestamo' o 'pagar')
        (AccountCategory.PASIVO_NO_CORRIENTE, [
            "hipoteca", "hipotecari", "largo plazo", "lp", "largo_plazo", "10 anos", "10 anios",
            "5 anos", "5 anios", "20 anos", "prestamo bancario a largo", "deuda a largo plazo",
            "obligaciones a largo", "bonos por pagar"
        ]),
        # 2. Pasivo Corriente (Corto Plazo)
        (AccountCategory.PASIVO_CORRIENTE, [
            "cuenta por pagar", "cuentas por pagar", "proveedor", "proveedores", "sueldos por pagar",
            "salarios por pagar", "impuesto por pagar", "impuestos por pagar", "tributos",
            "iva debito", "iva por pagar", "prestamo bancario a corto", "prestamo a corto",
            "a 6 meses", "a 3 meses", "a 12 meses", "a 1 ano", "a 1 anio", "corto plazo",
            "cp", "documentos por pagar", "acreedor", "acreedores"
        ]),
        # 3. Patrimonio
        (AccountCategory.PATRIMONIO, [
            "capital social", "capital aportado", "capital pagado", "capital", "acciones comunes",
            "acciones preferentes", "utilidades acumuladas", "utilidad acumulada", "ganancias acumuladas",
            "resultado acumulado", "resultados acumulados", "perdidas acumuladas", "reserva legal",
            "reservas estatutarias", "superavit"
        ]),
        # 4. Activo No Corriente
        (AccountCategory.ACTIVO_NO_CORRIENTE, [
            "terreno", "terrenos", "maquinaria", "equipo", "equipos", "vehiculo", "vehiculos",
            "mobiliario", "muebles y enseres", "edificio", "edificios", "edificaciones", "inmueble",
            "construcciones", "planta", "herramientas", "patente", "patentes", "marcas",
            "propiedad, planta", "propiedad planta"
        ]),
        # 5. Activo Corriente
        (AccountCategory.ACTIVO_CORRIENTE, [
            "caja", "banco", "bancos", "efectivo", "liquidez", "cuenta por cobrar", "cuentas por cobrar",
            "cliente", "clientes", "deudores", "inventario", "inventarios", "mercancia",
            "mercaderia", "existencias", "almacen", "anticipo a proveedores", "valores negociables",
            "inversiones temporales", "iva credito", "iva por cobrar"
        ]),
        # 6. Ingresos
        (AccountCategory.INGRESO, [
            "venta", "ventas", "ingreso por", "ingresos por", "ingreso de", "ingresos de",
            "facturacion", "honorarios profesionales"
        ]),
        # 7. Egresos / Costos / Gastos
        (AccountCategory.EGRESO, [
            "costo de venta", "costo de ventas", "costos", "gasto general", "gastos generales",
            "gastos administrativos", "gasto administrativo", "gastos de ventas", "gastos operativos",
            "gasto operativo", "sueldos y salarios", "alquileres", "servicios basicos"
        ])
    ]

    @staticmethod
    def normalize_str(text: str) -> str:
        """Normaliza cadenas eliminando acentos y puntuación."""
        if not text:
            return ""
        nfd = unicodedata.normalize("NFD", text)
        no_accents = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
        return no_accents.lower().strip()

    @classmethod
    def classify_single(cls, nombre: str, tipo_crudo: str = "") -> AccountCategory:
        """Determina la categoría contable de una partida usando tipo_crudo o análisis léxico de nombre."""
        tipo_norm = cls.normalize_str(tipo_crudo).replace(" ", "_").replace("-", "_")
        if tipo_norm in cls.TYPE_EXPLICIT_MAP:
            return cls.TYPE_EXPLICIT_MAP[tipo_norm]

        nombre_norm = cls.normalize_str(nombre)

        # Reglas léxicas por catálogo
        for category, keywords in cls.KEYWORDS_MAP:
            for kw in keywords:
                if kw in nombre_norm:
                    return category

        # Fallback inteligente si no coincide con ninguna palabra clave
        if "pagar" in nombre_norm or "deuda" in nombre_norm:
            return AccountCategory.PASIVO_CORRIENTE
        if "cobrar" in nombre_norm or "activo" in nombre_norm:
            return AccountCategory.ACTIVO_CORRIENTE
        if "gasto" in nombre_norm or "costo" in nombre_norm:
            return AccountCategory.EGRESO
        if "ingreso" in nombre_norm or "venta" in nombre_norm:
            return AccountCategory.INGRESO

        # Por defecto asignar a Activo Corriente para alertar o ajustar
        return AccountCategory.ACTIVO_CORRIENTE

    @classmethod
    def classify_records(cls, records: List[Dict[str, Any]]) -> List[Account]:
        """Convierte una lista de diccionarios parseados en instancias de Account clasificadas."""
        accounts: List[Account] = []
        for rec in records:
            cat = cls.classify_single(rec.get("nombre", ""), rec.get("tipo_crudo", ""))
            
            # Activos no corrientes son candidatos a depreciación si no son Terreno
            nombre_norm = cls.normalize_str(rec.get("nombre", ""))
            is_terreno = "terreno" in nombre_norm
            depreciable = (cat == AccountCategory.ACTIVO_NO_CORRIENTE) and not is_terreno

            account = Account(
                id_cuenta=str(rec.get("id_cuenta", "")),
                nombre=rec.get("nombre", "").strip(),
                categoria=cat,
                saldo=float(rec.get("monto", 0.0)),
                vida_util_anios=rec.get("vida_util_anios"),
                depreciable=depreciable,
                depreciacion_acumulada=0.0,
                valor_neto=float(rec.get("monto", 0.0))
            )
            accounts.append(account)
        return accounts
