import express, { type Application } from 'express'
import helmet from 'helmet'
import compression from 'compression'
import morgan from 'morgan'
import corsMiddleware from './cors'

const createServer = (): Application => {
  const app: Application = express()

  // Middleware
  app.use(express.json())
  app.use(express.urlencoded({ extended: true }))
  app.use(corsMiddleware) // Using custom CORS config for Vue.js
  app.use(
    helmet({
      contentSecurityPolicy: {
        directives: {
          ...helmet.contentSecurityPolicy.getDefaultDirectives(),
          'img-src': ["'self'", 'data:', 'blob:'],
        },
      },
    }),
  )
  app.use(compression())
  app.use(morgan('dev'))

  return app
}

export default createServer
