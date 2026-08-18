-- ============================================================================
-- Project 04: Garage & Automotive Repair Management System
-- File 02: PL/pgSQL Stored Procedures & Inventory Triggers
-- ============================================================================

-- 1. Trigger Function: Deduct Inventory Stock on Part Usage
CREATE OR REPLACE FUNCTION deduct_inventory_on_part_used()
RETURNS TRIGGER AS $$
DECLARE
    current_stock INT;
    part_name VARCHAR(255);
BEGIN
    -- Query current stock and part name
    SELECT stock_quantity, name INTO current_stock, part_name
    FROM inventory_parts
    WHERE part_id = NEW.part_id;

    -- Validate stock availability
    IF current_stock IS NULL THEN
        RAISE EXCEPTION 'Inventory part ID % does not exist.', NEW.part_id;
    END IF;

    IF current_stock < NEW.quantity_used THEN
        RAISE EXCEPTION 'Insufficient stock for part "%" (ID %). Available: %, Requested: %.', 
            part_name, NEW.part_id, current_stock, NEW.quantity_used;
    END IF;

    -- Deduct inventory quantity
    UPDATE inventory_parts
    SET stock_quantity = stock_quantity - NEW.quantity_used
    WHERE part_id = NEW.part_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger Binding: Fires before inserting a part usage record
DROP TRIGGER IF EXISTS trg_deduct_inventory ON service_parts_used;
CREATE TRIGGER trg_deduct_inventory
BEFORE INSERT ON service_parts_used
FOR EACH ROW
EXECUTE FUNCTION deduct_inventory_on_part_used();


-- 2. Stored Procedure: Recalculate Appointment Total Cost
CREATE OR REPLACE PROCEDURE recalculate_appointment_total(p_appointment_id INT)
AS $$
DECLARE
    v_parts_total NUMERIC(10, 2) := 0.00;
    v_labor_cost NUMERIC(10, 2) := 0.00;
BEGIN
    -- Calculate sum of parts used
    SELECT COALESCE(SUM(quantity_used * unit_price_charged), 0.00)
    INTO v_parts_total
    FROM service_parts_used
    WHERE appointment_id = p_appointment_id;

    -- Fetch labor cost
    SELECT COALESCE(labor_cost, 0.00)
    INTO v_labor_cost
    FROM service_appointments
    WHERE appointment_id = p_appointment_id;

    -- Update total cost in service_appointments
    UPDATE service_appointments
    SET total_cost = v_labor_cost + v_parts_total
    WHERE appointment_id = p_appointment_id;

    RAISE NOTICE 'Appointment ID % total cost recalculated: Parts %, Labor %, Total %', 
        p_appointment_id, v_parts_total, v_labor_cost, (v_labor_cost + v_parts_total);
END;
$$ LANGUAGE plpgsql;
