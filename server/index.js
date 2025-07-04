const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const morgan = require('morgan');
const dotenv = require('dotenv');
const { Server } = require('socket.io');
const http = require('http');
const Detection = require('./models/Detection');

dotenv.config();

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: 'http://localhost:5173', methods: ['GET', 'POST'] }
});

app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

// Connect to MongoDB (hardcode URI if preferred)
mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/yolov5_logs', {
  useNewUrlParser: true,
  useUnifiedTopology: true
}).then(() => {
  console.log('MongoDB connected');
}).catch(err => {
  console.error('MongoDB connection error:', err);
});

// Routes
app.use('/api/detections', require('./routes/detection'));

// Poll MongoDB for new detections
let lastTimestamp = null;
const pollDetections = async () => {
  try {
    const query = lastTimestamp ? { timestamp: { $gt: lastTimestamp } } : {};
    const newDetections = await Detection.find(query)
      .sort({ timestamp: -1 })
      .limit(10);
    
    if (newDetections.length > 0) {
      lastTimestamp = newDetections[0].timestamp;
      newDetections.forEach(detection => {
        io.emit('newDetection', detection);
      });
    }
  } catch (err) {
    console.error('Polling error:', err);
  }
};

// Poll every 1 second
setInterval(pollDetections, 1000);

// Socket.IO connection
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  server.close(() => {
    mongoose.connection.close();
    process.exit(0);
  });
});