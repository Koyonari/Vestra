import { type Request, type Response } from 'express'
import ProductService from '../services/productService'
import asyncHandler from 'express-async-handler'
import { successResponse, errorResponse } from '../utils/apiResponses'

// @desc    Create a product
// @route   POST /api/products
// @access  Private/Admin
export const createProduct = asyncHandler(async (req: Request, res: Response) => {
  try {
    const product = await ProductService.createProduct(req.body)
    successResponse(res, product, 'Product created successfully', 201)
  } catch (error) {
    if (error instanceof Error) {
      errorResponse(res, error.message, 400)
    } else {
      errorResponse(res, 'Failed to create product', 400)
    }
  }
})

// @desc    Get all products with optional filtering
// @route   GET /api/products
// @access  Public
export const getProducts = asyncHandler(async (req: Request, res: Response) => {
  try {
    const query = {
      category: req.query.category as string | undefined,
      inStock:
        req.query.inStock === 'true' ? true : req.query.inStock === 'false' ? false : undefined,
      minPrice: req.query.minPrice ? Number(req.query.minPrice) : undefined,
      maxPrice: req.query.maxPrice ? Number(req.query.maxPrice) : undefined,
      search: req.query.search as string | undefined,
    }

    const products = await ProductService.getAllProducts(query)
    successResponse(res, products)
  } catch (error) {
    if (error instanceof Error) {
      errorResponse(res, error.message, 500)
    } else {
      errorResponse(res, 'Failed to fetch products', 500)
    }
  }
})

// @desc    Get product by ID
// @route   GET /api/products/:id
// @access  Public
export const getProductById = asyncHandler(async (req: Request, res: Response) => {
  try {
    const product = await ProductService.getProductById(req.params.id)
    successResponse(res, product)
  } catch (error) {
    if (error instanceof Error) {
      errorResponse(res, error.message, 404)
    } else {
      errorResponse(res, 'Product not found', 404)
    }
  }
})

// @desc    Update a product
// @route   PUT /api/products/:id
// @access  Private/Admin
export const updateProduct = asyncHandler(async (req: Request, res: Response) => {
  try {
    const product = await ProductService.updateProduct(req.params.id, req.body)
    successResponse(res, product, 'Product updated successfully')
  } catch (error) {
    if (error instanceof Error) {
      errorResponse(res, error.message, 400)
    } else {
      errorResponse(res, 'Failed to update product', 400)
    }
  }
})

// @desc    Delete a product
// @route   DELETE /api/products/:id
// @access  Private/Admin
export const deleteProduct = asyncHandler(async (req: Request, res: Response) => {
  try {
    await ProductService.deleteProduct(req.params.id)
    successResponse(res, null, 'Product removed')
  } catch (error) {
    if (error instanceof Error) {
      errorResponse(res, error.message, 404)
    } else {
      errorResponse(res, 'Product not found', 404)
    }
  }
})
