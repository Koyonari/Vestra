import { errorResponse } from '@/utils/apiResponses'
import { type Request, type Response, type NextFunction } from 'express'

interface CustomError extends Error {
  statusCode?: number
}

export const errorHandler = (err: CustomError, req: Request, res: Response, next: NextFunction) => {
  const statusCode = err.statusCode || 500

  errorResponse(
    res,
    err.message || 'Server Error',
    statusCode,
    process.env.NODE_ENV === 'production' ? undefined : err.stack,
  )
}

export const notFound = (req: Request, res: Response, next: NextFunction) => {
  const error = new Error(`Not Found - ${req.originalUrl}`) as CustomError
  error.statusCode = 404
  next(error)
}
