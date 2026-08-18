const mongoose = require('mongoose');

const OrderItemSchema = new mongoose.Schema({
  productId: { type: String, required: true },
  name: { type: String, required: true },
  price: { type: Number, required: true },
  quantity: { type: Number, required: true, min: 1 }
});

const OrderSchema = new mongoose.Schema({
  customerName: { type: String, required: true },
  email: { type: String, required: true },
  deliveryAddress: { type: String, required: true },
  items: [OrderItemSchema],
  subtotal: { type: Number, required: true },
  deliveryFee: { type: Number, default: 3.99 },
  total: { type: Number, required: true },
  status: { type: String, default: 'Processing', enum: ['Processing', 'Packing', 'Out for Delivery', 'Delivered'] }
}, {
  timestamps: true
});

module.exports = mongoose.model('Order', OrderSchema);
