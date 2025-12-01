import { useState, useEffect, useCallback } from 'react'
import { userAPI } from '../api/client'
import { useAuth } from '../contexts/AuthContext'

interface User {
  id: number
  name: string
  email: string
  phone?: string
  address?: string
  is_active: number
  is_admin: number
  created_at?: string
}

const AdminUsers = () => {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    address: '',
    is_active: '1',
    is_admin: '0',
  })
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    page_size: 20,
    total_pages: 1,
    has_next: false,
    has_previous: false,
  })

  const loadUsers = useCallback(async () => {
    setLoading(true)
    try {
      const response = await userAPI.getUsers({ 
        page: pagination.page,
        page_size: pagination.page_size
      })
      setUsers(response.data.items || [])
      if (response.data.pagination) {
        setPagination(response.data.pagination)
      }
    } catch (error) {
      console.error('Failed to load users:', error)
      setMessage({ type: 'error', text: 'Не удалось загрузить пользователей' })
      setTimeout(() => setMessage(null), 5000)
    } finally {
      setLoading(false)
    }
  }, [pagination.page, pagination.page_size])

  useEffect(() => {
    loadUsers()
  }, [loadUsers])

  const handlePageChange = (newPage: number) => {
    setPagination(prev => ({ ...prev, page: newPage }))
  }

  const handleEdit = (user: User) => {
    setEditingUser(user)
    setFormData({
      name: user.name,
      phone: user.phone || '',
      address: user.address || '',
      is_active: user.is_active.toString(),
      is_admin: user.is_admin.toString(),
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingUser) return
    
    setMessage(null)
    try {
      await userAPI.updateUser(editingUser.id, {
        name: formData.name,
        phone: formData.phone || undefined,
        address: formData.address || undefined,
        is_active: parseInt(formData.is_active),
        is_admin: parseInt(formData.is_admin),
      })
      setMessage({ type: 'success', text: 'Пользователь успешно обновлен!' })
      setEditingUser(null)
      setFormData({
        name: '',
        phone: '',
        address: '',
        is_active: '1',
        is_admin: '0',
      })
      await loadUsers()
      setTimeout(() => setMessage(null), 3000)
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Не удалось обновить пользователя' })
      setTimeout(() => setMessage(null), 5000)
    }
  }

  const handleCancel = () => {
    setEditingUser(null)
    setFormData({
      name: '',
      phone: '',
      address: '',
      is_active: '1',
      is_admin: '0',
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

      <h1 className="text-3xl font-bold mb-6">Управление пользователями</h1>

      {editingUser && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4">Редактировать пользователя: {editingUser.email}</h2>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Имя *
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
                  Телефон
                </label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
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
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  Роль
                </label>
                <select
                  value={formData.is_admin}
                  onChange={(e) => setFormData({ ...formData, is_admin: e.target.value })}
                  disabled={editingUser?.id === currentUser?.id}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                >
                  <option value="0">Обычный пользователь</option>
                  <option value="1">Администратор</option>
                </select>
                {editingUser?.id === currentUser?.id && (
                  <p className="text-sm text-gray-500 mt-1">
                    Вы не можете изменить свою собственную роль
                  </p>
                )}
              </div>
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2">
                Адрес
              </label>
              <textarea
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex space-x-4">
              <button
                type="submit"
                className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
              >
                Сохранить
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
                Имя
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Email
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Телефон
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Статус
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Роль
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {users.map((user) => (
              <tr key={user.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {user.id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {user.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {user.email}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {user.phone || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <span className={`px-2 py-1 rounded ${
                    user.is_active === 1 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {user.is_active === 1 ? 'Активен' : 'Неактивен'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <span className={`px-2 py-1 rounded ${
                    user.is_admin === 1 
                      ? 'bg-blue-100 text-blue-800' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {user.is_admin === 1 ? 'Администратор' : 'Пользователь'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  {user.id === currentUser?.id ? (
                    <span className="text-gray-400">Текущий пользователь</span>
                  ) : (
                    <button
                      onClick={() => handleEdit(user)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Редактировать
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {users.length === 0 && !loading && (
          <div className="text-center py-12 text-gray-500">
            Пользователи не найдены
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

export default AdminUsers

