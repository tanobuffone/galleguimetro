# Protocolo de Búsqueda y Selección de Herramientas

## Orden de búsqueda web (siempre respetar)

Escalar al siguiente nivel **solo** cuando el anterior sea insuficiente:

```
1. SearXNG local  →  http://localhost:8080  (ilimitado — SIEMPRE primero)
2. Fetch directo  →  URL conocida           (ilimitado — segunda opción)
3. ArXiv MCP      →  papers científicos     (ilimitado — para academia)
4. Exa            →  búsqueda semántica     (1.000/mes — usar con criterio)
5. Tavily         →  extracción estructurada (1.000/mes — usar con criterio)
6. Supadata       →  YouTube/multimedia     (freemium — solo si no hay texto)
```

**Monitorear cuota**: Si Exa o Tavily devuelven error de límite, reportar al usuario y usar solo SearXNG + fetch hasta el próximo mes.

## Documentación de librerías — Context7 obligatorio

Para **cualquier tarea que genere código** usando librerías externas:
- Agregar `use context7` al prompt interno
- Context7 devuelve la documentación actualizada de la versión instalada
- Nunca asumir API de una librería sin verificarla — las versiones cambian

Librerías que **siempre** necesitan Context7: python-pptx, qdrant-client, fastmcp, SQLAlchemy, FastAPI, pydantic, yfinance, matplotlib, openscad-mcp.

## Selección de base de datos

| Tipo de dato | Base de datos | Cuándo |
|-------------|--------------|--------|
| Registros estructurados, joins, métricas | PostgreSQL + pgvector | Consultas relacionales, agregaciones |
| Relaciones, ontologías, grafos | Memgraph (Cypher) | Cuando las conexiones entre entidades importan |
| Búsqueda semántica por significado | Qdrant | Búsqueda por similitud, no por valor exacto |
| Cache temporal | Redis | Solo si hay cola de tareas o necesidad de TTL |

## Generación de imágenes

```
1. Pollinations.ai  →  https://image.pollinations.ai  (gratis, sin clave, sin límite)
2. ComfyUI local    →  http://localhost:8188            (Stable Diffusion, GPU local)
```

Nunca usar: DALL-E, Midjourney, Stability AI API pago, fal.ai, Replicate pago.

## Regla de Context Window

Antes de cargar archivos grandes en contexto, preguntar: ¿Necesito el archivo completo o solo una sección? Usar `read_file` con rangos de línea cuando sea posible. Los subagents son ideales para exploración paralela sin llenar el contexto principal.