const mongoose = require('mongoose');

const ProductSchema = new mongoose.Schema({
  name: { type: String, required: true, trim: true },
  category: { type: String, required: true, index: true }, // Fresh Produce, Bakery, Dairy, Organic, Beverages
  price: { type: Number, required: true, min: 0 },
  unit: { type: String, default: 'item' }, // lb, kg, pack, item, bunch
  stock: { type: Number, default: 50, min: 0 },
  imageUrl: { type: String, default: 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=500' },
  description: { type: String },
  isOrganic: { type: Boolean, default: false }
}, {
  timestamps: true
});

module.exports = mongoose.model('Product', ProductSchema);
