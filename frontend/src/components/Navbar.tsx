import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <nav className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="text-2xl font-bold text-blue-600">
            Интернет-магазин
          </Link>
          
          <div className="flex items-center space-x-4">
            <Link to="/products" className="text-gray-700 hover:text-blue-600">
              Товары
            </Link>
            
            {isAuthenticated ? (
              <>
                <Link to="/cart" className="text-gray-700 hover:text-blue-600">
                  Корзина
                </Link>
                <Link to="/orders" className="text-gray-700 hover:text-blue-600">
                  Заказы
                </Link>
                {user?.is_admin === 1 && (
                  <>
                    <Link to="/admin/categories" className="text-gray-700 hover:text-blue-600">
                      Категории
                    </Link>
                    <Link to="/admin/products" className="text-gray-700 hover:text-blue-600">
                      Товары
                    </Link>
                    <Link to="/admin/users" className="text-gray-700 hover:text-blue-600">
                      Пользователи
                    </Link>
                  </>
                )}
                <Link to="/profile" className="text-gray-700 hover:text-blue-600">
                  {user?.name}
                </Link>
                <button
                  onClick={handleLogout}
                  className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
                >
                  Выйти
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-gray-700 hover:text-blue-600">
                  Вход
                </Link>
                <Link
                  to="/register"
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                >
                  Регистрация
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar

