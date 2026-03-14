# Auto-mejora del Workspace

## Detectar patrones repetitivos

Si el usuario hace la misma instrucción por **tercera vez** en diferentes sesiones, proponer al final de la tarea:

> "Noto que me has dado esta instrucción varias veces: [instrucción]. ¿Quieres que la agregue como regla permanente con `/newrule` para no tener que repetirla?"

## Cuándo proponer cada tipo de customización

| Situación | Solución propuesta |
|-----------|-------------------|
| Instrucción repetida 3+ veces | Rule (global si aplica a todo, workspace si es proyecto) |
| Proceso multi-paso ejecutado 2+ veces | Workflow (`.clinerules/workflows/nuevo.md`) |
| Conocimiento especializado extenso | Skill (`~/.cline/skills/nuevo/SKILL.md`) |
| Validación automática necesaria | Hook (`.clinerules/hooks/PreToolUse`) |
| Archivos que llenan contexto innecesariamente | Entrada en `.clineignore` |

## Usar `/newrule` para reglas interactivas

Cuando detectes un patrón que merece una regla, sugerir al usuario:
```
"Puedo crear una regla para esto con /newrule. ¿Lo hago?"
```

## Nunca auto-modificar archivos del sistema de customización

No editar reglas, workflows, skills o hooks de forma autónoma. Siempre:
1. Proponer el cambio
2. Mostrar el contenido exacto que se agregaría
3. Esperar confirmación explícita
4. Ejecutar el cambio

## Usar Plan Mode para tareas complejas

Para cualquier tarea que afecte múltiples archivos o requiera decisiones arquitectónicas:
- Iniciar en **Plan Mode** para explorar y diseñar
- Usar `/deep-planning` para tareas grandes (feature cross-cutting, refactors)
- Cambiar a **Act Mode** solo cuando el plan esté confirmado

## Focus Chain para tareas largas

Cuando una tarea tiene 5+ pasos independientes, activar Focus Chain si está disponible para mantener el progreso visible y persistente entre compactaciones de contexto.