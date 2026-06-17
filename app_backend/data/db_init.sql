CREATE DATABASE IF NOT EXISTS data_base;
USE data_base;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS miembros_equipo;
DROP TABLE IF EXISTS logs_login;
DROP TABLE IF EXISTS materiales;
DROP TABLE IF EXISTS equipos;
DROP TABLE IF EXISTS evaluaciones;
DROP TABLE IF EXISTS notas;
DROP TABLE IF EXISTS profesor_curso;
DROP TABLE IF EXISTS password_reset_tokens;
DROP TABLE IF EXISTS alumnos;
DROP TABLE IF EXISTS profesores;
DROP TABLE IF EXISTS cursos;
DROP TABLE IF EXISTS evaluaciones;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS temas;
DROP TABLE IF EXISTS qr_asistencia;
DROP TABLE IF EXISTS asistencia;


CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    contrasenia TEXT NOT NULL,
    rol TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
CREATE TABLE logs_login(
    id_log INTEGER PRIMARY KEY AUTO_INCREMENT,
    id_usuario INTEGER,
    email TEXT NOT NULL,
    resultado TEXT NOT NULL,
    ip TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);
CREATE TABLE password_reset_tokens (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    id_usuario INTEGER NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    usado BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);
CREATE TABLE alumnos (
    legajo INTEGER PRIMARY KEY AUTO_INCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    dni VARCHAR(20) NOT NULL UNIQUE,
    email TEXT,
    curso int NOT NULL,
    anio INTEGER,
    cuatrimestre INTEGER, 
    estado TEXT NOT NULL,
    id_usuario INTEGER,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (curso) REFERENCES cursos(id_curso)
);
CREATE TABLE profesores (
    id_profesor INTEGER PRIMARY KEY AUTO_INCREMENT,
    nombre TEXT NOT NULL,
    departamento TEXT NOT NULL,
    id_usuario INTEGER,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);
CREATE TABLE profesor_curso (
    id_profesor_curso INTEGER PRIMARY KEY AUTO_INCREMENT,
    id_profesor INTEGER NOT NULL,
    id_curso INTEGER NOT NULL,
    FOREIGN KEY (id_profesor) REFERENCES profesores(id_profesor),
    FOREIGN KEY (id_curso) REFERENCES cursos(id_curso) ON DELETE CASCADE
);
CREATE TABLE cursos (
    id_curso INTEGER PRIMARY KEY AUTO_INCREMENT,
    anio INTEGER NOT NULL,
    cuatrimestre INTEGER NOT NULL
);
CREATE TABLE evaluaciones (
    id_evaluacion INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL,
    id_curso INT NOT NULL,
    FOREIGN KEY (id_curso) REFERENCES cursos(id_curso) ON DELETE CASCADE
);

CREATE TABLE notas (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    legajo_alumno INT NOT NULL,
    id_evaluacion INT NOT NULL,
    calificacion DECIMAL(4,2) NOT NULL,
    fecha DATE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_notas_alumno_id (legajo_alumno),
    INDEX idx_notas_evaluacion_id (id_evaluacion),

    CONSTRAINT unique_alumno_evaluacion UNIQUE (legajo_alumno, id_evaluacion),
    CONSTRAINT chk_calificacion_range CHECK (calificacion >= 0 AND calificacion <= 10),

    FOREIGN KEY (legajo_alumno) REFERENCES alumnos(legajo),
    FOREIGN KEY (id_evaluacion) REFERENCES evaluaciones(id_evaluacion)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE equipos (
    id_equipo INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nombre_equipo VARCHAR(255) NOT NULL,
    id_curso INT NOT NULL,

    INDEX (id_curso),
    FOREIGN KEY (id_curso) REFERENCES cursos (id_curso) 
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE miembros_equipo (
    id_miembro INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_equipo INT NOT NULL,
    legajo_alumno INT NOT NULL,
    FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo) ON DELETE CASCADE,
    FOREIGN KEY (legajo_alumno) REFERENCES alumnos(legajo),
    UNIQUE(id_equipo, legajo_alumno)
) ENGINE=InnoDB;
CREATE TABLE materiales(
  id_material INT AUTO_INCREMENT PRIMARY KEY,
    id_curso INT NOT NULL,
    id_profesor INT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    tipo_material ENUM(
        'apunte',
        'guia',
        'video',
        'imagen',
        'documento',
        'archivo',
        'bibliografia',
        'otro'
    ) NOT NULL,
    tema VARCHAR(100),
    orden_material INT DEFAULT 0,
    archivo_ruta VARCHAR(500) NOT NULL,
    es_externo BOOLEAN DEFAULT FALSE,
    tipo_archivo VARCHAR(50),
    tamano_bytes BIGINT,
    fecha_material DATE,
    es_libre BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE,
    estado ENUM(
        'borrador',
        'publicado',
        'archivado',
        'programado'
    ) DEFAULT 'publicado',
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_curso)
        REFERENCES cursos(id_curso)
        ON DELETE CASCADE,
    FOREIGN KEY (id_profesor)
        REFERENCES profesores(id_profesor)
        ON DELETE RESTRICT,
    INDEX idx_curso (id_curso),
    INDEX idx_profesor (id_profesor),
    INDEX idx_tema (tema),
    INDEX idx_tipo (tipo_material),
    INDEX idx_curso_tipo (id_curso, tipo_material)
);
CREATE TABLE temas (
    id_tema INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    id_curso INT NOT NULL,
    orden INT DEFAULT 0,
    FOREIGN KEY (id_curso) REFERENCES cursos(id_curso) ON DELETE CASCADE,
    UNIQUE KEY unique_tema_curso (nombre, id_curso)
);
CREATE TABLE qr_asistencia (
    id_qr INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(255) NOT NULL,
    fecha_generacion DATETIME NOT NULL,
    expiracion DATETIME NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);
