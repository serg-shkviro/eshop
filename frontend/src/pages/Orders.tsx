import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { ordersAPI, cartAPI } from '../api/client'

interface OrderItem {
  id: number
  product_id: number
  quantity: number
  price: string
  product: {
    name: string
  }
}

interface Order {
  id: number
  total_amount: string
  status: string
  shipping_address: string
  payment_method?: string
  created_at: string
  order_items: OrderItem[]
}

const Orders = () => {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [showCheckoutForm, setShowCheckoutForm] = useState(false)
  const [checkoutData, setCheckoutData] = useState({
    shipping_address: '',
    payment_method: '',
    notes: '',
  })
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [searchParams] = useSearchParams()
  const isCheckout = searchParams.get('checkout') === 'true'
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    page_size: 20,
    total_pages: 1,
    has_next: false,
    has_previous: false,
  })

  const loadOrders = useCallback(async () => {
    setLoading(true)
    try {
      const response = await ordersAPI.getOrders({ 
        page: pagination.page,
        page_size: pagination.page_size
      })
      setOrders(response.data.items || [])
      if (response.data.pagination) {
        setPagination(response.data.pagination)
      }
    } catch (error) {
      console.error('Failed to load orders:', error)
    } finally {
      setLoading(false)
    }
  }, [pagination.page, pagination.page_size])

  useEffect(() => {
    if (isCheckout) {
      setShowCheckoutForm(true)
    }
    loadOrders()
  }, [isCheckout, loadOrders])

  const handlePageChange = (newPage: number) => {
    setPagination(prev => ({ ...prev, page: newPage }))
  }

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage(null)
    try {
      await ordersAPI.createOrder(checkoutData)
      setShowCheckoutForm(false)
      setCheckoutData({ shipping_address: '', payment_method: '', notes: '' })
      await loadOrders()
      // Clear cart after successful order
      try {
        await cartAPI.clearCart()
      } catch (error) {
        // Cart might already be cleared by backend
      }
      setMessage({ type: 'success', text: 'Заказ успешно оформлен!' })
      setTimeout(() => setMessage(null), 3000)
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Не удалось создать заказ' })
      setTimeout(() => setMessage(null), 5000)
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
      
      <h1 className="text-3xl font-bold mb-6">Мои заказы</h1>

      {showCheckoutForm && (
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
          <h2 className="text-2xl font-bold mb-4">Оформление заказа</h2>
          <form onSubmit={handleCheckout}>
            <div className="mb-4">
              <label className="block mb-2">Адрес доставки *</label>
              <textarea
                value={checkoutData.shipping_address}
                onChange={(e) =>
                  setCheckoutData({ ...checkoutData, shipping_address: e.target.value })
                }
                required
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div className="mb-4">
              <label className="block mb-2">Способ оплаты</label>
              <input
                type="text"
                value={checkoutData.payment_method}
                onChange={(e) =>
                  setCheckoutData({ ...checkoutData, payment_method: e.target.value })
                }
                placeholder="например, Банковская карта, PayPal"
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div className="mb-4">
              <label className="block mb-2">Примечания</label>
              <textarea
                value={checkoutData.notes}
                onChange={(e) =>
                  setCheckoutData({ ...checkoutData, notes: e.target.value })
                }
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div className="flex space-x-4">
              <button
                type="submit"
                className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
              >
                Оформить заказ
              </button>
              <button
                type="button"
                onClick={() => setShowCheckoutForm(false)}
                className="bg-gray-300 text-gray-700 px-6 py-2 rounded hover:bg-gray-400"
              >
                Отмена
              </button>
            </div>
          </form>
        </div>
      )}

      {orders.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">Заказов пока нет</p>
          <button
            onClick={() => setShowCheckoutForm(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            Создать заказ из корзины
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <div key={order.id} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold">Заказ №{order.id}</h3>
                  <p className="text-gray-600">
                    {new Date(order.created_at).toLocaleString('ru-RU')}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-blue-600">
                    {parseFloat(order.total_amount).toFixed(2)} ₽
                  </p>
                  <span
                    className={`inline-block px-3 py-1 rounded text-sm mt-2 ${
                      order.status === 'delivered'
                        ? 'bg-green-100 text-green-800'
                        : order.status === 'cancelled'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                  >
                    {order.status === 'pending' ? 'ОЖИДАНИЕ' : 
                     order.status === 'confirmed' ? 'ПОДТВЕРЖДЕН' :
                     order.status === 'shipped' ? 'ОТПРАВЛЕН' :
                     order.status === 'delivered' ? 'ДОСТАВЛЕН' :
                     order.status === 'cancelled' ? 'ОТМЕНЕН' : order.status.toUpperCase()}
                  </span>
                </div>
              </div>

              <div className="mb-4">
                <p className="text-gray-700">
                  <strong>Доставка:</strong> {order.shipping_address}
                </p>
                {order.payment_method && (
                  <p className="text-gray-700">
                    <strong>Оплата:</strong> {order.payment_method}
                  </p>
                )}
              </div>

              <div className="border-t pt-4">
                <h4 className="font-bold mb-2">Товары:</h4>
                <ul className="space-y-2">
                  {order.order_items.map((item) => (
                    <li key={item.id} className="flex justify-between">
                      <span>
                        {item.product.name} x {item.quantity}
                      </span>
                      <span>{parseFloat(item.price).toFixed(2)} ₽</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      )}

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

export default Orders

