const http = require('http');
const express = require('express');
const cors = require('cors');
const { WebSocketServer, WebSocket } = require('ws');

const PORT = process.env.PORT || 5000;
const app = express();

app.use(cors());
app.use(express.json());

// In-Memory POS Store (Syncs with PostgreSQL when active)
let tables = [
  { id: 1, name: "Table 01", seats: 2, status: "available" },
  { id: 2, name: "Table 02", seats: 4, status: "occupied" },
  { id: 3, name: "Table 03", seats: 4, status: "available" },
  { id: 4, name: "Table 04", seats: 6, status: "reserved" },
  { id: 5, name: "Table 05", seats: 2, status: "available" },
  { id: 6, name: "Table 06", seats: 8, status: "available" }
];

let menuItems = [
  { id: 101, name: "Espresso Single", category: "Coffee", price: 3.50 },
  { id: 102, name: "Oat Milk Latte", category: "Coffee", price: 5.25 },
  { id: 103, name: "Matcha Latte", category: "Tea", price: 5.50 },
  { id: 104, name: "Artisanal Croissant", category: "Pastry", price: 4.00 },
  { id: 105, name: "Avocado Sourdough Toast", category: "Food", price: 12.00 }
];

let orders = [
  {
    id: "ORD-1001",
    tableId: 2,
    tableName: "Table 02",
    items: [
      { id: 102, name: "Oat Milk Latte", price: 5.25, quantity: 2 },
      { id: 104, name: "Artisanal Croissant", price: 4.00, quantity: 1 }
    ],
    subtotal: 14.50,
    tax: 1.16,
    total: 15.66,
    status: "in_kitchen",
    createdAt: new Date().toISOString()
  }
];

// Server & WebSocket Initialization
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

function broadcastWebSocketEvent(eventType, payload) {
  const message = JSON.stringify({ type: eventType, data: payload });
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  });
}

wss.on('connection', (ws) => {
  console.log('[WebSocket] KDS Client Connected');
  ws.send(JSON.stringify({ type: 'INIT_STATE', data: { tables, orders } }));
});

// REST Endpoints
app.get('/health', (req, res) => {
  res.json({ status: 'alive', service: 'Intelligent Cafe POS Server' });
});

app.get('/api/v1/tables', (req, res) => {
  res.json(tables);
});

app.patch('/api/v1/tables/:id/status', (req, res) => {
  const tableId = parseInt(req.params.id);
  const { status } = req.body;
  const table = tables.find(t => t.id === tableId);
  if (!table) return res.status(404).json({ error: 'Table not found' });

  table.status = status;
  broadcastWebSocketEvent('TABLE_STATUS_UPDATED', table);
  res.json(table);
});

app.get('/api/v1/menu', (req, res) => {
  res.json(menuItems);
});

app.get('/api/v1/orders', (req, res) => {
  res.json(orders);
});

app.post('/api/v1/orders', (req, res) => {
  const { tableId, items } = req.body;
  const table = tables.find(t => t.id === tableId);
  if (!table) return res.status(400).json({ error: 'Invalid Table ID' });

  const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const tax = parseFloat((subtotal * 0.08).toFixed(2));
  const total = parseFloat((subtotal + tax).toFixed(2));

  const newOrder = {
    id: `ORD-${Date.now().toString().slice(-4)}`,
    tableId,
    tableName: table.name,
    items,
    subtotal,
    tax,
    total,
    status: 'in_kitchen',
    createdAt: new Date().toISOString()
  };

  orders.unshift(newOrder);
  table.status = 'occupied';

  broadcastWebSocketEvent('ORDER_CREATED', newOrder);
  broadcastWebSocketEvent('TABLE_STATUS_UPDATED', table);

  res.status(201).json(newOrder);
});

app.patch('/api/v1/orders/:id/status', (req, res) => {
  const orderId = req.params.id;
  const { status } = req.body;
  const order = orders.find(o => o.id === orderId);
  if (!order) return res.status(404).json({ error: 'Order not found' });

  order.status = status;
  broadcastWebSocketEvent('ORDER_STATUS_UPDATED', order);
  res.json(order);
});

server.listen(PORT, () => {
  console.log(`[Express & WebSockets] Cafe POS Server running on port ${PORT}`);
});
