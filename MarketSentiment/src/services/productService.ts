import Product, { type IProduct } from '../models/productModel'

interface ProductData {
  name: string
  description: string
  price: number
  category: string
  imageUrl?: string
  inStock?: boolean
}

interface ProductQuery {
  category?: string
  inStock?: boolean
  minPrice?: number
  maxPrice?: number
  search?: string
}

export default class ProductService {
  public static async createProduct(productData: ProductData): Promise<IProduct> {
    return await Product.create(productData)
  }

  public static async getProductById(id: string): Promise<IProduct> {
    const product = await Product.findById(id)
    if (!product) {
      throw new Error('Product not found')
    }
    return product
  }

  public static async getAllProducts(query: ProductQuery = {}): Promise<IProduct[]> {
    const { category, inStock, minPrice, maxPrice, search } = query
    const filter: any = {}

    // Build filter based on query params
    if (category) filter.category = category
    if (inStock !== undefined) filter.inStock = inStock

    if (minPrice !== undefined || maxPrice !== undefined) {
      filter.price = {}
      if (minPrice !== undefined) filter.price.$gte = minPrice
      if (maxPrice !== undefined) filter.price.$lte = maxPrice
    }

    if (search) {
      filter.$or = [
        { name: { $regex: search, $options: 'i' } },
        { description: { $regex: search, $options: 'i' } },
      ]
    }

    return await Product.find(filter)
  }

  public static async updateProduct(
    id: string,
    productData: Partial<ProductData>,
  ): Promise<IProduct> {
    const product = await Product.findById(id)
    if (!product) {
      throw new Error('Product not found')
    }

    // Update fields
    if (productData.name) product.name = productData.name
    if (productData.description) product.description = productData.description
    if (productData.price !== undefined) product.price = productData.price
    if (productData.category) product.category = productData.category
    if (productData.imageUrl) product.imageUrl = productData.imageUrl
    if (productData.inStock !== undefined) product.inStock = productData.inStock

    await product.save()

    return product
  }

  public static async deleteProduct(id: string): Promise<void> {
    const product = await Product.findById(id)
    if (!product) {
      throw new Error('Product not found')
    }
    await product.deleteOne()
  }
}
