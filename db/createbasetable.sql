DROP DATABASE IF EXISTS assembler_db;
CREATE DATABASE assembler_db;
USE assembler_db;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE, -- validate email format at application level
    phone VARCHAR(30),         -- validate phone format (e.g., E.164) at application level
    address TEXT
);

CREATE TABLE roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL
);

CREATE TABLE user_roles (
    user_id INT,
    role_id INT,
    role_description TEXT,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE clients (
    client_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    phone VARCHAR(30) -- validate phone format at application level
);

CREATE TABLE manufacturers (
    manufacturer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    language VARCHAR(50),
    phone VARCHAR(30) -- validate phone format at application level
);

CREATE TABLE blueprints (
    blueprint_id INT AUTO_INCREMENT PRIMARY KEY,
    weight DECIMAL(10,2),
    scale VARCHAR(50),
    version VARCHAR(50),
    naming_scheme VARCHAR(100),
    developer_id INT,
    validator_id INT,
    lead_designer_id INT,
    chief_designer_id INT,
    approver_id INT,
    manufacturer_id INT,
    file_path TEXT,
    step TEXT,
    FOREIGN KEY (developer_id) REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (validator_id) REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (lead_designer_id) REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (chief_designer_id) REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (approver_id) REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(manufacturer_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE machines (
    machine_id INT AUTO_INCREMENT PRIMARY KEY,
    machine_name VARCHAR(255) NOT NULL,
    version VARCHAR(50)
);

CREATE TABLE machine_clients (
    client_id INT,
    machine_id INT,
    PRIMARY KEY (client_id, machine_id),
    FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE modules (
    module_id INT AUTO_INCREMENT PRIMARY KEY,
    machine_id INT,
    blueprint_id INT NOT NULL UNIQUE,
    decimal_number VARCHAR(100) UNIQUE,
    serial_number VARCHAR(100),
    name VARCHAR(255),
    parent_module_id INT,
    version VARCHAR(50),
    description TEXT,    
    assembly_status ENUM('in_progress', 'completed', 'cancelled') DEFAULT 'in_progress',
    
    created_on DATETIME NOT NULL,
    updated_on DATETIME,
    created_by INT,
    updated_by INT,
    
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (parent_module_id) REFERENCES modules(module_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (blueprint_id) REFERENCES blueprints(blueprint_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE part_manufacture (
    description_part_id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer_id INT,
    part_description TEXT,
    material VARCHAR(100),
    manufacture_date DATE,
    
    created_on DATETIME NOT NULL,
    updated_on DATETIME,
    created_by INT,
    updated_by INT,

    FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(manufacturer_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE parts (
    part_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL, 
    description_part_id INT,
    
    created_on DATETIME NOT NULL,
    updated_on DATETIME,
    created_by INT,
    updated_by INT,
    
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (description_part_id) REFERENCES part_manufacture(description_part_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE module_part (
    module_id INT NOT NULL,
    part_id INT NOT NULL,
    quantity INT NOT NULL,
    PRIMARY KEY (module_id, part_id),

    FOREIGN KEY (module_id) REFERENCES modules(module_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (part_id) REFERENCES parts(part_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE changes_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    
    table_name VARCHAR(100),
    record_id INT,
    column_name VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    changed_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    changed_by INT,

    FOREIGN KEY (changed_by) REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Индексы
CREATE INDEX idx_module_serial_number ON modules(serial_number);
CREATE INDEX idx_module_decimal_number ON modules(decimal_number);
CREATE INDEX idx_module_name ON modules(name);
CREATE INDEX idx_part_name ON parts(name);
CREATE INDEX idx_client_name ON clients(name);

CREATE INDEX idx_part_module ON module_part(module_id, part_id);
CREATE INDEX idx_module_machine_serial ON modules(machine_id, serial_number);
CREATE INDEX idx_part_manufacturer_id ON part_manufacture(manufacturer_id);
CREATE INDEX idx_module_machine_id ON modules(machine_id);
