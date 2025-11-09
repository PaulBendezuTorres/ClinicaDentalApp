-- Crea la base de datos (opcional)
CREATE DATABASE clinica_dental CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE clinica_dental;

DROP TABLE IF EXISTS citas;
DROP TABLE IF EXISTS horarios_dentistas;
DROP TABLE IF EXISTS consultorios;
DROP TABLE IF EXISTS tratamientos;
DROP TABLE IF EXISTS dentistas;
DROP TABLE IF EXISTS pacientes;

CREATE TABLE pacientes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(120) NOT NULL,
  telefono VARCHAR(40) NOT NULL
);

CREATE TABLE dentistas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(120) NOT NULL,
  especialidad VARCHAR(120) NOT NULL
);

CREATE TABLE consultorios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre_sala VARCHAR(80) NOT NULL,
  equipo_especial TINYINT(1) NOT NULL DEFAULT 0
);

CREATE TABLE horarios_dentistas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  dentista_id INT NOT NULL,
  dia_semana ENUM('lunes','martes','miercoles','jueves','viernes','sabado','domingo') NOT NULL,
  hora_inicio TIME NOT NULL,
  hora_fin TIME NOT NULL,
  FOREIGN KEY (dentista_id) REFERENCES dentistas(id) ON DELETE CASCADE
);

CREATE TABLE tratamientos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(120) NOT NULL,
  duracion_minutos INT NOT NULL,
  costo DECIMAL(10,2) NOT NULL,
  requiere_equipo_especial TINYINT(1) NOT NULL DEFAULT 0
);

CREATE TABLE citas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  paciente_id INT NOT NULL,
  dentista_id INT NOT NULL,
  consultorio_id INT NOT NULL,
  tratamiento_id INT NOT NULL,
  fecha DATE NOT NULL,
  hora_inicio TIME NOT NULL,
  FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
  FOREIGN KEY (dentista_id) REFERENCES dentistas(id),
  FOREIGN KEY (consultorio_id) REFERENCES consultorios(id),
  FOREIGN KEY (tratamiento_id) REFERENCES tratamientos(id),
  UNIQUE KEY uk_dentista_fecha_hora (dentista_id, fecha, hora_inicio)
);

-- Datos de ejemplo mínimos
INSERT INTO pacientes(nombre, telefono) VALUES
('Ana Rojas','999-111-222'), ('Luis Pérez','999-222-333');

INSERT INTO dentistas(nombre, especialidad) VALUES
('Dr. Sáenz','Endodoncia'), ('Dra. Rivera','Ortodoncia');

INSERT INTO consultorios(nombre_sala, equipo_especial) VALUES
('Sala 1', 0), ('Sala 2', 1);

INSERT INTO tratamientos(nombre, duracion_minutos, costo, requiere_equipo_especial) VALUES
('Limpieza', 30, 80.00, 0),
('Endodoncia', 90, 450.00, 1);

INSERT INTO horarios_dentistas(dentista_id, dia_semana, hora_inicio, hora_fin) VALUES
(1, 'lunes', '09:00', '17:00'),
(1, 'martes', '09:00', '17:00'),
(2, 'lunes', '10:00', '18:00');
