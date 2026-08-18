-- ============================================================================
-- Project 04: Garage & Automotive Repair Management System
-- File 03: Performance Optimization B-Tree Indexes & Analytical Views
-- ============================================================================

-- 1. B-Tree Indexes for Foreign Keys & Frequent Query Filters
CREATE INDEX IF NOT EXISTS idx_vehicles_customer_id ON vehicles(customer_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_vin ON vehicles(vin);
CREATE INDEX IF NOT EXISTS idx_inventory_part_number ON inventory_parts(part_number);
CREATE INDEX IF NOT EXISTS idx_appointments_vehicle_date ON service_appointments(vehicle_id, service_date DESC);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON service_appointments(status);
CREATE INDEX IF NOT EXISTS idx_service_parts_appointment ON service_parts_used(appointment_id);
CREATE INDEX IF NOT EXISTS idx_service_parts_part ON service_parts_used(part_id);

-- 2. Analytical View: Low Stock Inventory Alerts
CREATE OR REPLACE VIEW v_low_stock_alerts AS
SELECT 
    part_id,
    part_number,
    name,
    stock_quantity,
    reorder_threshold,
    (reorder_threshold - stock_quantity) AS units_needed
FROM inventory_parts
WHERE stock_quantity <= reorder_threshold
ORDER BY stock_quantity ASC;

-- 3. Analytical View: Comprehensive Vehicle Service History
CREATE OR REPLACE VIEW v_vehicle_service_history AS
SELECT 
    c.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    c.phone,
    v.vehicle_id,
    v.vin,
    CONCAT(v.year, ' ', v.make, ' ', v.model) AS vehicle_info,
    sa.appointment_id,
    sa.service_date,
    sa.status,
    sa.labor_cost,
    sa.total_cost
FROM customers c
JOIN vehicles v ON c.customer_id = v.customer_id
JOIN service_appointments sa ON v.vehicle_id = sa.vehicle_id;
