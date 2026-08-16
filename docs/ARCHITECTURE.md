# Arquitectura web

La aplicación usa una arquitectura de dos capas que conserva el motor Python existente:

```text
Navegador (public/index.html)
        │ POST multipart/form-data
        ▼
FastAPI /api/analyze (src/web.py)
        ▼
Pipeline: CSVParser → AccountClassifier → DepreciationEngine
        ▼
AccountingValidator → FinancialRatios → CreditEvaluation
        ▼
Contrato JSON → interfaz
```

`public/index.html` es un cliente estático sin dependencias. En desarrollo, FastAPI lo sirve junto con las rutas `/api/health` y `/api/analyze`. En Vercel, `api/index.py` exporta la aplicación ASGI como función Python y el directorio `public/` se sirve como contenido estático.

La API acepta un campo multipart `file` con extensión `.csv` y un parámetro opcional `period_days` de 1 a 366. Limita las cargas a 5 MB y devuelve errores HTTP accionables para extensión inválida, archivo vacío o tamaño excesivo. No se persisten archivos ni resultados.
