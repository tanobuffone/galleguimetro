## Arquitectura del Sistema

**Backend (FastAPI)**:
- Puerto: 8000
- Conexión DDE: win32com.client
- Cálculos: QuantLib
- Base de datos: PostgreSQL (ws-postgres:5432)
- Vectores: Qdrant (ws-qdrant:6333)

**Frontend (React)**:
- Puerto: 3000
- Gráficos: TradingView Charting Library
- Estado: Redux Toolkit
- Tiempo real: WebSocket

**Flujo de Datos**:
1. Excel → DDE → Backend Python
2. Backend → PostgreSQL (datos estructurados)
3. Backend → Qdrant (vectores financieros)
4. Backend → Frontend (API REST + WebSocket)