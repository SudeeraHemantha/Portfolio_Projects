import React, { useState, useEffect } from 'react';

const API_BASE = "http://localhost:5007/api/v1";

export default function App() {
  const [tables, setTables] = useState([
    { id: 1, name: "Table 01", seats: 2, status: "available" },
    { id: 2, name: "Table 02", seats: 4, status: "occupied" },
    { id: 3, name: "Table 03", seats: 4, status: "available" },
    { id: 4, name: "Table 04", seats: 6, status: "reserved" },
    { id: 5, name: "Table 05", seats: 2, status: "available" },
    { id: 6, name: "Table 06", seats: 8, status: "available" }
  ]);

  const [menuItems] = useState([
    { id: 101, name: "Espresso Single", category: "Coffee", price: 3.50 },
    { id: 102, name: "Oat Milk Latte", category: "Coffee", price: 5.25 },
    { id: 103, name: "Matcha Latte", category: "Tea", price: 5.50 },
    { id: 104, name: "Artisanal Croissant", category: "Pastry", price: 4.00 },
    { id: 105, name: "Avocado Sourdough Toast", category: "Food", price: 12.00 }
  ]);

  const [selectedTable, setSelectedTable] = useState(1);
  const [cart, setCart] = useState([]);
  const [activeOrders, setActiveOrders] = useState([]);

  const addToCart = (item) => {
    setCart((prev) => {
      const existing = prev.find((i) => i.id === item.id);
      if (existing) {
        return prev.map((i) => (i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i));
      }
      return [...prev, { ...item, quantity: 1 }];
    });
  };

  const removeFromCart = (id) => {
    setCart((prev) => prev.filter((item) => item.id !== id));
  };

  const subtotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const tax = parseFloat((subtotal * 0.08).toFixed(2));
  const total = parseFloat((subtotal + tax).toFixed(2));

  const placeOrder = () => {
    if (cart.length === 0) return;
    const tableObj = tables.find((t) => t.id === selectedTable);
    const newOrder = {
      id: `ORD-${Date.now().toString().slice(-4)}`,
      tableId: selectedTable,
      tableName: tableObj ? tableObj.name : `Table ${selectedTable}`,
      items: [...cart],
      subtotal,
      tax,
      total,
      status: "in_kitchen",
      createdAt: new Date().toLocaleTimeString()
    };

    setActiveOrders([newOrder, ...activeOrders]);
    setTables((prev) =>
      prev.map((t) => (t.id === selectedTable ? { ...t, status: "occupied" } : t))
    );
    setCart([]);
  };

  return (
    <div style={{ padding: "24px", maxWidth: "1400px", margin: "0 auto" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px", borderBottom: "1px solid #334155", paddingBottom: "16px" }}>
        <div>
          <h1 style={{ margin: 0, color: "#38bdf8", fontSize: "28px" }}>☕ Intelligent Cafe POS</h1>
          <p style={{ margin: "4px 0 0", color: "#94a3b8" }}>Real-time Table Grid & Kitchen Operations System</p>
        </div>
        <div style={{ background: "#1e293b", padding: "8px 16px", borderRadius: "8px", border: "1px solid #334155", color: "#10b981", fontWeight: "600" }}>
          ● Live KDS WebSocket Sync Active
        </div>
      </header>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "24px" }}>
        {/* Column 1: Table Selection */}
        <div style={{ background: "#1e293b", padding: "20px", borderRadius: "12px", border: "1px solid #334155" }}>
          <h2 style={{ fontSize: "18px", marginTop: 0, borderBottom: "1px solid #334155", paddingBottom: "12px" }}>🪑 Floor Grid & Tables</h2>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
            {tables.map((t) => (
              <div
                key={t.id}
                onClick={() => setSelectedTable(t.id)}
                style={{
                  padding: "16px",
                  borderRadius: "8px",
                  cursor: "pointer",
                  border: selectedTable === t.id ? "2px solid #38bdf8" : "1px solid #334155",
                  background: t.status === "occupied" ? "#451a03" : t.status === "reserved" ? "#312e81" : "#064e3b"
                }}
              >
                <div style={{ fontWeight: "bold", fontSize: "16px" }}>{t.name}</div>
                <div style={{ fontSize: "12px", color: "#cbd5e1" }}>Seats: {t.seats}</div>
                <div style={{ fontSize: "12px", textTransform: "capitalize", marginTop: "4px", color: "#94a3b8" }}>Status: {t.status}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Column 2: Menu Catalog & Order Builder */}
        <div style={{ background: "#1e293b", padding: "20px", borderRadius: "12px", border: "1px solid #334155" }}>
          <h2 style={{ fontSize: "18px", marginTop: 0, borderBottom: "1px solid #334155", paddingBottom: "12px" }}>📜 Menu Catalog</h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px", maxHeight: "350px", overflowY: "auto" }}>
            {menuItems.map((item) => (
              <div key={item.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px", background: "#0f172a", borderRadius: "6px" }}>
                <div>
                  <div style={{ fontWeight: "600" }}>{item.name}</div>
                  <div style={{ fontSize: "12px", color: "#94a3b8" }}>{item.category} • ${item.price.toFixed(2)}</div>
                </div>
                <button
                  onClick={() => addToCart(item)}
                  style={{ background: "#0284c7", color: "white", border: "none", padding: "6px 12px", borderRadius: "4px", cursor: "pointer" }}
                >
                  + Add
                </button>
              </div>
            ))}
          </div>

          <h3 style={{ fontSize: "16px", marginTop: "20px" }}>Cart for Table 0{selectedTable}</h3>
          {cart.length === 0 ? (
            <p style={{ color: "#94a3b8", fontSize: "14px" }}>No items in cart.</p>
          ) : (
            <div>
              {cart.map((c) => (
                <div key={c.id} style={{ display: "flex", justifyContent: "space-between", fontSize: "14px", margin: "4px 0" }}>
                  <span>{c.name} x {c.quantity}</span>
                  <span>${(c.price * c.quantity).toFixed(2)} <button onClick={() => removeFromCart(c.id)} style={{ background: "transparent", color: "#ef4444", border: "none", cursor: "pointer" }}>✕</button></span>
                </div>
              ))}
              <div style={{ borderTop: "1px dashed #334155", marginTop: "12px", paddingTop: "8px" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}><span>Subtotal:</span><span>${subtotal.toFixed(2)}</span></div>
                <div style={{ display: "flex", justifyContent: "space-between" }}><span>Tax (8%):</span><span>${tax.toFixed(2)}</span></div>
                <div style={{ display: "flex", justifyContent: "space-between", fontWeight: "bold", fontSize: "16px", marginTop: "4px", color: "#38bdf8" }}><span>Total:</span><span>${total.toFixed(2)}</span></div>
              </div>
              <button
                onClick={placeOrder}
                style={{ width: "100%", background: "#10b981", color: "white", border: "none", padding: "10px", borderRadius: "6px", fontWeight: "bold", marginTop: "12px", cursor: "pointer" }}
              >
                Submit Order to Kitchen
              </button>
            </div>
          )}
        </div>

        {/* Column 3: Kitchen Display System (KDS) Live Stream */}
        <div style={{ background: "#1e293b", padding: "20px", borderRadius: "12px", border: "1px solid #334155" }}>
          <h2 style={{ fontSize: "18px", marginTop: 0, borderBottom: "1px solid #334155", paddingBottom: "12px" }}>👨‍🍳 Kitchen Display Feed (KDS)</h2>
          {activeOrders.length === 0 ? (
            <p style={{ color: "#94a3b8", fontSize: "14px" }}>No active kitchen orders.</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "12px", maxHeight: "500px", overflowY: "auto" }}>
              {activeOrders.map((ord) => (
                <div key={ord.id} style={{ background: "#0f172a", padding: "12px", borderRadius: "8px", borderLeft: "4px solid #f59e0b" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontWeight: "bold" }}>
                    <span>{ord.id} ({ord.tableName})</span>
                    <span style={{ color: "#f59e0b", fontSize: "12px" }}>● In Kitchen</span>
                  </div>
                  <div style={{ fontSize: "12px", color: "#94a3b8", marginBottom: "8px" }}>Ordered at: {ord.createdAt}</div>
                  {ord.items.map((i, idx) => (
                    <div key={idx} style={{ fontSize: "13px" }}>• {i.quantity}x {i.name}</div>
                  ))}
                  <div style={{ marginTop: "8px", fontWeight: "bold", textAlign: "right", color: "#10b981" }}>Total: ${ord.total.toFixed(2)}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
