CREATE DATABASE IF NOT EXISTS data_base;
USE data_base;
SET FOREIGN_KEY_CHECKS = 0; -- Deshabilitar temporalmente las comprobaciones de claves foráneas para evitar errores de tablas
DROP TABLE IF EXISTS miembros_equipo;
DROP TABLE IF EXISTS equipos;
DROP TABLE IF EXISTS evaluaciones;
DROP TABLE IF EXISTS notas;
DROP TABLE IF EXISTS profesor_curso;
DROP TABLE IF EXISTS password_reset_tokens;
DROP TABLE IF EXISTS alumnos;
DROP TABLE IF EXISTS profesores;
DROP TABLE IF EXISTS cursos;
DROP TABLE IF EXISTS usuarios;
CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY AUTO_INCREMENT,
    email TEXT NOT NULL,
    contrasenia TEXT NOT NULL,
    rol TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
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
    legajo INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    estado TEXT NOT NULL,
    id_usuario INTEGER,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
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
    FOREIGN KEY (id_curso) REFERENCES cursos(id_curso)
);
CREATE TABLE cursos (
    id_curso INTEGER PRIMARY KEY AUTO_INCREMENT,
    nombre TEXT NOT NULL,
    anio INTEGER NOT NULL,
    semestre INTEGER NOT NULL
);
CREATE TABLE evaluaciones (
    id_evaluacion INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL,
    id_curso INT NOT NULL,
    FOREIGN KEY (id_curso) REFERENCES cursos(id_curso)
);
CREATE TABLE notas (
    id_nota INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    legajo_alumno INT NOT NULL,
    id_evaluacion INT NOT NULL,
    nota DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (legajo_alumno) REFERENCES alumnos(legajo),
    FOREIGN KEY (id_evaluacion) REFERENCES evaluaciones(id_evaluacion)
);
CREATE TABLE equipos (
    id_equipo INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nombre_equipo VARCHAR(255) NOT NULL,
    id_curso INT NOT NULL,

    INDEX (id_curso),
    FOREIGN KEY (id_curso) REFERENCES cursos (id_curso)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE miembros_equipo (
    id_miembro INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_equipo INT NOT NULL,
    legajo_alumno INT NOT NULL,
    FOREIGN KEY (id_equipo) REFERENCES equipos(id_equipo) ON DELETE CASCADE,
    FOREIGN KEY (legajo_alumno) REFERENCES alumnos(legajo),
    UNIQUE(id_equipo, legajo_alumno)
) ENGINE=InnoDB;
INSERT INTO usuarios (email, contrasenia, rol)
VALUES
 ('admin@example.com', 'scrypt:32768:8:1$Hid9QZTkQuxvOQsc$75db4c395ec522e9159b5e58cf012086b1f51e05388e72c4a898b9b76ec8ace4fb08590a30e9a3ce04acb71b6e633462d1773c1e8aed8ed6112bd5a0a7f3e0a8', 'admin'),
 ('profesor@example.com', 'scrypt:32768:8:1$8DIUDP0hWtiGIYf5$dfa9cafbc33ae053c7ec1aa3e680074e0f8fb6a220fc7ba763c063c3b36dce8a6ab3a71f3ab9d375b1766402c2a54d61228070f531dcbaa2cd5fa89b76ac355d', 'profesor'),
 ('alumno@example.com', 'scrypt:32768:8:1$CJT3ez7XdwNDV3oS$f86dd776ceaa5b38df2ccd16164b3e6f50dd3fc76bc951b353ac9316283e57e59ece0079bc76eeb98290e8a04ba95d0428e87632dfb39b6c43cd5525ff6536cc', 'alumno'),
 ('JuanPerez@gmail.com', 'scrypt:32768:8:1$xVqTD27xuA95I8wt$51965ef800581032c12342c890ecdff213d189e043a57b8fb7485cd10e6b40fc31c880cd42cf05c6ddb5df14545648e173793d4478825f65af12669a8593427c', 'profesor');
INSERT INTO profesores (nombre, departamento, id_usuario)
VALUES
 ('Dr. Smith', 'Matemáticas', 2),
 ('juan', 'intro DS', 4 );

INSERT INTO alumnos (legajo, nombre, estado, id_usuario)
VALUES
 (115598, 'Juan Pérez', 'activo', 3);
INSERT INTO cursos (nombre, anio, semestre)
VALUES
 ('Introducción al Desarrollo', 2024, 1),
 ('Fundamentos de Programación', 2024, 2);
INSERT INTO evaluaciones (nombre, tipo, fecha, id_curso)
VALUES 
    ('Primer Parcial Teórico-Práctico', 'parcial', '2026-05-20', 1),
    ('Trabajo Práctico Integrador Final', 'TP', '2026-06-17', 1),
    ('Control de Lectura - Parcialito 1', 'parcialito', '2026-05-13', 2);
INSERT INTO notas (legajo_alumno, id_evaluacion, nota)
VALUES
    (115598, 1, 8.5),
    (115598, 2, 9.0),
    (115598, 3, 7.5);
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
SET FOREIGN_KEY_CHECKS = 1;  -- Restaurar la verificación de claves foráneas
