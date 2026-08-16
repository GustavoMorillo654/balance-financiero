"""Aplicación web para cargar CSV y presentar el análisis financiero."""

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.staticfiles import StaticFiles

from src.index import process_balance_content


MAX_UPLOAD_BYTES = 5 * 1024 * 1024
PUBLIC_DIR = Path(__file__).resolve().parent.parent / "public"

app = FastAPI(
    title="Balance Financiero",
    version="1.0.0",
    description="Procesamiento de balances, índices financieros y evaluación de crédito.",
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    """Confirma que la función web está disponible."""
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze_csv(
    file: UploadFile = File(...),
    period_days: int = Query(365, ge=1, le=366),
) -> dict:
    """Procesa un archivo CSV cargado por el usuario."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Seleccione un archivo con extensión .csv.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="El archivo CSV está vacío.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="El archivo excede el límite de 5 MB.",
        )

    csv_content = content.decode("utf-8-sig", errors="replace")
    result = process_balance_content(csv_content, periodo_dias=period_days)
    return result


# En desarrollo FastAPI también sirve la interfaz. En Vercel, `public/` se
# publica por separado y no se incluye dentro del bundle de la función Python.
if PUBLIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="web")
