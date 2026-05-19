CREATE DATABASE IF NOT EXISTS data_base;
USE data_base;

DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS alumnos;
DROP TABLE IF EXISTS profesores;
DROP TABLE IF EXISTS cursos;


CREATE TABLE usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    contraseña TEXT NOT NULL,
    rol TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
);

INSERT INTO usuarios (email, contraseña, rol) 
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
 ('Introducción al Desarrollo', 2024, 1),
 ('Fundamentos de Programación', 2024, 2);