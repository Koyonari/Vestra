import { type Response } from 'express'

export interface ApiResponse<T> {
  success: boolean
  data?: T
  message?: string
  errors?: any
}

export const successResponse = <T>(
  res: Response,
  data: T,
  message = 'Success',
  statusCode = 200,
): void => {
  res.status(statusCode).json({
    success: true,
    data,
    message,
  } as ApiResponse<T>)
}

export const errorResponse = (
  res: Response,
  message = 'Error',
  statusCode = 500,
  errors?: any,
): void => {
  res.status(statusCode).json({
    success: false,
    message,
    errors,
  } as ApiResponse<null>)
}
