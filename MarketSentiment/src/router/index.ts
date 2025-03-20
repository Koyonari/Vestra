import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
  ],
})

export default router

// src/routes/index.ts
// import express from 'express';
// import userRoutes from './userRoutes';
// import productRoutes from './productRoutes';

// const router = express.Router();

// // Health check endpoint
// router.get('/health', (req, res) => {
//   res.status(200).json({ status: 'ok', message: 'API is running' });
// });

// // API routes
// router.use('/users', userRoutes);
// router.use('/products', productRoutes);

// export default router;

// src/index.ts
// import app from './app';
// import dotenv from 'dotenv';

// dotenv.config();

// const PORT = process.env.PORT || 5000;

// app.listen(PORT, () => {
//   console.log(`Server running in ${process.env.NODE_ENV} mode on port ${PORT}`);
// });
