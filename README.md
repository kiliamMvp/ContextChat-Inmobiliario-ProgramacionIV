# ContextChat Inmobiliario — Entregable Final Programación IV

Sistema en Django para administrar propiedades inmobiliarias (CRUD + reportes)
con un chatbot que responde preguntas usando IA local (Ollama, modelo `casas-qwen2.5`).

## Requisitos

- Python 3.11
- Django 5.2.17 (ver `requirements.txt`)
- Ollama instalado y corriendo en `http://localhost:11434`
- SQLite (ya incluido con Python)

## Instalación

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Variables de entorno

```bash
cp .env.example .env
```

Valores usados (`OLLAMA_URL`, `OLLAMA_MODEL`, `SECRET_KEY`, `DEBUG`).
Si no existe `.env`, la app usa valores por defecto y funciona igual.

## Ollama y el modelo

```bash
ollama pull qwen2.5:1.5b
ollama create casas-qwen2.5 -f modelfile-casas
ollama run casas-qwen2.5
```

El modelo `casas-qwen2.5` solo responde sobre propiedades inmobiliarias.
Además Django bloquea las preguntas fuera del dominio sin llamar a Ollama.

## Base de datos

```bash
python manage.py migrate
python create_data.py
```

`create_data.py` carga 3 propiedades de ejemplo
(Villa Serena, Ático Mirador Real, Residencial Los Robles).

## Ejecutar

```bash
python manage.py runserver
```

Abrir `http://127.0.0.1:8000/`.

- `/` catálogo de propiedades
- `/propiedades/nueva/` crear propiedad
- `/propiedades/<id>/` detalle, `/editar/`, `/eliminar/`
- `/reportes/` 5 reportes con datos reales
- `/chat/<id>/` chat con IA sobre esa propiedad
- `/admin/` administración

## Pruebas

```bash
python manage.py check
python manage.py test
```

## Cómo funciona el chat

1. El usuario escribe una pregunta en `/chat/<id>/`.
2. Django detecta si es sobre propiedades (precio, ubicación, descripción,
   hospitales, colegios, transporte, tiendas).
3. Si NO es del dominio, responde fijo sin llamar a Ollama:
   `Solo puedo responder consultas sobre propiedades inmobiliarias y sus datos.`
4. Si es del dominio, busca los datos reales en la base de datos,
   los envía a `casas-qwen2.5` y muestra la respuesta.
5. Si falta el dato: `No tengo ese dato disponible.`
6. Si Ollama está apagado: `No fue posible comunicarse con el servicio de
   IA local. Verifique que Ollama esté ejecutándose.`
