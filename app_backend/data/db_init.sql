CREATE DATABASE IF NOT EXISTS data_base;
USE data_base;

DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS password_reset_tokens;
DROP TABLE IF EXISTS alumnos;
DROP TABLE IF EXISTS profesores;
DROP TABLE IF EXISTS cursos;
DROP TABLE IF EXISTS logs;
DROP TABLE IF EXISTS parciales;
DROP TABLE IF EXISTS equipos;

CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    contrasenia VARCHAR(255) NOT NULL,
    rol TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
);

CREATE TABLE password_reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    token TEXT NOT NULL UNIQUE,
    usado BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE alumnos (
    legajo INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    estado TEXT NOT NULL,
    id_usuario INTEGER,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE profesores (
    id_profesor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    departamento TEXT NOT NULL,
    id_usuario INTEGER,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE cursos (
    id_curso INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    anio INTEGER NOT NULL,
    semestre INTEGER NOT NULL,
    id_profesor INT NOT NULL,
);

CREATE TABLE parciales (
    id_parcial INT NOT NULL PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(255) NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL,
    id_curso INT NOT NULL,
);

CREATE TABLE equipos (
    id INT NOT NULL PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(255) NOT NULL,
    id_curso INT NOT NULL,

    INDEX (id_curso),
    FOREIGN KEY (id_curso) REFERENCES cursos (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO usuarios (email, contrasenia, rol) 
VALUES
 ('admin@example.com', 'admin123', 'admin'),
 ('profesor@example.com', 'profesor123', 'profesor'),
 ('alumno@example.com', 'alumno123', 'alumno');

INSERT INTO profesores (nombre, departamento, id_usuario)
VALUES
 ('Dr. Smith', 'Matemáticas', 2);

INSERT INTO alumnos (nombre, estado, id_usuario)
VALUES
 ('Juan Pérez', 'activo', 3);

INSERT INTO cursos (nombre, anio, semestre)
VALUES
 ('Introducción al Desarrollo', 2024, 1, 1),
 ('Fundamentos de Programación', 2024, 2, 2);

INSERT INTO evaluaciones (nombre, tipo, fecha, id_curso)
VALUES 
    ('Primer Parcial Teórico-Práctico', 'parcial', '2026-05-20', 1),
    ('Trabajo Práctico Integrador Final', 'TP', '2026-06-17', 1),
    ('Control de Lectura - Parcialito 1', 'parcialito', '2026-05-13', 2);

INSERT INTO equipos (nombre, curso_id)
VALUES 
    ('Equipo Artemis 3', 1),
    ('Equipo Backend Masters', 1),
    ('Equipo Gastronómico Control', 2);
