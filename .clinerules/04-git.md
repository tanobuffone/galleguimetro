# Convenciones Git

## Formato de commits — Conventional Commits

```
<tipo>(<scope>): <descripción imperativa en español>

[cuerpo opcional: qué y por qué, no cómo]

[footer: Breaking Changes, refs a issues]
```

**Tipos permitidos:**
- `feat`: nueva funcionalidad
- `fix`: corrección de bug
- `refactor`: refactor sin cambio de comportamiento
- `test`: agregar o corregir tests
- `docs`: documentación
- `chore`: mantenimiento, deps, config
- `perf`: mejora de performance
- `mem`: actualización de memory bank (tipo especial del workspace)
- `data`: cambios en schemas o migraciones de DB

**Ejemplos correctos:**
```
feat(auth): agregar autenticación JWT con refresh tokens
fix(portfolio): corregir cálculo de CAGR con fechas timezone-aware
mem: 2025-03-10 session update — implementado módulo de portfolio
data: agregar tabla portfolio_snapshots con índice GIN en metadata
```

## Reglas de seguridad

- **Verificar `.gitignore` antes de `git add .`** — buscar `.env`, `*.key`, `*.pem`, `credentials*`
- **Nunca** agregar archivos con credenciales, aunque el usuario lo pida explícitamente
- **`git push --force`**: mostrar el comando, explicar el riesgo, esperar confirmación explícita
- **Ramas**: `main` es producción. Usar ramas para features: `feat/nombre`, `fix/nombre`

## Commits atómicos

- Un commit = un cambio lógico
- No mezclar refactor + nueva feature en mismo commit
- Los archivos `memory-bank/` siempre en commits separados (`mem:`)
- Los archivos de migración DB siempre en commits separados (`data:`)

## Antes de cada commit

```bash
git diff --cached  # revisar qué se va a commitear
git status         # verificar que no hay archivos inesperados