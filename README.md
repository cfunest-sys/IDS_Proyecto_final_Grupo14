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

## Estructura de Carpetas del Repositorio

La arquitectura del sistema mantiene una separación estricta entre la API lógica de backend y la interfaz de gestión de frontend:

```text
├── app_backend/
│   ├── data/
│   │   ├── db_init.sql          # Esquema SQL de base de datos centrado en la administración del curso
│   │   └── queries.py           # Consultas SQL reutilizables para la lógica de datos administrativos
│   ├── database/
│   │   └── db.py                # Conexión y configuración del pool hacia MySQL
│   ├── routes/
│   │   ├── alumnos.py           # Endpoints de la API para la gestión docente sobre el padrón de alumnos y CSV
│   │   └── profesores.py        # Endpoints de la API para la administración de evaluaciones y cursos
│   └── app.py                   # Inicialización y arranque del servidor Backend Flask
│
├── app_frontend/
│   ├── routes/
│   │   └── routes.py            # Enrutamiento de la interfaz de gestión y consumo de la API RESTful
│   ├── static/
│   │   ├── images/
│   │   │   ├── background.jpeg  # Fondo con imagen del edificio de Paseo Colón a incluir en los templates.
│   │   │   └── logo.png         # Logo de la FIUBA a incluir en los templates.
│   │   ├── script.js            # Interactividad y validaciones del lado del cliente (JavaScript Vanilla)
│   │   └── styles.css           # Hoja de estilos del panel de administración (CSS/Bootstrap)
│   ├── templates/
│   │   └── inicio.html          # Template base y vistas de los paneles de control de la cátedra
│   └── app.py                   # Inicialización del servidor de Frontend (Flask + Jinja2)
│
├── .gitignore                   # Exclusión de archivos del entorno virtual y temporales
├── README.md                    # Documentación técnica del sistema (este archivo)
└── requirements.txt             # Dependencias del proyecto de Python