CREATE TABLE asistencia (
    id_asistencia INT AUTO_INCREMENT PRIMARY KEY,
    alumno_legajo INT NOT NULL,
    qr_id INT NOT NULL,
    fecha DATE NOT NULL,
    registrado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alumno_legajo) REFERENCES alumnos(legajo),
    FOREIGN KEY (qr_id) REFERENCES qr_asistencia(id_qr)
);



INSERT INTO usuarios (email, contrasenia, rol)
VALUES
 ('admin@example.com', 'scrypt:32768:8:1$Hid9QZTkQuxvOQsc$75db4c395ec522e9159b5e58cf012086b1f51e05388e72c4a898b9b76ec8ace4fb08590a30e9a3ce04acb71b6e633462d1773c1e8aed8ed6112bd5a0a7f3e0a8', 'admin'), -- Contraseña: admin123
 ('profesor@example.com', 'scrypt:32768:8:1$8DIUDP0hWtiGIYf5$dfa9cafbc33ae053c7ec1aa3e680074e0f8fb6a220fc7ba763c063c3b36dce8a6ab3a71f3ab9d375b1766402c2a54d61228070f531dcbaa2cd5fa89b76ac355d', 'profesor'),
 ('alumno@example.com', 'scrypt:32768:8:1$CJT3ez7XdwNDV3oS$f86dd776ceaa5b38df2ccd16164b3e6f50dd3fc76bc951b353ac9316283e57e59ece0079bc76eeb98290e8a04ba95d0428e87632dfb39b6c43cd5525ff6536cc', 'alumno'),
 ('JuanPerez@gmail.com', 'scrypt:32768:8:1$xVqTD27xuA95I8wt$51965ef800581032c12342c890ecdff213d189e043a57b8fb7485cd10e6b40fc31c880cd42cf05c6ddb5df14545648e173793d4478825f65af12669a8593427c', 'profesor');
 
INSERT INTO profesores (nombre, departamento, id_usuario)
VALUES
 ('Dr. Smith', 'Matemáticas', 2),
 ('juan', 'intro DS', 4 );

INSERT INTO alumnos (
    legajo,
    nombre,
    apellido,
    dni,
    curso,
    anio,
    cuatrimestre,
    estado,
    id_usuario
)
VALUES (
    115598,
    'Juan',
    'Pérez',
    '40123456',
    1,
    2025,
    1,
    'activo',
    3
);
INSERT INTO cursos (anio, cuatrimestre)
VALUES
 (2024, 1),
 (2024, 2);

INSERT INTO evaluaciones (nombre, tipo, fecha, id_curso)
VALUES 
    ('Primer Parcial Teórico-Práctico', 'parcial', '2026-05-20', 1),
    ('Trabajo Práctico Integrador Final', 'TP', '2026-06-17', 1),
    ('Control de Lectura - Parcialito 1', 'parcialito', '2026-05-13', 2);

INSERT INTO notas (legajo_alumno, id_evaluacion, calificacion, fecha)
VALUES
    (115598, 1, 8.5, CURDATE()),
    (115598, 2, 9.0, CURDATE()),
    (115598, 3, 7.5, CURDATE());

INSERT INTO equipos (nombre_equipo, id_curso)
VALUES 
    ('Equipo Artemis 3', 1),
    ('Equipo Backend Masters', 1),
    ('Equipo Gastronómico Control', 2);

INSERT INTO miembros_equipo (id_equipo, legajo_alumno)
VALUES
    (1, 115598);
INSERT INTO profesor_curso (id_profesor, id_curso)
VALUES
 (2, 1),
 (2, 2),
 (1, 1);
SET FOREIGN_KEY_CHECKS = 1;
