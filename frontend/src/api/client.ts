import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 errors (unauthorized)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient

// Auth API
export const authAPI = {
  register: (data: { name: string; email: string; password: string; phone?: string; address?: string }) =>
    apiClient.post('/auth/register', data),
  
  login: (email: string, password: string) => {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)
    return apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
  
  getMe: () => apiClient.get('/auth/me'),
}

// Products API
export const productsAPI = {
  getProducts: (params?: {
    page?: number
    page_size?: number
    category_id?: number
    search?: string
    min_price?: number
    max_price?: number
    in_stock?: boolean
    include_inactive?: boolean
  }) => apiClient.get('/products/', { params }),
  
  getProduct: (id: number) => apiClient.get(`/products/${id}`),
  
  createProduct: (data: {
    name: string
    description?: string
    price: number
    stock: number
    category_id?: number
    image_url?: string
    is_active?: number
  }) => apiClient.post('/products/', data),
  
  updateProduct: (id: number, data: {
    name?: string
    description?: string
    price?: number
    stock?: number
    category_id?: number
    image_url?: string
    is_active?: number
  }) => apiClient.put(`/products/${id}`, data),
  
  deleteProduct: (id: number) => apiClient.delete(`/products/${id}`),
}

// Categories API
export const categoriesAPI = {
  getCategories: (params?: { page?: number; page_size?: number }) =>
    apiClient.get('/categories/', { params }),
  
  getCategory: (id: number) => apiClient.get(`/categories/${id}`),
  
  createCategory: (data: { name: string; description?: string }) =>
    apiClient.post('/categories/', data),
  
  updateCategory: (id: number, data: { name?: string; description?: string }) =>
    apiClient.put(`/categories/${id}`, data),
  
  deleteCategory: (id: number) => apiClient.delete(`/categories/${id}`),
}

// Cart API
export const cartAPI = {
  getCart: () => apiClient.get('/cart'),
  
  addToCart: (productId: number, quantity: number) =>
    apiClient.post('/cart/items', { product_id: productId, quantity }),
  
  updateCartItem: (itemId: number, quantity: number) =>
    apiClient.put(`/cart/items/${itemId}`, { quantity }),
  
  removeFromCart: (itemId: number) => apiClient.delete(`/cart/items/${itemId}`),
  
  clearCart: () => apiClient.delete('/cart'),
}

// Orders API
export const ordersAPI = {
  getOrders: (params?: { page?: number; page_size?: number }) =>
    apiClient.get('/orders', { params }),
  
  getOrder: (id: number) => apiClient.get(`/orders/${id}`),
  
  createOrder: (data: {
    shipping_address: string
    payment_method?: string
    notes?: string
  }) => apiClient.post('/orders', data),
  
  updateOrderStatus: (id: number, status: string) =>
    apiClient.put(`/orders/${id}`, { status }),
}

// Reviews API
export const reviewsAPI = {
  getProductReviews: (productId: number, params?: { page?: number; page_size?: number }) =>
    apiClient.get(`/reviews/product/${productId}`, { params }),
  
  getMyReviews: (params?: { page?: number; page_size?: number }) =>
    apiClient.get('/reviews/my', { params }),
  
  createReview: (data: { product_id: number; rating: number; comment?: string }) =>
    apiClient.post('/reviews', data),
  
  updateReview: (id: number, data: { rating?: number; comment?: string }) =>
    apiClient.put(`/reviews/${id}`, data),
  
  deleteReview: (id: number) => apiClient.delete(`/reviews/${id}`),
}

// User API
export const userAPI = {
  getProfile: () => apiClient.get('/users/me'),
  
  updateProfile: (data: { name?: string; phone?: string; address?: string }) =>
    apiClient.put('/users/me', data),
  
  changePassword: (data: { current_password: string; new_password: string }) =>
    apiClient.post('/users/me/change-password', data),
  
  getUsers: (params?: { page?: number; page_size?: number }) =>
    apiClient.get('/users', { params }),
  
  updateUser: (id: number, data: {
    name?: string
    phone?: string
    address?: string
    is_active?: number
    is_admin?: number
  }) => apiClient.put(`/users/${id}`, data),
}

