import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { productsAPI, categoriesAPI } from '../api/client'

interface Product {
  id: number
  name: string
  description: string
  price: string
  stock: number
  image_url?: string
  category?: { id: number; name: string }
}

interface Category {
  id: number
  name: string
}

const Products = () => {
  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    search: '',
    category_id: '',
    min_price: '',
    max_price: '',
    in_stock: false,
    page: 1,
    page_size: 20,
  })
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    page_size: 20,
    total_pages: 1,
    has_next: false,
    has_previous: false,
  })

  useEffect(() => {
    loadCategories()
  }, [])

  useEffect(() => {
    loadProducts()
  }, [filters])

  const loadCategories = async () => {
    try {
      const response = await categoriesAPI.getCategories({ page_size: 100 })
      setCategories(response.data.items || [])
    } catch (error) {
      console.error('Failed to load categories:', error)
    }
  }

  const loadProducts = async () => {
    setLoading(true)
    try {
      const params: any = {
        page: filters.page,
        page_size: filters.page_size,
      }
      
      if (filters.search) params.search = filters.search
      if (filters.category_id) params.category_id = parseInt(filters.category_id)
      if (filters.min_price) params.min_price = parseFloat(filters.min_price)
      if (filters.max_price) params.max_price = parseFloat(filters.max_price)
      if (filters.in_stock) params.in_stock = true

      const response = await productsAPI.getProducts(params)
      setProducts(response.data.items || [])
      setPagination(response.data.pagination || pagination)
    } catch (error) {
      console.error('Failed to load products:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (key: string, value: any) => {
    if (key === 'page') {
      setFilters({ ...filters, page: value })
    } else {
      setFilters({ ...filters, [key]: value, page: 1 })
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Товары</h1>
      
      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <input
            type="text"
            placeholder="Поиск товаров..."
            value={filters.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          />
          
          <select
            value={filters.category_id}
            onChange={(e) => handleFilterChange('category_id', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="">Все категории</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
          
          <input
            type="number"
            placeholder="Мин. цена"
            value={filters.min_price}
            onChange={(e) => handleFilterChange('min_price', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          />
          
          <input
            type="number"
            placeholder="Макс. цена"
            value={filters.max_price}
            onChange={(e) => handleFilterChange('max_price', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          />
          
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={filters.in_stock}
              onChange={(e) => handleFilterChange('in_stock', e.target.checked)}
              className="mr-2"
            />
            Только в наличии
          </label>
        </div>
      </div>

      {/* Products Grid */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      ) : products.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          Товары не найдены
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {products.map((product) => (
              <Link
                key={product.id}
                to={`/products/${product.id}`}
                className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow"
              >
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="w-full h-48 object-cover"
                  />
                ) : (
                  <div className="w-full h-48 bg-gray-200 flex items-center justify-center">
                    <span className="text-gray-400">Нет изображения</span>
                  </div>
                )}
                <div className="p-4">
                  <h3 className="font-bold text-lg mb-2">{product.name}</h3>
                  <p className="text-gray-600 text-sm mb-2 line-clamp-2">
                    {product.description}
                  </p>
                  <div className="flex justify-between items-center">
                    <span className="text-xl font-bold text-blue-600">
                      {parseFloat(product.price).toFixed(2)} ₽
                    </span>
                    <span
                      className={`text-sm ${
                        product.stock > 0 ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {product.stock > 0 ? 'В наличии' : 'Нет в наличии'}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {pagination.total_pages > 1 && (
            <div className="flex justify-center items-center space-x-2 mt-8">
              <button
                onClick={() => handleFilterChange('page', pagination.page - 1)}
                disabled={!pagination.has_previous}
                className="px-4 py-2 border rounded disabled:opacity-50"
              >
                Назад
              </button>
              <span className="px-4">
                Страница {pagination.page} из {pagination.total_pages}
              </span>
              <button
                onClick={() => handleFilterChange('page', pagination.page + 1)}
                disabled={!pagination.has_next}
                className="px-4 py-2 border rounded disabled:opacity-50"
              >
                Вперед
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default Products

