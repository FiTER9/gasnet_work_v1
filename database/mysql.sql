CREATE DATABASE IF NOT EXISTS gasnet CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE gasnet;
CREATE TABLE IF NOT EXISTS gas_data (
 id BIGINT PRIMARY KEY AUTO_INCREMENT, time DATETIME NOT NULL, simulation_id VARCHAR(36) NOT NULL,
 branch INT NOT NULL, pressure DOUBLE NOT NULL, flow DOUBLE NOT NULL, valve DOUBLE NOT NULL,
 risk_level TINYINT NOT NULL DEFAULT 0, INDEX idx_gas_time(time), INDEX idx_simulation(simulation_id)
);
CREATE TABLE IF NOT EXISTS alarm (
 id BIGINT PRIMARY KEY AUTO_INCREMENT, time DATETIME NOT NULL, device VARCHAR(100) NOT NULL,
 type VARCHAR(50) NOT NULL, level TINYINT NOT NULL, description TEXT NOT NULL,
 status VARCHAR(20) NOT NULL DEFAULT '未处理', handled_by BIGINT NULL, handled_at DATETIME NULL,
 INDEX idx_alarm_time(time), INDEX idx_alarm_status(status)
);

