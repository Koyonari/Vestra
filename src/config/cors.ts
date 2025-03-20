import cors from 'cors'

// Configuring CORS for Vue.js frontend
const corsOptions = {
  origin: process.env.FRONTEND_URL || 'http://localhost:8080', // Default Vue.js dev server
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  credentials: true, // Allow cookies for authentication
  maxAge: 86400, // OPTION results are cached for 24 hours
}

export default cors(corsOptions)
