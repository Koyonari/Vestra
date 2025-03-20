import User, { type IUser } from '../models/userModel'
import jwt from 'jsonwebtoken'

interface UserData {
  name: string
  email: string
  password: string
  isAdmin?: boolean
}

interface LoginData {
  email: string
  password: string
}

export interface AuthResult {
  user: Partial<IUser>
  token: string
}

export default class UserService {
  public static async registerUser(userData: UserData): Promise<AuthResult> {
    const { name, email, password, isAdmin } = userData

    // Check if user exists
    const existingUser = await User.findOne({ email })
    if (existingUser) {
      throw new Error('User already exists')
    }

    // Create user
    const user = await User.create({
      name,
      email,
      password,
      isAdmin: isAdmin || false,
    })

    const token = this.generateToken((user._id as string).toString())

    const userWithoutPassword = {
      _id: user._id,
      name: user.name,
      email: user.email,
      isAdmin: user.isAdmin,
    }

    return { user: userWithoutPassword, token }
  }
  public static async loginUser(loginData: LoginData): Promise<AuthResult> {
    const { email, password } = loginData

    // Check for user
    const user = await User.findOne({ email }).select('+password')
    if (!user) {
      throw new Error('Invalid credentials')
    }

    // Check if password matches
    const isMatch = await user.comparePassword(password)
    if (!isMatch) {
      throw new Error('Invalid credentials')
    }

    const token = this.generateToken((user._id as string).toString())

    const userWithoutPassword = {
      _id: user._id,
      name: user.name,
      email: user.email,
      isAdmin: user.isAdmin,
    }

    return { user: userWithoutPassword, token }
  }

  public static async getUserById(id: string): Promise<IUser> {
    const user = await User.findById(id)
    if (!user) {
      throw new Error('User not found')
    }
    return user
  }

  public static async getAllUsers(): Promise<IUser[]> {
    return await User.find()
  }

  public static async updateUser(id: string, userData: Partial<UserData>): Promise<IUser> {
    const user = await User.findById(id)
    if (!user) {
      throw new Error('User not found')
    }

    // Update fields
    if (userData.name) user.name = userData.name
    if (userData.email) user.email = userData.email
    if (userData.password) user.password = userData.password
    if (userData.isAdmin !== undefined) user.isAdmin = userData.isAdmin

    await user.save()

    return user
  }

  public static async deleteUser(id: string): Promise<void> {
    const user = await User.findById(id)
    if (!user) {
      throw new Error('User not found')
    }
    await user.deleteOne()
  }

  private static generateToken(id: string): string {
    return jwt.sign({ id }, process.env.JWT_SECRET || 'secret', {
      expiresIn: '30d',
    })
  }
}
