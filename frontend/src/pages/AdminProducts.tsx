import { useState, useEffect, useRef } from 'react'
import { productsAPI, categoriesAPI } from '../api/client'

interface Product {
  id: number
  name: string
  description?: string
  price: string
  stock: number
  category_id?: number
  category?: { id: number; name: string }
  image_url?: string
  is_active: number
}

interface Category {
  id: number
  name: string
}

const AdminProducts = () => {
  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [includeInactive, setIncludeInactive] = useState(false)
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    page_size: 20,
    total_pages: 1,
    has_next: false,
    has_previous: false,
  })
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    stock: '',
    category_id: '',
    image_url: '',
    is_active: '1',
  })
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const isInitialMount = useRef(true)
  const prevIncludeInactive = useRef(false)
  const isLoadingFromFilterChange = useRef(false)
  const prevPageRef = useRef(1)

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
      const response = await productsAPI.getProducts({ 
        page: pagination.page,
        page_size: pagination.page_size,
        include_inactive: includeInactive 
      })
      setProducts(response.data.items || [])
      if (response.data.pagination) {
        setPagination(response.data.pagination)
      }
    } catch (error) {
      console.error('Failed to load products:', error)
      setMessage({ type: 'error', text: 'Не удалось загрузить товары' })
      setTimeout(() => setMessage(null), 5000)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadCategories()
    loadProducts()
    isInitialMount.current = false
    prevIncludeInactive.current = includeInactive
    prevPageRef.current = pagination.page
  }, [])

  useEffect(() => {
    if (isInitialMount.current) return
    
    if (prevIncludeInactive.current !== includeInactive) {
      prevIncludeInactive.current = includeInactive
      
      // Устанавливаем флаг ДО любых изменений состояния
      isLoadingFromFilterChange.current = true
      prevPageRef.current = 1
      
      const loadWithNewFilter = async () => {
        setLoading(true)
        try {
          const response = await productsAPI.getProducts({ 
            page: 1,
            page_size: pagination.page_size,
            include_inactive: includeInactive 
          })
          setProducts(response.data.items || [])
          if (response.data.pagination) {
            const newPagination = { ...response.data.pagination, page: 1 }
            setPagination(newPagination)
          }
        } catch (error) {
          console.error('Failed to load products:', error)
          setMessage({ type: 'error', text: 'Не удалось загрузить товары' })
          setTimeout(() => setMessage(null), 5000)
        } finally {
          setLoading(false)
          // Сбрасываем флаг после завершения всех обновлений состояния
          setTimeout(() => {
            isLoadingFromFilterChange.current = false
          }, 100)
        }
      }
      loadWithNewFilter()
    }
  }, [includeInactive])

  useEffect(() => {
    if (isInitialMount.current) return
    if (isLoadingFromFilterChange.current) {
      // Если это изменение из-за фильтра, не загружаем повторно
      return
    }
    
    // Обновляем prevPageRef только если страница действительно изменилась
    if (prevPageRef.current !== pagination.page) {
      prevPageRef.current = pagination.page
      loadProducts()
    }
  }, [pagination.page, pagination.page_size])

  const handlePageChange = (newPage: number) => {
    setPagination(prev => ({ ...prev, page: newPage }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage(null)
    
    try {
      const productData = {
        name: formData.name,
        description: formData.description || undefined,
        price: parseFloat(formData.price),
        stock: parseInt(formData.stock),
        category_id: formData.category_id ? parseInt(formData.category_id) : undefined,
        image_url: formData.image_url || undefined,
        is_active: parseInt(formData.is_active),
      }

      if (editingProduct) {
        await productsAPI.updateProduct(editingProduct.id, productData)
        setMessage({ type: 'success', text: 'Товар успешно обновлен!' })
      } else {
        await productsAPI.createProduct(productData)
        setMessage({ type: 'success', text: 'Товар успешно создан!' })
      }
      
      setShowForm(false)
      setEditingProduct(null)
      setFormData({
        name: '',
        description: '',
        price: '',
        stock: '',
        category_id: '',
        image_url: '',
        is_active: '1',
      })
      loadProducts()
      setTimeout(() => setMessage(null), 3000)
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Не удалось сохранить товар' })
      setTimeout(() => setMessage(null), 5000)
    }
  }

  const handleEdit = (product: Product) => {
    setEditingProduct(product)
    setFormData({
      name: product.name,
      description: product.description || '',
      price: product.price,
      stock: product.stock.toString(),
      category_id: product.category_id?.toString() || '',
      image_url: product.image_url || '',
      is_active: product.is_active.toString(),
    })
    setShowForm(true)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить этот товар?')) return
    
    setMessage(null)
    try {
      await productsAPI.deleteProduct(id)
      setMessage({ type: 'success', text: 'Товар успешно удален!' })
      await loadProducts()
      setTimeout(() => setMessage(null), 3000)
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Не удалось удалить товар' })
      setTimeout(() => setMessage(null), 5000)
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingProduct(null)
    setFormData({
      name: '',
      description: '',
      price: '',
      stock: '',
      category_id: '',
      image_url: '',
      is_active: '1',
    })
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    )
  }

  return (
    <div>
      {message && (
        <div className={`px-4 py-3 rounded mb-4 ${
          message.type === 'success' 
            ? 'bg-green-100 border border-green-400 text-green-700' 
            : 'bg-red-100 border border-red-400 text-red-700'
        }`}>
          {message.text}
        </div>
      )}

      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Управление товарами</h1>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={includeInactive}
              onChange={(e) => setIncludeInactive(e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Показать неактивные товары</span>
          </label>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {showForm ? 'Отмена' : '+ Добавить товар'}
        </button>
        </div>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4">
            {editingProduct ? 'Редактировать товар' : 'Создать товар'}
          </h2>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Название *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Цена *
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.price}
                  onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Количество на складе *
                </label>
                <input
                  type="number"
                  min="0"
                  value={formData.stock}
                  onChange={(e) => setFormData({ ...formData, stock: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Категория
                </label>
                <select
                  value={formData.category_id}
                  onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Без категории</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  URL изображения
                </label>
                <input
                  type="url"
                  value={formData.image_url}
                  onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Статус
                </label>
                <select
                  value={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="1">Активен</option>
                  <option value="0">Неактивен</option>
                </select>
              </div>
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2">
                Описание
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex space-x-4">
              <button
                type="submit"
                className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
              >
                {editingProduct ? 'Сохранить' : 'Создать'}
              </button>
              <button
                type="button"
                onClick={handleCancel}
                className="bg-gray-300 text-gray-700 px-6 py-2 rounded hover:bg-gray-400"
              >
                Отмена
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Название
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Цена
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Склад
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Категория
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Статус
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {products.map((product) => (
              <tr key={product.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {product.id}
                </td>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">
                  {product.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {parseFloat(product.price).toFixed(2)} ₽
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {product.stock}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {product.category?.name || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <span className={`px-2 py-1 rounded ${
                    product.is_active === 1 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {product.is_active === 1 ? 'Активен' : 'Неактивен'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => handleEdit(product)}
                    className="text-blue-600 hover:text-blue-900 mr-4"
                  >
                    Редактировать
                  </button>
                  <button
                    onClick={() => handleDelete(product.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {products.length === 0 && !loading && (
          <div className="text-center py-12 text-gray-500">
            Товары не найдены
          </div>
        )}
      </div>

      {pagination.total_pages > 1 && (
        <div className="flex justify-center items-center space-x-2 mt-8">
          <button
            onClick={() => handlePageChange(pagination.page - 1)}
            disabled={!pagination.has_previous}
            className="px-4 py-2 border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Назад
          </button>
          <span className="px-4">
            Страница {pagination.page} из {pagination.total_pages} (Всего: {pagination.total})
          </span>
          <button
            onClick={() => handlePageChange(pagination.page + 1)}
            disabled={!pagination.has_next}
            className="px-4 py-2 border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
          >
            Вперед
          </button>
        </div>
      )}
    </div>
  )
}

export default AdminProducts

