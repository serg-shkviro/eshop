import { useState, useEffect } from 'react'
import { userAPI } from '../api/client'
import { useAuth } from '../contexts/AuthContext'

const Profile = () => {
  const { user: authUser } = useAuth()
  const [user, setUser] = useState(authUser)
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    address: '',
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [showPasswordForm, setShowPasswordForm] = useState(false)
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })
  const [changingPassword, setChangingPassword] = useState(false)

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const response = await userAPI.getProfile()
      setUser(response.data)
      setFormData({
        name: response.data.name || '',
        phone: response.data.phone || '',
        address: response.data.address || '',
      })
    } catch (error) {
      console.error('Failed to load profile:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setMessage(null)
    try {
      const response = await userAPI.updateProfile(formData)
      setUser(response.data)
      setMessage({ type: 'success', text: 'Профиль успешно обновлен!' })
      setTimeout(() => setMessage(null), 3000)
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Не удалось обновить профиль' })
      setTimeout(() => setMessage(null), 5000)
    } finally {
      setSaving(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage(null)
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage({ type: 'error', text: 'Новые пароли не совпадают' })
      setTimeout(() => setMessage(null), 5000)
      return
    }
    
    if (passwordData.new_password.length < 6) {
      setMessage({ type: 'error', text: 'Новый пароль должен быть не менее 6 символов' })
      setTimeout(() => setMessage(null), 5000)
      return
    }
    
    setChangingPassword(true)
    try {
      await userAPI.changePassword({
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      })
      setMessage({ type: 'success', text: 'Пароль успешно изменен!' })
      setShowPasswordForm(false)
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      })
      setTimeout(() => setMessage(null), 3000)
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Не удалось изменить пароль' })
      setTimeout(() => setMessage(null), 5000)
    } finally {
      setChangingPassword(false)
    }
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      {message && (
        <div className={`px-4 py-3 rounded mb-4 ${
          message.type === 'success' 
            ? 'bg-green-100 border border-green-400 text-green-700' 
            : 'bg-red-100 border border-red-400 text-red-700'
        }`}>
          {message.text}
        </div>
      )}
      
      <h1 className="text-3xl font-bold mb-6">Мой профиль</h1>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="mb-4">
          <p className="text-gray-600">Email</p>
          <p className="font-bold">{user?.email}</p>
        </div>
        <div className="mb-4">
          <p className="text-gray-600">ID пользователя</p>
          <p className="font-bold">{user?.id}</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-2xl font-bold mb-4">Обновить профиль</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Имя
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
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
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Адрес
            </label>
            <textarea
              name="address"
              value={formData.address}
              onChange={handleChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={saving}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Сохранение...' : 'Сохранить изменения'}
          </button>
        </form>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Изменить пароль</h2>
          <button
            onClick={() => {
              setShowPasswordForm(!showPasswordForm)
              if (showPasswordForm) {
                setPasswordData({
                  current_password: '',
                  new_password: '',
                  confirm_password: '',
                })
              }
            }}
            className="text-blue-600 hover:text-blue-700"
          >
            {showPasswordForm ? 'Отмена' : 'Изменить пароль'}
          </button>
        </div>

        {showPasswordForm && (
          <form onSubmit={handlePasswordChange}>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2">
                Текущий пароль *
              </label>
              <input
                type="password"
                value={passwordData.current_password}
                onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2">
                Новый пароль *
              </label>
              <input
                type="password"
                value={passwordData.new_password}
                onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                required
                minLength={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-sm text-gray-500 mt-1">Минимум 6 символов</p>
            </div>

            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-bold mb-2">
                Подтвердите новый пароль *
              </label>
              <input
                type="password"
                value={passwordData.confirm_password}
                onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                required
                minLength={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              type="submit"
              disabled={changingPassword}
              className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {changingPassword ? 'Изменение...' : 'Изменить пароль'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}

export default Profile

