import csv
import io
import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple, Union


class CSVParser:
    """Servicio de lectura, tolerancia a delimitadores y sanitización de CSV contables."""

    # Mapeo de alias para normalizar columnas
    COLUMN_ALIASES = {
        "id": ["id", "id_cuenta", "codigo", "code", "num", "numero", "nro", "cod"],
        "nombre": ["descripcion_cuenta", "descripcion", "nombre", "nombre_cuenta", "cuenta", "partida", "account", "name", "detalle"],
        "tipo": ["tipo_saldo", "tipo", "tipo_cuenta", "categoria", "category", "type", "clasificacion"],
        "monto": ["monto", "saldo", "valor", "importe", "balance", "amount", "total", "saldo_actual"],
        "vida_util": ["vida_util_anios", "vida_util", "vida_util_anos", "vida_util_meses", "useful_life", "anios_vida_util", "vida_util_año", "vida_util_ano"]
    }

    @staticmethod
    def normalize_text(text: str) -> str:
        """Elimina acentos, convierte a minúsculas y remueve espacios sobrantes."""
        if not text:
            return ""
        # Normalización NFD para separar caracteres de diacríticos
        text_normalized = unicodedata.normalize("NFD", text)
        text_no_accents = "".join(c for c in text_normalized if unicodedata.category(c) != "Mn")
        return text_no_accents.lower().strip()

    @classmethod
    def detect_delimiter(cls, sample_content: str) -> str:
        """Detecta automáticamente el delimitador del archivo CSV."""
        candidates = [",", ";", "\t", "|"]
        lines = [line.strip() for line in sample_content.splitlines() if line.strip()][:5]
        if not lines:
            return ","

        # Intentar usar csv.Sniffer
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff("\n".join(lines), delimiters=";,|\t")
            if dialect.delimiter in candidates:
                return dialect.delimiter
        except Exception:
            pass

        # Conteo por frecuencia si Sniffer falla
        delimiter_scores: Dict[str, int] = {d: 0 for d in candidates}
        for line in lines:
            for d in candidates:
                delimiter_scores[d] += line.count(d)

        best_delimiter = max(delimiter_scores.items(), key=lambda item: item[1])[0]
        return best_delimiter if delimiter_scores[best_delimiter] > 0 else ","

    @classmethod
    def sanitize_amount(cls, value: Any) -> float:
        """
        Sanitiza strings con símbolos monetarios ($ € Bs. BsF etc.),
        comas decimales vs puntos y espacios en blanco.
        """
        if value is None:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)

        val_str = str(value).strip()
        if not val_str:
            return 0.0

        # Manejo de negativos entre paréntesis ej. (1500.00)
        is_negative = False
        if val_str.startswith("(") and val_str.endswith(")"):
            is_negative = True
            val_str = val_str[1:-1].strip()
        elif val_str.startswith("-"):
            is_negative = True
            val_str = val_str[1:].strip()

        # Remover prefijos/sufijos de texto con posibles puntos como Bs. BsF. USD EUR etc.
        val_str = re.sub(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ]+\.?", "", val_str)
        # Remover símbolos de moneda
        val_str = re.sub(r"[\$\€\£\¥\₹]", "", val_str)
        # Remover espacios sobrantes
        val_str = val_str.strip()

        # Permitir solo dígitos, comas, puntos y signos
        val_str = re.sub(r"[^\d,\.]", "", val_str)
        if not val_str:
            return 0.0

        # Determinar si la coma o el punto es el separador decimal
        if "," in val_str and "." in val_str:
            if val_str.rfind(",") > val_str.rfind("."):
                # Formato europeo/latam: 1.500,50 -> 1500.50
                val_str = val_str.replace(".", "").replace(",", ".")
            else:
                # Formato anglosajón: 1,500.50 -> 1500.50
                val_str = val_str.replace(",", "")
        elif "," in val_str:
            # Solo comas: si hay múltiples comas, son separadores de miles
            if val_str.count(",") > 1:
                val_str = val_str.replace(",", "")
            else:
                parts = val_str.split(",")
                # Si tiene 3 dígitos después de la coma y más de 0 antes, ej 1,000 -> 1000
                if len(parts) == 2 and len(parts[1]) == 3 and len(parts[0]) > 0 and len(parts[0]) <= 3:
                    val_str = val_str.replace(",", "")
                else:
                    val_str = val_str.replace(",", ".")
        elif "." in val_str:
            # Solo puntos: si hay múltiples puntos (ej. 1.000.000), son miles
            if val_str.count(".") > 1:
                val_str = val_str.replace(".", "")

        try:
            amount = float(val_str)
            return -amount if is_negative else amount
        except ValueError:
            return 0.0

    @classmethod
    def sanitize_useful_life(cls, value: Any) -> Optional[float]:
        """Sanitiza el campo de vida útil en años."""
        if value is None:
            return None
        val_str = str(value).strip()
        if not val_str or val_str.lower() in ("none", "null", "nan", ""):
            return None
        try:
            years = cls.sanitize_amount(val_str)
            return years if years > 0 else None
        except Exception:
            return None

    @classmethod
    def map_columns(cls, header: List[str]) -> Dict[str, int]:
        """Mapea los nombres de las columnas a los campos canónicos del sistema."""
        mapping: Dict[str, int] = {}
        for idx, col in enumerate(header):
            col_norm = cls.normalize_text(col)
            for canon_field, aliases in cls.COLUMN_ALIASES.items():
                for alias in aliases:
                    if col_norm == alias or col_norm.replace("_", "") == alias.replace("_", ""):
                        mapping[canon_field] = idx
                        break
                if canon_field in mapping and mapping[canon_field] == idx:
                    break
        return mapping

    @classmethod
    def parse_file(cls, filepath: str) -> List[Dict[str, Any]]:
        """Lee y parsea un archivo CSV en una lista de registros estandarizados."""
        with open(filepath, "r", encoding="utf-8-sig", errors="replace") as f:
            content = f.read()
        return cls.parse_content(content)

    @classmethod
    def parse_content(cls, content: str) -> List[Dict[str, Any]]:
        """Parsea el contenido de texto CSV en una lista de registros estandarizados."""
        if not content.strip():
            return []

        delimiter = cls.detect_delimiter(content)
        reader = csv.reader(io.StringIO(content), delimiter=delimiter)

        rows = [row for row in reader if any(cell.strip() for cell in row)]
        if not rows:
            return []

        header = rows[0]
        col_map = cls.map_columns(header)

        # Si no se detectó al menos la columna nombre o monto, intentar fallback posicional
        if "nombre" not in col_map and len(header) >= 2:
            col_map["id"] = 0
            col_map["nombre"] = 1
            col_map["monto"] = min(3, len(header) - 1)

        records: List[Dict[str, Any]] = []
        for line_idx, row in enumerate(rows[1:], start=2):
            if not any(cell.strip() for cell in row):
                continue

            id_val = row[col_map["id"]].strip() if "id" in col_map and col_map["id"] < len(row) else str(line_idx)
            nombre_val = row[col_map["nombre"]].strip() if "nombre" in col_map and col_map["nombre"] < len(row) else f"Cuenta_{line_idx}"
            tipo_val = row[col_map["tipo"]].strip() if "tipo" in col_map and col_map["tipo"] < len(row) else ""
            
            monto_raw = row[col_map["monto"]] if "monto" in col_map and col_map["monto"] < len(row) else 0.0
            monto_val = cls.sanitize_amount(monto_raw)

            vida_util_raw = row[col_map["vida_util"]] if "vida_util" in col_map and col_map["vida_util"] < len(row) else None
            vida_util_val = cls.sanitize_useful_life(vida_util_raw)

            records.append({
                "id_cuenta": id_val,
                "nombre": nombre_val,
                "tipo_crudo": tipo_val,
                "monto": monto_val,
                "vida_util_anios": vida_util_val,
            })

        return records
