# Documentación

## README.md — estructura mínima

```markdown
# Nombre del Proyecto
Descripción de una línea.

## Prerrequisitos
## Instalación
## Variables de entorno (.env.example)
## Cómo correr tests
## Estructura del proyecto
```

## Estilo Markdown

- Oraciones en minúscula para headings (sentence case), no Title Case
- Párrafos cortos: 3-4 oraciones máximo
- Code blocks con lenguaje especificado siempre: ` ```python `
- Links relativos para referencias internas al repo

## ADRs (Architecture Decision Records) — en memory-bank/decisions/

```markdown
## ADR-[N]: [Título de la decisión]
**Fecha:** YYYY-MM-DD
**Estado:** Accepted | Deprecated | Superseded by ADR-[N]

### Contexto
[Por qué se necesitaba esta decisión]

### Opciones consideradas
1. **[Opción A]** — pros: [...] / contras: [...]

### Decisión
[Qué se eligió y por qué]

### Consecuencias
[Qué implica hacia adelante]
```

## Memory Bank — recordatorio de actualización

`activeContext.md` es el archivo que más cambia — actualizar al final de cada sesión.
`progress.md` es append-only — nunca borrar entradas existentes.
`projectbrief.md` es inmutable — solo modificar con instrucción explícita del usuario.