import { type Request, type Response } from 'express'
import UserService from '../services/userService'
import asyncHandler from 'express-async-handler'
import { successResponse, errorResponse } from '../utils/apiResponses'

// @desc    Register a new user
// @route   POST /api/users
// @access  Public
export const registerUser = asyncHandler(async (req: Request, res: Response) => {
  try {
    const { user, token } = await UserService.registerUser(req.body)
    successResponse(res, { user, token }, 'User registered successfully', 201)
  } catch (error) {
    if (error instanceof Error) {
      errorResponse(res, error.message, 400)
    } else {
      errorResponse(res, 'An unknown error occurred', 400)
    }
  }
})

// @desc    Auth user & get token
// @route   POST /api/users/login
// @access  Public
export const loginUser = asyncHandler(async (req: Request, res: Response) => {
  try {
    const { user, token } = await UserService.loginUser(req.body)
    successResponse(res, { user, token }, 'Login successful')
  } catch (error) {
    if (error instanceof Error) {
      errorResponse(res, error.message, 401)
    } else {
      errorResponse(res, 'An unknown error occurred', 401)
    }
  }
})

// @desc    Get user profile
// @route   GET /api/users/profile
// @access  Private
export const getUserProfile = asyncHandler(async (req: Request, res: Response) => {
  try {
    // @ts-ignore - req.user is added by auth middleware
    const user = await UserService.getUserById(req.user._id)
    successResponse(res, {
      _id: user._id,
      name: user.name,
      email: user.email,
      isAdmin: user.isAdmin,
    })
  } catch (error) {
    if (error instanceof Error) {
      errorResponse(res, error.message, 404)
    } else {
      errorResponse(res, 'User not found', 404)
    }
  }
})

// @desc    Update user profile
// @route   PUT /api/users/profile
// @access  Private
export const updateUserProfile = asyncHandler(async (req: Request, res: Response) => {
  try {
    // @ts-ignore - req.user is added by auth middleware
    const user = await UserService.updateUser(req.user._id, req.body)
    successResponse(
      res,
      {
        _id: user._id,
        name: user.name,
        email: user.email,
        isAdmin: user.isAdmin,
      },
      'Profile updated successfully',
    )
  } catch (error) {
    if (error instanceof Error) {
      errorResponse(res, error.message, 400)
    } else {
      errorResponse(res, 'An unknown error occurred', 400)
    }
  }
})

// @desc    Get all users
// @route   GET /api/users
// @access  Private/Admin
export const getUsers = asyncHandler(async (req: Request, res: Response) => {
  try {
    const users = await UserService.getAllUsers()
    successResponse(res, users)
  } catch (error) {
    if (error instanceof Error) {
      errorResponse(res, error.message, 500)
    } else {
      errorResponse(res, 'Failed to fetch users', 500)
    }
  }
})

// @desc    Delete user
// @route   DELETE /api/users/:id
// @access  Private/Admin
export const deleteUser = asyncHandler(async (req: Request, res: Response) => {
  try {
    await UserService.deleteUser(req.params.id)
    successResponse(res, null, 'User removed')
  } catch (error) {
    if (error instanceof Error) {
      errorResponse(res, error.message, 404)
    } else {
      errorResponse(res, 'User not found', 404)
    }
  }
})

// @desc    Get user by ID
// @route   GET /api/users/:id
// @access  Private/Admin
export const getUserById = asyncHandler(async (req: Request, res: Response) => {
  try {
    const user = await UserService.getUserById(req.params.id)
    successResponse(res, {
      _id: user._id,
      name: user.name,
      email: user.email,
      isAdmin: user.isAdmin,
    })
  } catch (error) {
    if (error instanceof Error) {
      errorResponse(res, error.message, 404)
    } else {
      errorResponse(res, 'User not found', 404)
    }
  }
})

// @desc    Update user
// @route   PUT /api/users/:id
// @access  Private/Admin
export const updateUser = asyncHandler(async (req: Request, res: Response) => {
  try {
    const user = await UserService.updateUser(req.params.id, req.body)
    successResponse(
      res,
      {
        _id: user._id,
        name: user.name,
        email: user.email,
        isAdmin: user.isAdmin,
      },
      'User updated successfully',
    )
  } catch (error) {
    if (error instanceof Error) {
      errorResponse(res, error.message, 400)
    } else {
      errorResponse(res, 'Failed to update user', 400)
    }
  }
})
