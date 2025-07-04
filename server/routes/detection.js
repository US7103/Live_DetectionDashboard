const express = require('express');
const router = express.Router();
const Detection = require('../models/Detection');

// Get latest 50 detections
router.get('/', async (req, res) => {
  try {
    const detection = await Detection.find()
      .sort({ timestamp: -1 })
      .limit(50);
    res.json(detection);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;