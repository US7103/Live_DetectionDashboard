const mongoose = require('mongoose');

const detectionSchema = new mongoose.Schema({
  timestamp: { type: String, required: true },
  label: { type: String, required: true },
  confidence: { type: Number, required: true },
  bbox: {
    xmin: { type: Number, required: true },
    ymin: { type: Number, required: true },
    xmax: { type: Number, required: true },
    ymax: { type: Number, required: true }
  },
  source: { type: String, required: true }
}, { timestamps: true });

module.exports = mongoose.model('Detection', detectionSchema);