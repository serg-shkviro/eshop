import { useState, useEffect, useCallback } from 'react'
import { categoriesAPI } from '../api/client'

interface Category {
  id: number
  name: string
  description?: string
  created_at?: string
}

const AdminCategories = () => {
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingCategory, setEditingCategory] = useState<Category | null>(null)
  const [formData, setFormData] = useState({ name: '', description: '' })
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    page_size: 20,
    total_pages: 1,
    has_next: false,
    has_previous: false,
  })

  const loadCategories = useCallback(async () => {
    setLoading(true)
    try {
      const response = await categoriesAPI.getCategories({ 
        page: pagination.page,
        page_size: pagination.page_size
      })
      setCategories(response.data.items || [])
      if (response.data.pagination) {
        setPagination(response.data.pagination)
      }
    } catch (error) {
      console.error('Failed to load categories:', error)
      setMessage({ type: 'error', text: 'Не удалось загрузить категории' })
      setTimeout(() => setMessage(null), 5000)
    } finally {
      setLoading(false)
    }
  }, [pagination.page, pagination.page_size])

  useEffect(() => {
    loadCategories()
  }, [loadCategories])

  const handlePageChange = (newPage: number) => {
    setPagination(prev => ({ ...prev, page: newPage }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage(null)
    
    try {
      if (editingCategory) {
        await categoriesAPI.updateCategory(editingCategory.id, formData)
        setMessage({ type: 'success', text: 'Категория успешно обновлена!' })
      } else {
        await categoriesAPI.createCategory(formData)
        setMessage({ type: 'success', text: 'Категория успешно создана!' })
      }
      
      setShowForm(false)
      setEditingCategory(null)
      setFormData({ name: '', description: '' })
      await loadCategories()
      setTimeout(() => setMessage(null), 3000)
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Не удалось сохранить категорию' })
      setTimeout(() => setMessage(null), 5000)
    }
  }

  const handleEdit = (category: Category) => {
    setEditingCategory(category)
    setFormData({ name: category.name, description: category.description || '' })
    setShowForm(true)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить эту категорию?')) return
    
    setMessage(null)
    try {
      await categoriesAPI.deleteCategory(id)
      setMessage({ type: 'success', text: 'Категория успешно удалена!' })
      await loadCategories()
      setTimeout(() => setMessage(null), 3000)
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Не удалось удалить категорию' })
      setTimeout(() => setMessage(null), 5000)
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingCategory(null)
    setFormData({ name: '', description: '' })
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
        <h1 className="text-3xl font-bold">Управление категориями</h1>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {showForm ? 'Отмена' : '+ Добавить категорию'}
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4">
            {editingCategory ? 'Редактировать категорию' : 'Создать категорию'}
          </h2>
          <form onSubmit={handleSubmit}>
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
                Описание
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex space-x-4">
              <button
                type="submit"
                className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
              >
                {editingCategory ? 'Сохранить' : 'Создать'}
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
                Описание
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {categories.map((category) => (
              <tr key={category.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {category.id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {category.name}
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {category.description || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => handleEdit(category)}
                    className="text-blue-600 hover:text-blue-900 mr-4"
                  >
                    Редактировать
                  </button>
                  <button
                    onClick={() => handleDelete(category.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {categories.length === 0 && !loading && (
          <div className="text-center py-12 text-gray-500">
            Категории не найдены
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

export default AdminCategories

