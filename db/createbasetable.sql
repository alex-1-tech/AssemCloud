CREATE DATABASE assembler_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE machine (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE assembly (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    machine_id INT NOT NULL,
    parent_assembly_id INT DEFAULT NULL,
    FOREIGN KEY (machine_id) REFERENCES machine(id),
    FOREIGN KEY (parent_assembly_id) REFERENCES assembly(id)
);

CREATE TABLE part (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    assembly_id INT NOT NULL,
    FOREIGN KEY (assembly_id) REFERENCES assembly(id)
);