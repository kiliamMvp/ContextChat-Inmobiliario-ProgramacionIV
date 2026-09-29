# 03 — Historial persistente del chat (tipo ChatGPT)

## Objetivo de la sesión
Mostrar en `/chat/<house_id>/` el historial de conversaciones guardado,
reutilizando el modelo `ChatMessage` existente, con una mejora visual pequeña.

## Qué se pidió
- Historial visible por propiedad (pregunta, respuesta, fecha/hora), ordenado.
- Comportamiento tipo ChatGPT: al volver, las conversaciones siguen ahí.
- Transformar la sección "Ideas de preguntas" en "Historial de conversación",
  conservando atajos útiles debajo.
- Sin cambiar modelos, Ollama, restricción, CSRF ni errores. 28 tests debían seguir pasando.

## Archivos revisados
- `chatbot/views.py` (`chat_view` ya consultaba `ChatMessage` y lo pasaba como
  `messages`; ya guardaba cada pregunta/respuesta; ya no usa `@csrf_exempt`).
- `chatbot/models.py` (`ChatMessage` con `ordering = ['created_at']`).
- `chatbot/templates/chatbot/chat.html` (tenía "Ideas de Preguntas" en el
  lateral y ya mostraba historial en el área principal).
- `chatbot/tests.py` (para agregar el test sin duplicar).

## Archivos modificados
1. `chatbot/templates/chatbot/chat.html` (único cambio visual + funcional):
   el bloque lateral "Ideas de Preguntas" ahora es "Historial de
   conversación": lista pregunta/respuesta/fecha de cada `msg in messages`
   con scroll (`max-h-64`), mensaje vacío
   "Todavía no hay conversaciones para esta propiedad.", y debajo una
   sección pequeña "Ideas de preguntas" con 2 atajos (precio, hospitales).
2. `chatbot/tests.py`: import de `ChatMessage` + clase `TestHistorialVisible`
   (2 tests: historial vacío e historial en orden).

No se tocó backend (ya existía), modelos, migraciones, Ollama ni JS del formulario.

## Cómo se implementó el historial
Se reutilizó `ChatMessage.objects.filter(house_id=...)` que la vista ya
pasaba al template. El historial NO se envía a Ollama; solo se muestra.
Al enviar, el JS agrega el mensaje al momento y el POST lo guarda, así que
al recargar aparece desde la BD.

## Resultados
```bash
python manage.py check
# System check identified no issues (0 silenced).

python manage.py test
# Ran 30 tests ... OK (28 anteriores + 2 nuevas)
```

## Impacto
El chat conserva el diseño, CSRF, restricción inmobiliaria, manejo de
errores y botones CSV/PDF. La única diferencia visible es el lateral con
historial persistente por propiedad.
