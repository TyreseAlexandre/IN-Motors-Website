-- IN Motors — MySQL schema
-- Run once against an empty database, e.g.:
--   mysql -u root -p in_motors < database/schema.sql
 
 use in_motors;
 
 
CREATE TABLE IF NOT EXISTS admin_users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS vehicles (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    slug         VARCHAR(255) NOT NULL UNIQUE,
    brand        VARCHAR(100) NOT NULL,
    model        VARCHAR(100) NOT NULL,
    year         SMALLINT NOT NULL,
    price        DECIMAL(12,2) NOT NULL,
    mileage      INT NULL,
    transmission VARCHAR(50) NULL,
    fuel_type    VARCHAR(50) NULL,
    engine       VARCHAR(100) NULL,
    color        VARCHAR(50) NULL,
    location     VARCHAR(100) NULL,
    description  TEXT NULL,
    status       ENUM('disponivel','reservado','vendido') NOT NULL DEFAULT 'disponivel',
    is_featured  BOOLEAN NOT NULL DEFAULT FALSE,
    is_visible   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_vehicles_visible_status (is_visible, status),
    INDEX idx_vehicles_brand (brand)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS vehicle_images (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id  INT NOT NULL,
    image_url   VARCHAR(500) NOT NULL,
    public_id   VARCHAR(255) NOT NULL,
    is_primary  BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order  INT NOT NULL DEFAULT 0,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_vehicle_images_vehicle
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
        ON DELETE CASCADE,
    INDEX idx_vehicle_images_vehicle (vehicle_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create/update the app's DB user and grant access. Run this manually in a
-- terminal (never store a real password in a committed file):
--   CREATE USER IF NOT EXISTS 'inmotors_app'@'localhost' IDENTIFIED BY 'your-password-here';
--   GRANT ALL PRIVILEGES ON in_motors.* TO 'inmotors_app'@'localhost';
--   FLUSH PRIVILEGES;