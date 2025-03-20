import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/base.css'

const app = createApp(App)

app.use(router)

app.mount('#app')

// import express, { Application } from 'express';
// import createServer from './config/server';
// import connectDB from './config/database';
// import { notFound, errorHandler } from './middleware/error';
// import apiRoutes from './routes';
// import path from 'path';

// const app: Application = createServer();

// // Connect to database
// connectDB();

// // API Routes (all under /api)
// app.use('/api', apiRoutes);

// // Serve static assets in production
// if (process.env.NODE_ENV === 'production') {
//   // Set static folder
//   const distPath = path.resolve(__dirname, '../../frontend/dist');
//   app.use(express.static(distPath));

//   // Any route that is not an API route should serve the index.html
//   app.get('*', (req, res) => {
//     res.sendFile(path.resolve(distPath, 'index.html'));
//   });
// } else {
//   app.get('/', (req, res) => {
//     res.send('API is running...');
//   });
// }

// // Error Middleware
// app.use(notFound);
// app.use(errorHandler);

// export default app;
