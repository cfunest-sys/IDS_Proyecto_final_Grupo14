# Plataforma de Administración y Control de un Curso Universitario
### Proyecto Final Integrador — Introducción al Desarrollo de Software (IDS)
### Facultad de Ingeniería, Universidad de Buenos Aires (FIUBA)

---

## Integrantes — Equipo: Artemis 3

* **Julieta Paola Fernández** - Padrón: 115660
* **Celeste Abigail Funes Taya** - Padrón: 115585
* **Joaquín Tapia Castañeda** - Padrón: 114342
* **Nicolás Pattini** - Padrón: 114947
* **Iván Nahuel Avillo Llanos** - Padrón: 112713
* **Lucas Calahuana** - Padrón: 114651
* **Lucca Moyano** - Padrón: 113987
* **Luna Abril Alonso Díaz** - Padrón: 115439
* **David García** - Padrón: 115695

**Tutor asignado:** Tommy Villegas

---

## Alcance del Proyecto (Etapa inicial)

Desarrollo e implementacicón de la **Plataforma Web de Gestión y Administración del Curso Universitario**, priorizando de manera absoluta el **Módulo de Administración por parte del Cuerpo Docente**. 

---

## Requisitos Previos

- **Docker** (≥ 24.0)
- **Docker Compose** (≥ 2.20, incluido con Docker Desktop / Docker Engine)

El proyecto se ejecuta completamente containerizado. No es necesario instalar Python ni MySQL en el host.

---

## Cómo ejecutar el proyecto

1. Clonar el repositorio y acceder al directorio raíz del proyecto:

   ```bash
   git clone git@github.com:cfunest-sys/IDS_Proyecto_final_Grupo14.git
   ```


2. (Opcional) Revisar las variables de entorno en `app_backend/.env.example` y, si es necesario, crear `app_backend/.env` con los valores deseados.  
   Los valores por defecto del `docker-compose.yml` son suficientes para desarrollo.

3. Levantar los servicios con Docker Compose:

   ```bash
   docker compose up -d
   ```

   Esto construye las imágenes y levanta tres servicios:

   | Servicio  | Puerto  | Descripción                    |
   |-----------|---------|--------------------------------|
   | `db`      | `3306`  | Base de datos MySQL 8.0        |
   | `backend` | `5001`  | API RESTful del backend        |
   | `frontend`| `8080`  | Interfaz web de administración |

4. Una vez que los servicios estén levantados, acceder a:

   - **Frontend:** [http://localhost:8080](http://localhost:8080)
   - **Backend (API):** [http://localhost:5001](http://localhost:5001)
   - **Ejemplo de endpoint:** `http://localhost:5001/api/alumnos/`

5. Para detener los servicios:

   ```bash
   docker compose down
   ```

   Para detener y eliminar volúmenes (base de datos y archivos subidos):

   ```bash
   docker compose down -v
   ```

---

## Estructura de Carpetas del Repositorio

La arquitectura del sistema mantiene una separación entre la API lógica de backend y la interfaz de frontend:

```text
├── app_backend/
│   ├── data/
│   │   ├── db_init.sql           # Esquema SQL de la base de datos
│   │   └── queries.py            # Consultas SQL reutilizables
│   ├── database/
│   │   └── db.py                 # Conexión y pool hacia MySQL
│   ├── routes/
│   │   ├── alumnos.py            # Endpoints para gestión de alumnos y CSV
│   │   ├── auth.py               # Autenticación y registro
│   │   ├── dashboard.py          # Dashboard del backend
│   │   ├── equipos.py            # Gestión de equipos
│   │   ├── evaluaciones.py       # Evaluaciones y exámenes
│   │   ├── login.py              # Inicio de sesión
│   │   ├── materiales.py         # Material de estudio
│   │   ├── notas.py              # Notas y calificaciones
│   │   ├── perfil.py             # Perfil de usuario
│   │   ├── profesores.py         # Administración de cursos
│   │   ├── registro_asistencia.py # Registro de asistencia
│   │   └── reportes.py           # Reportes y estadísticas
│   ├── utils/
│   │   └── auth.py               # Utilidades JWT
│   ├── uploads/
│   │   └── materiales/           # Archivos subidos por los profesores
│   ├── .env                      # Variables de entorno (no versionar configurarlo antes con el .example)
│   ├── .env.example              # Ejemplo de variables de entorno
│   ├── app.py                    # Inicialización del backend Flask
│   ├── config.py                 # Configuración (DB, JWT)
│   └── Dockerfile                # Imagen Docker del backend
├── app_frontend/
│   ├── routes/
│   │   ├── routes.py             # Rutas principales
│   │   ├── dashboard_profesor.py # Dashboard del profesor
│   │   ├── equipos.py            # Gestión de equipos
│   │   ├── evaluaciones.py       # Evaluaciones
│   │   ├── notas.py              # Notas
│   │   └── perfil.py             # Perfil
│   ├── static/
│   │   ├── images/
│   │   │   ├── background.jpeg   # Fondo (edificio de Paseo Colón)
│   │   │   └── logo.png          # Logo de la FIUBA
│   │   ├── script.js             # Interactividad del lado del cliente
│   │   └── styles.css            # Estilos del panel de administración
│   ├── templates/                # 20 templates HTML (Jinja2)
│   │   ├── 404.html
│   │   ├── alumnos.html
│   │   ├── asistencia.html
│   │   ├── base.html
│   │   ├── calendario.html
│   │   ├── dashboard_profesor.html
│   │   ├── equipos.html
│   │   ├── evaluaciones.html
│   │   ├── inicio.html
│   │   ├── login.html
│   │   ├── materiales_alumno.html
│   │   ├── materiales_profesor.html
│   │   ├── navbar.html
│   │   ├── notas.html
│   │   ├── perfil_alumno.html
│   │   ├── perfil_profesor.html
│   │   ├── prueba.html
│   │   ├── registro-asistencia.html
│   │   ├── registro.html
│   │   └── reportes.html
│   ├── app.py                    # Inicialización del frontend Flask
│   └── Dockerfile                # Imagen Docker del frontend
├── .gitignore                    # Exclusión de archivos del entorno virtual y temporales
├── docker-compose.yml            # configuracion para levantar los servicios (DB, backend, frontend)
├── README.md                     # Documentación técnica del sistema (este archivo)
└── requirements.txt              # Dependencias del proyecto de Python
