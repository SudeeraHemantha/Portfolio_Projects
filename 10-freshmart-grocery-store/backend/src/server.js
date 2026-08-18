const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');

const Product = require('./models/Product');
const Order = require('./models/Order');

const PORT = process.env.PORT || 5000;
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/freshmart_db';

const app = express();

app.use(cors());
app.use(express.json());

// Initial Sample Grocery Catalog Seeding
const initialProducts = [
  { name: "Organic Honeycrisp Apples", category: "Fresh Produce", price: 2.99, unit: "lb", isOrganic: true, stock: 100, description: "Crisp and sweet organic apples sourced from local orchards." },
  { name: "Artisanal Whole Wheat Bread", category: "Bakery", price: 4.49, unit: "loaf", isOrganic: false, stock: 40, description: "Freshly baked daily with 100% whole grain flour." },
  { name: "Organic Whole Milk (1 Gal)", category: "Dairy", price: 5.29, unit: "gallon", isOrganic: true, stock: 60, description: "Pasteurized organic whole milk rich in nutrients." },
  { name: "Fresh Hass Avocados (Bag of 4)", category: "Fresh Produce", price: 4.99, unit: "bag", isOrganic: true, stock: 85, description: "Ripe and ready to eat creamy Hass avocados." },
  { name: "Cold Pressed Orange Juice 32oz", category: "Beverages", price: 6.99, unit: "bottle", isOrganic: true, stock: 35, description: "100% pure cold pressed oranges with zero added sugar." },
  { name: "Grass-Fed Greek Yogurt 32oz", category: "Dairy", price: 5.79, unit: "tub", isOrganic: true, stock: 45, description: "Probiotic-rich plain Greek yogurt." }
];

async function seedDatabaseIfEmpty() {
  try {
    const count = await Product.countDocuments();
    if (count === 0) {
      await Product.insertMany(initialProducts);
      console.log('[MongoDB] FreshMart product catalog seeded successfully.');
    }
  } catch (err) {
    console.error('[MongoDB] Seeding error:', err.message);
  }
}

// Connect to MongoDB
mongoose.connect(MONGODB_URI)
  .then(() => {
    console.log('[MongoDB] Connected to FreshMart Database');
    seedDatabaseIfEmpty();
  })
  .catch(err => console.error('[MongoDB] Connection Error:', err));

// REST Routes
app.get('/health', (req, res) => {
  res.json({ status: 'alive', service: 'FreshMart Grocery E-Commerce API', db: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected' });
});

app.get('/api/v1/products', async (req, res) => {
  try {
    const { category, search } = req.query;
    let query = {};

    if (category && category !== 'All') {
      query.category = category;
    }

    if (search) {
      query.name = { $regex: search, $options: 'i' };
    }

    const products = await Product.find(query).sort({ createdAt: -1 });
    res.json(products);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/v1/products', async (req, res) => {
  try {
    const product = new Product(req.body);
    await product.save();
    res.status(201).json(product);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

app.post('/api/v1/orders', async (req, res) => {
  try {
    const { customerName, email, deliveryAddress, items } = req.body;
    if (!items || items.length === 0) {
      return res.status(400).json({ error: 'Order must contain at least one item' });
    }

    const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const deliveryFee = 3.99;
    const total = parseFloat((subtotal + deliveryFee).toFixed(2));

    const order = new Order({
      customerName,
      email,
      deliveryAddress,
      items,
      subtotal,
      deliveryFee,
      total,
      status: 'Processing'
    });

    await order.save();
    res.status(201).json(order);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

app.get('/api/v1/orders', async (req, res) => {
  try {
    const orders = await Order.find().sort({ createdAt: -1 });
    res.json(orders);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`[Express] FreshMart Server running on port ${PORT}`);
});
