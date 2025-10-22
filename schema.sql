-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS db_academica;
USE db_academica;

-- Crear la tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
  idUsuario INT(10) AUTO_INCREMENT PRIMARY KEY,
  usuario CHAR(35) NOT NULL,
  clave CHAR(35) NOT NULL,
  nombre CHAR(85) NOT NULL,
  direccion CHAR(100),
  telefono CHAR(9)
);

-