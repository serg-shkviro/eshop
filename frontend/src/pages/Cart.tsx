import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { cartAPI } from '../api/client'

interface CartItem {
  id: number
  product_id: number
  quantity: number
  product: {
    id: number
    name: string
    price: string
    image_url?: string
  }
}

const Cart = () => {
  const [cart, setCart] = useState<{ items: CartItem[]; total: string } | null>(null)
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState<number | null>(null)
  const [error, setError] = useState<string>('')
  const [showClearConfirm, setShowClearConfirm] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    loadCart()
  }, [])

  const loadCart = async () => {
    try {
      const response = await cartAPI.getCart()
      setCart(response.data)
    } catch (error) {
      console.error('Failed to load cart:', error)
    } finally {
      setLoading(false)
    }
  }

  const updateQuantity = async (itemId: number, quantity: number) => {
    if (quantity < 1) return
    
    setUpdating(itemId)
    setError('')
    try {
      await cartAPI.updateCartItem(itemId, quantity)
      loadCart()
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Не удалось обновить корзину')
      setTimeout(() => setError(''), 5000)
    } finally {
      setUpdating(null)
    }
  }

  const removeItem = async (itemId: number) => {
    setError('')
    try {
      await cartAPI.removeFromCart(itemId)
      loadCart()
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Не удалось удалить товар')
      setTimeout(() => setError(''), 5000)
    }
  }

  const clearCart = async () => {
    setError('')
    try {
      await cartAPI.clearCart()
      loadCart()
      setShowClearConfirm(false)
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Не удалось очистить корзину')
      setTimeout(() => setError(''), 5000)
    }
  }

  const handleCheckout = () => {
    navigate('/orders?checkout=true')
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    )
  }

  if (!cart || cart.items.length === 0) {
    return (
      <div className="text-center py-12">
        <h1 className="text-3xl font-bold mb-4">Ваша корзина пуста</h1>
        <button
          onClick={() => navigate('/products')}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
        >
          Просмотреть товары
        </button>
      </div>
    )
  }

  return (
    <div>
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      {showClearConfirm && (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4 flex justify-between items-center">
          <span>Вы уверены, что хотите очистить корзину?</span>
          <div className="space-x-2">
            <button
              onClick={clearCart}
              className="bg-red-600 text-white px-4 py-1 rounded hover:bg-red-700"
            >
              Да
            </button>
            <button
              onClick={() => setShowClearConfirm(false)}
              className="bg-gray-300 text-gray-700 px-4 py-1 rounded hover:bg-gray-400"
            >
              Нет
            </button>
          </div>
        </div>
      )}

      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Корзина</h1>
        <button
          onClick={() => setShowClearConfirm(true)}
          className="text-red-600 hover:text-red-700"
        >
          Очистить корзину
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            {cart.items.map((item) => (
              <div
                key={item.id}
                className="border-b border-gray-200 p-4 flex items-center space-x-4"
              >
                {item.product.image_url ? (
                  <img
                    src={item.product.image_url}
                    alt={item.product.name}
                    className="w-20 h-20 object-cover rounded"
                  />
                ) : (
                  <div className="w-20 h-20 bg-gray-200 rounded flex items-center justify-center">
                    <span className="text-gray-400 text-xs">Нет изображения</span>
                  </div>
                )}
                
                <div className="flex-1">
                  <h3 className="font-bold">{item.product.name}</h3>
                  <p className="text-gray-600">
                    {parseFloat(item.product.price).toFixed(2)} ₽ за шт.
                  </p>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => updateQuantity(item.id, item.quantity - 1)}
                    disabled={updating === item.id}
                    className="px-2 py-1 border rounded disabled:opacity-50"
                  >
                    -
                  </button>
                  <span className="w-12 text-center">{item.quantity}</span>
                  <button
                    onClick={() => updateQuantity(item.id, item.quantity + 1)}
                    disabled={updating === item.id}
                    className="px-2 py-1 border rounded disabled:opacity-50"
                  >
                    +
                  </button>
                </div>

                <div className="text-right">
                  <p className="font-bold">
                    {(parseFloat(item.product.price) * item.quantity).toFixed(2)} ₽
                  </p>
                  <button
                    onClick={() => removeItem(item.id)}
                    className="text-red-600 hover:text-red-700 text-sm mt-1"
                  >
                    Удалить
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold mb-4">Итого</h2>
            <div className="space-y-2 mb-4">
              <div className="flex justify-between">
                <span>Промежуточная сумма:</span>
                <span>{parseFloat(cart.total).toFixed(2)} ₽</span>
              </div>
              <div className="flex justify-between font-bold text-lg pt-4 border-t">
                <span>Всего:</span>
                <span>{parseFloat(cart.total).toFixed(2)} ₽</span>
              </div>
            </div>
            <button
              onClick={handleCheckout}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700"
            >
              Оформить заказ
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Cart

