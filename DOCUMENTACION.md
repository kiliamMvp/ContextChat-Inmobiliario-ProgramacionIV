# DOCUMENTACION.md — Decisiones técnicas (Entregable Final)

## 1. Arquitectura

```
Usuario
  ↓  formulario de chat (/chat/<id>/)
Django (chatbot/views.py)
  ↓  detect_intent + validate_data (chatbot/logic.py)
  ├─ fuera del dominio → respuesta fija SIN llamar a Ollama
  └─ dentro del dominio → datos reales de la BD (chatbot/context.py)
        ↓  prompt con contexto (chatbot/services/ollama_service.py)
      Ollama http://localhost:11434, modelo casas-qwen2.5
        ↓  respuesta
Django → Usuario (y guarda en ChatMessage)
```

Se conservó el proyecto existente: misma app `chatbot`, mismos modelos base,
mismas URLs y plantillas del chat. Solo se agregó lo que pedía la actividad.

## 2. Entidad

`House` (propiedad): id, codigo (único), name, location, price, description,
dormitorios → 7 campos. `Place` (lugar cercano por categoría) y
`HouseDistance` (distancia en metros) ya existían y se mantuvieron.
`ChatMessage` (historial) ya existía y se mantuvo.

Se agregaron solo 2 campos (`codigo`, `dormitorios`) porque la actividad pide
mínimo 6 campos con identificador único. El precio es numérico
(`DecimalField(max_digits=12, decimal_places=2)`); la migración
`0004_alter_house_price.py` convirtió los precios de texto a Decimal
conservando los datos. Para mostrarlo se usa `precio_formateado()`
(ej: `$480,000`).

## 3. Integración con Ollama

- Servicio en `chatbot/services/ollama_service.py` (patrón Factory).
- `chatbot/ai.py` quedó como función `generate_response()` que usa el servicio,
  para no romper las vistas ni el comando `chat`.
- Siempre se envía pregunta + datos reales de la BD, nunca solo la pregunta.
- Modelo: `casas-qwen2.5` (basado en `qwen2.5:1.5b`), ver `modelfile-casas`.
- Configuración por variables `OLLAMA_URL` y `OLLAMA_MODEL` (ver `.env.example`).

## 4. Restricción de la IA (dos niveles)

- Nivel 1 (Ollama): `modelfile-casas` con system prompt e instrucciones.
- Nivel 2 (Django): `logic.py` bloquea antes de llamar a Ollama.
  Mensaje exacto fuera del dominio:
  `Solo puedo responder consultas sobre propiedades inmobiliarias y sus datos.`
  Mensaje exacto sin datos:
  `No tengo ese dato disponible.`
- Se quitaron de las plantillas los textos y botones que invitaban a
  preguntas libres (cielo azul, chistes, capital de Francia).

## 5. Patrones de diseño

1. **Strategy** (`chatbot/reports.py`): cada reporte es una clase con
   `calcular()`. La vista solo recorre la lista `REPORTES`. Agregar un reporte
   nuevo no toca la vista. Resuelve: 5 reportes ordenados y extensibles.
2. **Factory** (`chatbot/report_factory.py`): `ReporteFactory.crear(tipo)`
   devuelve la estrategia (`total`, `mas_cara`, `mas_barata`,
   `bajo_promedio`, `por_ubicacion`) sin que la vista conozca las clases.
   Tipo inexistente lanza `ValueError`. Resuelve: crear reportes en un solo
   lugar. No confundir con `crear_servicio_ollama()`, que centraliza la
   creación del servicio de Ollama (no crea reportes).

## 6. Estructura de la app

```
chatbot/
  models.py      House, Place, HouseDistance, ChatMessage
  forms.py       HouseForm con validaciones
  views.py       catálogo, CRUD, reportes, chat, exportar CSV/PDF
  urls.py        rutas (se mantuvieron las existentes)
  logic.py       detect_intent + validate_data (restricción)
  context.py     arma el contexto real desde la BD
  ai.py          generate_response (usa el servicio)
  services/      ollama_service.py (Factory + servicio)
  reports.py     5 reportes (Strategy)
  report_factory.py  Factory de reportes
  admin.py       administración personalizada
  tests.py       30 pruebas unitarias
  templates/     catálogo, chat, CRUD, reportes
```

## 7. Validaciones

- `codigo` obligatorio y único (BD + formulario).
- `price` obligatorio y no negativo (`DecimalField` + `clean_price`).
- `dormitorios` no negativo.
- Mensajes de éxito/error con `django.contrib.messages` en crear/editar/eliminar.

## 8. Manejo de errores

- Propiedad inexistente: página 404.
- Pregunta vacía: `Por favor, escribe una pregunta para comenzar.`
- Ollama apagado: `No fue posible comunicarse con el servicio de IA local.
  Verifique que Ollama esté ejecutándose.` (sin traceback).
- Error interno del chat: JSON con mensaje, no se cae la página.
