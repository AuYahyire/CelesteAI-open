# 🤖 CelesteAI - Bot Inteligente para Telegram

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)](https://openai.com)
[![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue.svg)](https://core.telegram.org/bots/api)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://mysql.com)

> **Bot avanzado para Telegram potenciado por OpenAI GPT-4, con gestión inteligente de conversaciones, integración de herramientas y sistema automatizado de recordatorios.**

## 🌟 Funcionalidades Clave

### 🧠 **Gestión Inteligente de Conversaciones**
- **Contexto Persistente**: Mantiene el historial de la conversación entre sesiones usando almacenamiento MySQL.
- **Soporte Multilingüe**: Detección automática de idioma y adaptación de respuestas.
- **Respuestas Contextuales**: Aprovecha los modelos avanzados de OpenAI para interacciones naturales.

### 🛠️ **Integración Avanzada de Herramientas**
- **Ejecución de Funciones**: Ejecución dinámica de herramientas mediante la API de function calling de OpenAI.
- **Sistema de Recordatorios**: Programación inteligente con soporte RRULE para eventos recurrentes.
- **Datos en Tiempo Real**: Consultas de fecha/hora actual con reconocimiento de zona horaria.
- **Traducción Inteligente**: Traducción bidireccional inglés-español con soporte para contenido en imágenes (restringido por defecto a administradores y usuarios angloparlantes, personalizable).
- **Arquitectura Extensible**: Registro de herramientas basado en plugins para facilitar la expansión de funcionalidades.

### 🔐 **Seguridad de Nivel Empresarial**
- **Autorización Multinivel**: Control de acceso basado en chat y usuario.
- **Gestión de Administradores**: Privilegios dedicados para usuarios administradores.
- **Saneamiento de Entradas**: Protección XSS y manejo seguro de datos.
- **Configuración por Entorno**: Gestión segura de credenciales.

### 🚀 **Infraestructura Lista para Producción**
- **Arquitectura Asíncrona**: FastAPI + asyncio para alto rendimiento.
- **Pooling de Conexiones a BBDD**: Conexiones MySQL optimizadas con reintentos automáticos.
- **Integración Webhook**: Gestión eficiente de webhooks de Telegram.
- **Monitorización de Salud**: Chequeos de salud integrados y registro exhaustivo de logs.
- **Despliegue en la Nube**: Preparado para Railway.app con configuración Procfile.

## 🏗️ Resumen de la Arquitectura

```
CelesteAI/
├── 🤖 bot/                     # Implementación principal del bot
│   ├── 🧠 core/               # Componentes esenciales
│   │   ├── config.py          # Gestión de entorno y configuración
│   │   ├── logger.py          # Sistema centralizado de logs
│   │   └── telegram_bot.py    # Inicialización del bot de Telegram
│   ├── 💾 db/                 # Capa de base de datos
│   │   └── models.py          # Modelos MySQL y pooling de conexiones
│   ├── 🎯 handlers/           # Manejadores de mensajes y eventos
│   │   ├── manejar_mensaje.py # Procesamiento principal de mensajes
│   │   ├── auth.py            # Lógica de autenticación
│   │   ├── help.py            # Sistema de ayuda
│   │   └── start.py           # Comandos de inicio del bot
│   ├── 🌐 routes/             # Rutas FastAPI
│   │   ├── webhook.py         # Endpoint de webhook de Telegram
│   │   └── recordatorios.py   # Sistema de programación de recordatorios
│   ├── 🤖 services/           # Servicios de lógica de negocio
│   │   └── OpenAI/            # Integración con OpenAI
│   │       ├── responder.py   # Orquestador principal de respuestas
│   │       ├── conversation.py # Gestión del estado conversacional
│   │       ├── openai.py      # Cliente de la API de OpenAI
│   │       ├── utils.py       # Funciones utilitarias
│   │       ├── tools/         # Herramientas para function calling
│   │       └── resources/     # Instrucciones IA y definiciones de herramientas
│   └── 🛠️ utils/              # Módulos utilitarios
│       └── image_utils.py     # Utilidades para procesamiento de imágenes
├── 🔧 tools/                  # Implementaciones de herramientas externas
│   └── funciones.py           # Funciones principales de herramientas
└── 📋 Archivos de Configuración
    ├── requirements.txt       # Dependencias de Python
    ├── .env.example          # Plantilla de variables de entorno
    ├── Procfile              # Configuración para Railway
    └── railway.json          # Configuración de servicio Railway
```

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.8+
- MySQL 8.0+
- Token de Bot de Telegram ([Crea uno](https://t.me/BotFather))
- Clave API de OpenAI ([Consigue la tuya](https://platform.openai.com/api-keys))

### 1. Configuración del Entorno
```bash
# Clona el repositorio
git clone <repository-url>
cd CelesteAI

# Crea un entorno virtual
python -m venv venv

# Activa el entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instala las dependencias
pip install -r requirements.txt
```

### 2. Configuración
```bash
# Copia la plantilla de entorno
copy .env.example .env

# Edita .env con tus credenciales
```

**Variables de Entorno Requeridas:**
```env
# Configuración de Telegram
TOKEN_TELEGRAM=tu_token_de_bot_telegram
BOT_USERNAME=tu_nombre_de_usuario_bot
CHAT_IDS_AUTORIZADOS=[123456789, 987654321]
ADMIN_USER_IDS=[123456789]
ANGLOPARLANTE_USER_IDS=[123456789]

# Configuración de OpenAI
OPENAI_API_KEY=tu_clave_api_openai
OPENAI_BASE_MODEL=gpt-4.1

# Configuración de Base de Datos
MYSQLHOST=localhost
MYSQLPORT=3306
MYSQLUSER=tu_usuario_db
MYSQLPASSWORD=tu_contraseña_db
MYSQL_DATABASE=celeste_db

# Configuración de la Aplicación
APP_NAME=CelesteAI
PORT=8000
```

### 3. Configuración de la Base de Datos
```sql
CREATE DATABASE celeste_db;
```

### 4. Lanzar la Aplicación
```bash
python main.py
```

La aplicación estará disponible en `http://localhost:8000`

## 🔧 Implementación Técnica

### **Sistema de Gestión de Conversaciones**
```python
class ConversationStateManager:
    """Gestiona el contexto persistente de la conversación entre sesiones de usuario"""
    
    def get_state(self, user_id: int) -> Tuple[str, int]:
        """Recupera el estado de la conversación desde MySQL"""
        
    def save_state(self, user_id: int, response_id: str, timestamp: int):
        """Guarda el estado de la conversación para mantener el contexto"""
```

### **Arquitectura de Integración de Herramientas**
```python
class ToolDispatcher:
    """Sistema de ejecución dinámica de herramientas con patrón de registro"""
    
    def execute(self, name: str, args: dict):
        """Ejecuta herramientas registradas con tipado seguro"""
        
    def _registry = {
        "guardar_recordatorio": self._guardar_recordatorio,
        "consultar_fecha_hora_actual": self._consultar_fecha_hora_actual,
    }
```

### **Sistema Avanzado de Recordatorios**
- **Soporte RRULE**: Eventos recurrentes compatibles con RFC 5545.
- **Reconocimiento de Zona Horaria**: Por defecto Venezuela/Caracas porque eran mis usuarios finales, pero configurable.
- **Procesamiento Asíncrono**: Entrega de recordatorios sin bloqueo.
- **Optimización de Base de Datos**: Consultas indexadas para mayor rendimiento.

### **Características de Seguridad**
- **Saneamiento de Entradas**: Escape de HTML y prevención de XSS.
- **Protección contra Path Traversal**: Operaciones de archivos seguras.
- **Capas de Autorización**: Control de acceso multinivel, por categorías de Telegram o personalizadas.
- **Aislamiento de Entorno**: Gestión segura de credenciales.

## 📊 Rendimiento y Escalabilidad

### **Optimización de Base de Datos**
- **Pooling de Conexiones**: Pool de conexiones MySQL (5 conexiones).
- **Consultas Indexadas**: Búsquedas optimizadas de recordatorios y conversaciones.
- **Limpieza Automática**: Gestión del estado conversacional.

### **Arquitectura Asíncrona**
- **FastAPI**: Framework web asíncrono de alto rendimiento.
- **Procesamiento Concurrente**: Operaciones I/O no bloqueantes.
- **Tareas en Segundo Plano**: Programación automática de recordatorios.

### **Gestión de Recursos**
- **Optimización de Memoria**: Reutilización eficiente de conexiones.
- **Recuperación ante Errores**: Manejo robusto de excepciones.
- **Sistema de Logs**: Monitorización y depuración exhaustivas.

## 🛡️ Buenas Prácticas de Seguridad

### **Protección de Datos**
- ✅ Gestión de secretos basada en entorno
- ✅ Validación y saneamiento de entradas
- ✅ Prevención de inyección SQL
- ✅ Protección XSS
- ✅ Mitigación de path traversal

### **Control de Acceso**
- ✅ Sistema de autorización multinivel
- ✅ Separación de privilegios de administrador
- ✅ Restricciones de acceso por chat
- ✅ Validación de identificación de usuario

## 🚀 Despliegue

### **Despliegue en Railway.app (ejemplo básico)**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100
  }
}
```

### **Configuración de Variables de Entorno**
Toda la configuración sensible se gestiona mediante variables de entorno.

## 🔮 Funcionalidades Avanzadas

### **Inteligencia Multilingüe**
- Detección automática de idioma
- Generación de respuestas contextuales
- **Traducción con Visión Artificial**: Los comandos `/translate` y `/traducir` procesan tanto texto como imágenes usando los modelos de visión de OpenAI.
- **Acceso por Roles**: Funciones de traducción restringidas a grupos de administradores y usuarios angloparlantes.
- Adaptación cultural para distintos grupos de usuarios

### **Sistema Extensible de Herramientas**
- Arquitectura de plugins para nuevas herramientas
- Ejecución de funciones con tipado seguro
- Registro automático de herramientas

### **Flujo de Conversación Inteligente**
- Conservación de contexto entre sesiones
- Enrutamiento inteligente de respuestas
- Mecanismos de recuperación ante errores y fallback

## 📈 Monitorización y Analítica

### **Registro Exhaustivo de Logs**
- Seguimiento de peticiones/respuestas
- Métricas de rendimiento
- Monitorización de errores
- Analítica de interacción de usuarios

### **Monitorización de Salud**
- Endpoints de salud de la aplicación
- Estado de conexión a la base de datos
- Chequeos de disponibilidad del servicio

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Sin embargo, ten en cuenta las siguientes directrices:

Este bot fue creado originalmente para uso privado y ahora se publica principalmente como ejemplo de buenas prácticas y arquitectura avanzada en Python. **No** está pensado actualmente como un proyecto comunitario con soporte activo o desarrollo continuo. Sin embargo, si crees que debería convertirse en un proyecto colaborativo, siéntete libre de argumentarlo si consideras que merece crecer como proyecto abierto.

- **Pull Requests:**  
  Si quieres aportar un parche, mejora o nueva funcionalidad, puedes enviar un Pull Request. Revisaré los PR cuando sea posible y los fusionaré si cumplen los estándares de calidad y coherencia del proyecto.

- **Issues:**  
  No se ofrece soporte personalizado, y no se garantiza respuesta a incidencias o preguntas. Si encuentras un bug importante, puedes abrir una issue, pero entiende que los tiempos de respuesta o solución no están garantizados. Para mejoras o sugerencias, se prefiere el envío de un PR.

- **Otras formas de contribuir:**  
  Actualmente no se aceptan propuestas vía Wiki, Discussions ni contribuciones a la documentación.

## 🙋 Soporte

Este proyecto lo mantengo como un portafolio personal de buenas prácticas y arquitectura avanzada en Python. No existe un canal formal de soporte.  
Sin embargo, te animo a explorar el código, aprender de él y adaptarlo a tus propios proyectos.

## 📄 Licencia

Este proyecto está bajo licencia MIT – consulta el archivo [LICENSE](LICENSE) para más detalles.

## 🔗 Tecnologías Utilizadas

- **Backend:** Python 3.8+, FastAPI, asyncio  
- **IA/ML:** OpenAI GPT-4, Function Calling API  
- **Base de Datos:** MySQL 8.0+, Pooling de conexiones  
- **Mensajería:** Telegram Bot API, Webhooks  
- **Despliegue:** Railway.app, Docker-ready  
- **Seguridad:** Configuración por entorno, saneamiento de entradas  
- **Monitorización:** Logging estructurado, chequeos de salud  

---

**Hecho con ❤️ para ayudar a quienes lo necesitan**