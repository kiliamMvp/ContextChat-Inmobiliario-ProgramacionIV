# Cambios realizados al proyecto

## 1. Adaptación del proyecto

Se tomó como base el proyecto:

**Context Chat Module (Django + Local AI)**

Repositorio original:

https://github.com/ARAVINDs2002/ContextChat-Context-Aware-Chatbot-for-Detail-Pages-Django-Ollama-

Se realizaron modificaciones para cumplir con los requisitos de la actividad.

---

## 2. Cambio de versión de Django

El proyecto original utilizaba una versión anterior de Django.

Se modificó `requirements.txt` para utilizar Django 5.2:

```text
Django>=5.2,<5.3
requests
rich
```

Versión utilizada:

```text
Django 5.2.17
```

---

## 3. Adaptación de la configuración del proyecto

El proyecto clonado no tenía completa la estructura de configuración de Django necesaria para ejecutarlo directamente.

Se creó la configuración:

```text
contextchat/
├── __init__.py
├── asgi.py
├── settings.py
├── urls.py
└── wsgi.py
```

También se configuró:

```python
DJANGO_SETTINGS_MODULE = "contextchat.settings"
```

Se agregó la aplicación `chatbot` a `INSTALLED_APPS`.

Además, se configuró `ALLOWED_HOSTS` para permitir el acceso mediante la dirección IP local del equipo.

---

## 4. Traducción de la interfaz

Se modificó:

```text
chatbot/templates/chatbot/chat.html
```

Se tradujeron al español diferentes elementos de la interfaz:

* Títulos.
* Mensajes de bienvenida.
* Botones.
* Preguntas rápidas.
* Mensajes del asistente.
* Textos relacionados con las propiedades.
* Mensajes de ayuda.

El objetivo fue que la aplicación pudiera ser presentada completamente en español.

---

## 5. Cambio del modelo de Ollama

El proyecto original utilizaba:

```text
mistral:7b-instruct
```

Se cambió por:

```text
qwen2.5:1.5b
```

El cambio se realizó en:

```text
chatbot/ai.py
```

La aplicación continúa utilizando Ollama mediante:

```text
http://localhost:11434/api/generate
```

---

## 6. Ajuste del prompt

Se modificó el prompt utilizado para generar las respuestas.

Se indicó al modelo que:

* Utilice solamente los datos proporcionados por Django.
* No invente información.
* No compare propiedades.
* Responda de manera breve.
* Responda en español.

Esto permite que las respuestas sean más adecuadas para la interfaz modificada.

---

# 7. Historial de conversación

Se creó el modelo:

```text
ChatMessage
```

en:

```text
chatbot/models.py
```

Este modelo guarda:

```text
Propiedad
Pregunta
Respuesta
Fecha y hora
```

Se creó la migración:

```bash
python manage.py makemigrations chatbot
```

Resultado:

```text
Migrations for 'chatbot':
  chatbot/migrations/0002_alter_place_category_chatmessage.py
    ~ Alter field category on place
    + Create model ChatMessage
```

Se aplicó con:

```bash
python manage.py migrate
```

Resultado:

```text
Applying chatbot.0002_alter_place_category_chatmessage... OK
```

---

## 8. Guardado automático del historial

Se modificó:

```text
chatbot/views.py
```

para guardar automáticamente cada pregunta y respuesta en `ChatMessage`.

El historial queda asociado a cada propiedad.

---

## 9. Visualización del historial

Se modificó:

```text
chatbot/templates/chatbot/chat.html
```

para mostrar las conversaciones almacenadas.

Cada mensaje muestra:

* Pregunta del usuario.
* Respuesta de la IA.
* Fecha y hora.

También se agregó desplazamiento automático para facilitar la visualización de los mensajes recientes.

---

# 10. Exportación CSV

Se agregó una nueva vista:

```text
export_chat_csv
```

La ruta agregada es:

```text
/chat/<house_id>/exportar/csv/
```

El archivo descargado contiene:

```text
ID Mensaje
Fecha y Hora
Propiedad
Pregunta del Usuario
Respuesta de la IA
```

El CSV utiliza codificación UTF-8 con BOM para facilitar su apertura en Excel y mantener correctamente los caracteres del español.

---

# 11. Exportación PDF

Se agregó una nueva vista:

```text
export_chat_pdf
```

La ruta agregada es:

```text
/chat/<house_id>/exportar/pdf/
```

También se creó:

```text
chatbot/pdf_export.py
```

Este módulo genera el PDF directamente en memoria y permite descargar el historial de la conversación.

No se utilizaron dependencias externas pesadas para esta funcionalidad.

---

# 12. Pruebas

Se agregó:

```text
test_history_and_export.py
```

Las pruebas verifican:

* Guardado del historial.
* Visualización del historial.
* Descarga CSV.
* Descarga PDF.

Comando:

```bash
./venv/bin/python test_history_and_export.py
```

Resultado:

```text
----------------------------------------------------------------------
Ran 4 tests
OK
```

También se mantuvo la prueba original:

```bash
./venv/bin/python verify.py
```

Resultado:

```text
----------------------------------------------------------------------
Ran 3 tests
OK
```

---

# 13. Archivos modificados

| Archivo                               | Cambio                                         |
| ------------------------------------- | ---------------------------------------------- |
| `requirements.txt`                    | Adaptación a Django 5.2                        |
| `manage.py`                           | Configuración del proyecto Django              |
| `contextchat/settings.py`             | Configuración de Django y aplicación           |
| `contextchat/urls.py`                 | Inclusión de las rutas de `chatbot`            |
| `chatbot/models.py`                   | Nuevo modelo `ChatMessage`                     |
| `chatbot/views.py`                    | Historial y exportaciones                      |
| `chatbot/urls.py`                     | Nuevas rutas CSV y PDF                         |
| `chatbot/ai.py`                       | Cambio de modelo Ollama y prompt               |
| `chatbot/templates/chatbot/chat.html` | Traducción, historial y botones de exportación |

---

# 14. Archivos nuevos

```text
contextchat/
chatbot/migrations/0002_alter_place_category_chatmessage.py
chatbot/pdf_export.py
test_history_and_export.py
```

---

# 15. Comandos principales utilizados

```bash
git clone https://github.com/ARAVINDs2002/ContextChat-Context-Aware-Chatbot-for-Detail-Pages-Django-Ollama-.git

cd ContextChat-Context-Aware-Chatbot-for-Detail-Pages-Django-Ollama-

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

python -m django --version

python manage.py check

python manage.py makemigrations chatbot

python manage.py migrate

ollama list

ollama run qwen2.5:1.5b

python manage.py runserver 0.0.0.0:8000
```

---

# 16. Generación final de requirements.txt

El archivo final de dependencias debe generarse dentro del entorno virtual activado mediante:

```bash
pip freeze > requirements.txt
```

Esto permite registrar las versiones exactas de las librerías instaladas en el entorno utilizado para el proyecto.
