-- ============================================================================
-- Project 04: Garage & Automotive Repair Management System
-- File 01: 3NF Relational Database Schema Initialization
-- ============================================================================

-- 1. Customers Table (1NF / 2NF / 3NF Compliant)
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Vehicles Table (3NF: linked via customer_id FK)
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    vin VARCHAR(17) UNIQUE NOT NULL,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INT NOT NULL CHECK (year >= 1900 AND year <= 2100),
    license_plate VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Inventory Parts Catalog Table
CREATE TABLE IF NOT EXISTS inventory_parts (
    part_id SERIAL PRIMARY KEY,
    part_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    unit_cost NUMERIC(10, 2) NOT NULL CHECK (unit_cost >= 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    stock_quantity INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    reorder_threshold INT NOT NULL DEFAULT 5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Service Appointments Table
CREATE TABLE IF NOT EXISTS service_appointments (
    appointment_id SERIAL PRIMARY KEY,
    vehicle_id INT NOT NULL REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    service_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'Scheduled' CHECK (status IN ('Scheduled', 'In Progress', 'Completed', 'Cancelled')),
    labor_cost NUMERIC(10, 2) DEFAULT 0.00 CHECK (labor_cost >= 0),
    total_cost NUMERIC(10, 2) DEFAULT 0.00 CHECK (total_cost >= 0),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Service Parts Used Junction Table (Resolves Many-to-Many between Appointments & Parts)
CREATE TABLE IF NOT EXISTS service_parts_used (
    service_part_id SERIAL PRIMARY KEY,
    appointment_id INT NOT NULL REFERENCES service_appointments(appointment_id) ON DELETE CASCADE,
    part_id INT NOT NULL REFERENCES inventory_parts(part_id) ON DELETE RESTRICT,
    quantity_used INT NOT NULL CHECK (quantity_used > 0),
    unit_price_charged NUMERIC(10, 2) NOT NULL CHECK (unit_price_charged >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
