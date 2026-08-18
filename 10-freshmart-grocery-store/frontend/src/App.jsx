import React, { useState } from 'react';

const initialProducts = [
  { id: "p1", name: "Organic Honeycrisp Apples", category: "Fresh Produce", price: 2.99, unit: "lb", isOrganic: true, stock: 100, image: "🍎", description: "Crisp and sweet organic apples sourced from local orchards." },
  { id: "p2", name: "Artisanal Whole Wheat Bread", category: "Bakery", price: 4.49, unit: "loaf", isOrganic: false, stock: 40, image: "🍞", description: "Freshly baked daily with 100% whole grain flour." },
  { id: "p3", name: "Organic Whole Milk (1 Gal)", category: "Dairy", price: 5.29, unit: "gallon", isOrganic: true, stock: 60, image: "🥛", description: "Pasteurized organic whole milk rich in nutrients." },
  { id: "p4", name: "Fresh Hass Avocados (Bag of 4)", category: "Fresh Produce", price: 4.99, unit: "bag", isOrganic: true, stock: 85, image: "🥑", description: "Ripe and ready to eat creamy Hass avocados." },
  { id: "p5", name: "Cold Pressed Orange Juice 32oz", category: "Beverages", price: 6.99, unit: "bottle", isOrganic: true, stock: 35, image: "🍊", description: "100% pure cold pressed oranges with zero added sugar." },
  { id: "p6", name: "Grass-Fed Greek Yogurt 32oz", category: "Dairy", price: 5.79, unit: "tub", isOrganic: true, stock: 45, image: "🥣", description: "Probiotic-rich plain Greek yogurt." }
];

