import { type Request, type Response, type NextFunction } from 'express'
import jwt from 'jsonwebtoken'
import User, { type IUser } from '../models/userModel'
import asyncHandler from 'express-async-handler'
import { errorResponse } from '../utils/apiResponses'

interface JwtPayload {
  id: string
}

declare global {
  namespace Express {
    interface Request {
      user?: IUser
    }
  }
}

export const protect = asyncHandler(async (req: Request, res: Response, next: NextFunction) => {
  let token

  // Check if auth header exists and starts with Bearer
  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    try {
      // Get token from header
      token = req.headers.authorization.split(' ')[1]

      // Verify token
      const decoded = jwt.verify(token, process.env.JWT_SECRET || 'secret') as JwtPayload

      // Get user from the token
      req.user = await User.findById(decoded.id).select('-password')

      next()
    } catch (error) {
      errorResponse(res, 'Not authorized, token failed', 401)
      return
    }
  }

  if (!token) {
    errorResponse(res, 'Not authorized, no token', 401)
    return
  }
})

export const admin = (req: Request, res: Response, next: NextFunction) => {
  if (req.user && req.user.isAdmin) {
    next()
  } else {
    errorResponse(res, 'Not authorized as an admin', 403)
    return
  }
}