export default function App() {
  const [products] = useState(initialProducts);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [cart, setCart] = useState([]);
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);
  const [orderPlaced, setOrderPlaced] = useState(null);
  const [formData, setFormData] = useState({ name: "", email: "", address: "" });

  const categories = ["All", "Fresh Produce", "Bakery", "Dairy", "Beverages"];

  const filteredProducts = products.filter((p) => {
    const matchesCategory = selectedCategory === "All" || p.category === selectedCategory;
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const addToCart = (product) => {
    setCart((prev) => {
      const existing = prev.find((item) => item.id === product.id);
      if (existing) {
        return prev.map((item) => (item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item));
      }
      return [...prev, { ...product, quantity: 1 }];
    });
  };

  const updateQuantity = (id, delta) => {
    setCart((prev) =>
      prev
        .map((item) => {
          if (item.id === id) {
            const newQty = item.quantity + delta;
            return newQty > 0 ? { ...item, quantity: newQty } : null;
          }
          return item;
        })
        .filter(Boolean)
    );
  };

  const subtotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const deliveryFee = cart.length > 0 ? 3.99 : 0.00;
  const total = parseFloat((subtotal + deliveryFee).toFixed(2));

  const handleCheckout = (e) => {
    e.preventDefault();
    if (!formData.name || !formData.email || !formData.address) return;

    const newOrder = {
      orderId: `FM-${Math.floor(100000 + Math.random() * 900000)}`,
      customerName: formData.name,
      items: cart,
      total,
      estimatedDelivery: "30-45 minutes"
    };

    setOrderPlaced(newOrder);
    setCart([]);
    setIsCheckoutOpen(false);
  };

  return (
    <div style={{ minHeight: "100vh", background: "#0f172a" }}>
      {/* Header Bar */}
      <header style={{ background: "#1e293b", borderBottom: "1px solid #334155", padding: "16px 32px", display: "flex", justifyContent: "space-between", alignItems: "center", sticky: "top" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <span style={{ fontSize: "32px" }}>🥬</span>
          <div>
            <h1 style={{ margin: 0, color: "#10b981", fontSize: "24px" }}>FreshMart Express</h1>
            <p style={{ margin: 0, color: "#94a3b8", fontSize: "12px" }}>Same-Day Organic Grocery Delivery</p>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <input
            type="text"
            placeholder="Search fresh groceries..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ padding: "10px 16px", borderRadius: "20px", border: "1px solid #334155", background: "#0f172a", color: "white", width: "260px" }}
          />

          <button
            onClick={() => setIsCheckoutOpen(true)}
            style={{ background: "#10b981", color: "white", border: "none", padding: "10px 20px", borderRadius: "20px", fontWeight: "bold", cursor: "pointer", display: "flex", alignItems: "center", gap: "8px" }}
          >
            🛒 Cart ({cart.reduce((sum, item) => sum + item.quantity, 0)}) - ${total.toFixed(2)}
          </button>
        </div>
      </header>

      {/* Main Layout */}
      <div style={{ display: "flex", padding: "32px", maxWidth: "1400px", margin: "0 auto", gap: "32px" }}>
        {/* Category Sidebar */}
        <aside style={{ width: "220px", background: "#1e293b", padding: "20px", borderRadius: "16px", border: "1px solid #334155", height: "fit-content" }}>
          <h3 style={{ margin: "0 0 16px", color: "#38bdf8" }}>Categories</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                style={{
                  textAlign: "left",
                  padding: "10px 14px",
                  borderRadius: "8px",
                  border: "none",
                  background: selectedCategory === cat ? "#10b981" : "transparent",
                  color: selectedCategory === cat ? "white" : "#cbd5e1",
                  fontWeight: selectedCategory === cat ? "bold" : "normal",
                  cursor: "pointer"
                }}
              >
                {cat}
              </button>
            ))}
          </div>
        </aside>

        {/* Product Grid */}
        <main style={{ flex: 1 }}>
          <h2 style={{ margin: "0 0 20px", color: "#f8fafc" }}>{selectedCategory} Products</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: "20px" }}>
            {filteredProducts.map((product) => (
              <div key={product.id} style={{ background: "#1e293b", borderRadius: "16px", padding: "20px", border: "1px solid #334155", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                <div>
                  <div style={{ fontSize: "48px", textAlign: "center", marginBottom: "12px" }}>{product.image}</div>
                  {product.isOrganic && (
                    <span style={{ background: "#065f46", color: "#34d399", fontSize: "10px", fontWeight: "bold", padding: "4px 8px", borderRadius: "12px", textTransform: "uppercase" }}>
                      Organic
                    </span>
                  )}
                  <h3 style={{ fontSize: "16px", margin: "8px 0 4px", color: "#f8fafc" }}>{product.name}</h3>
                  <p style={{ fontSize: "12px", color: "#94a3b8", margin: "0 0 12px" }}>{product.description}</p>
                </div>
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                    <span style={{ fontSize: "20px", fontWeight: "bold", color: "#34d399" }}>${product.price.toFixed(2)}</span>
                    <span style={{ fontSize: "12px", color: "#64748b" }}>/ {product.unit}</span>
                  </div>
                  <button
                    onClick={() => addToCart(product)}
                    style={{ width: "100%", background: "#0284c7", color: "white", border: "none", padding: "10px", borderRadius: "8px", fontWeight: "bold", cursor: "pointer" }}
                  >
                    Add to Cart
                  </button>
                </div>
              </div>
            ))}
          </div>
        </main>
      </div>

      {/* Checkout Modal */}
      {isCheckoutOpen && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.75)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100 }}>
          <div style={{ background: "#1e293b", width: "450px", padding: "28px", borderRadius: "20px", border: "1px solid #334155", color: "white" }}>
            <h2 style={{ margin: "0 0 16px", color: "#10b981" }}>Checkout Summary</h2>
            {cart.length === 0 ? (
              <p>Your cart is empty.</p>
            ) : (
              <form onSubmit={handleCheckout}>
                <div style={{ maxHeight: "200px", overflowY: "auto", marginBottom: "16px" }}>
                  {cart.map((item) => (
                    <div key={item.id} style={{ display: "flex", justifyContent: "space-between", fontSize: "14px", margin: "8px 0" }}>
                      <span>{item.name} x {item.quantity}</span>
                      <div>
                        <button type="button" onClick={() => updateQuantity(item.id, -1)} style={{ padding: "2px 6px" }}>-</button>
                        <button type="button" onClick={() => updateQuantity(item.id, 1)} style={{ padding: "2px 6px", marginLeft: "4px" }}>+</button>
                        <span style={{ marginLeft: "12px" }}>${(item.price * item.quantity).toFixed(2)}</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div style={{ borderTop: "1px solid #334155", paddingTop: "12px", marginBottom: "16px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between" }}><span>Subtotal:</span><span>${subtotal.toFixed(2)}</span></div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}><span>Delivery Fee:</span><span>${deliveryFee.toFixed(2)}</span></div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontWeight: "bold", fontSize: "18px", marginTop: "8px", color: "#10b981" }}><span>Total:</span><span>${total.toFixed(2)}</span></div>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginBottom: "20px" }}>
                  <input type="text" placeholder="Full Name" required value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} style={{ padding: "10px", borderRadius: "8px", border: "1px solid #334155", background: "#0f172a", color: "white" }} />
                  <input type="email" placeholder="Email Address" required value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} style={{ padding: "10px", borderRadius: "8px", border: "1px solid #334155", background: "#0f172a", color: "white" }} />
                  <input type="text" placeholder="Delivery Address" required value={formData.address} onChange={(e) => setFormData({ ...formData, address: e.target.value })} style={{ padding: "10px", borderRadius: "8px", border: "1px solid #334155", background: "#0f172a", color: "white" }} />
                </div>

                <div style={{ display: "flex", gap: "12px" }}>
                  <button type="button" onClick={() => setIsCheckoutOpen(false)} style={{ flex: 1, background: "#475569", color: "white", border: "none", padding: "12px", borderRadius: "8px", cursor: "pointer" }}>Cancel</button>
                  <button type="submit" style={{ flex: 1, background: "#10b981", color: "white", border: "none", padding: "12px", borderRadius: "8px", fontWeight: "bold", cursor: "pointer" }}>Place Order</button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* Order Confirmation Banner */}
      {orderPlaced && (
        <div style={{ position: "fixed", bottom: "32px", right: "32px", background: "#065f46", border: "1px solid #34d399", color: "white", padding: "20px 28px", borderRadius: "16px", boxShadow: "0 10px 25px rgba(0,0,0,0.5)" }}>
          <h3 style={{ margin: "0 0 4px", color: "#34d399" }}>🎉 Order Confirmed!</h3>
          <p style={{ margin: 0, fontSize: "14px" }}>Order ID: <strong>{orderPlaced.orderId}</strong></p>
          <p style={{ margin: "4px 0 0", fontSize: "12px", color: "#a7f3d0" }}>Thank you {orderPlaced.customerName}! Estimated Delivery: {orderPlaced.estimatedDelivery}.</p>
        </div>
      )}
    </div>
  );
}
