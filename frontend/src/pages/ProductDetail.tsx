import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { productsAPI, reviewsAPI, cartAPI } from '../api/client'
import { useAuth } from '../contexts/AuthContext'

interface Product {
  id: number
  name: string
  description: string
  price: string
  stock: number
  image_url?: string
  category?: { id: number; name: string }
}

interface Review {
  id: number
  rating: number
  comment?: string
  user: { name: string }
  created_at: string
}

const ProductDetail = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const [product, setProduct] = useState<Product | null>(null)
  const [reviews, setReviews] = useState<Review[]>([])
  const [quantity, setQuantity] = useState(1)
  const [loading, setLoading] = useState(true)
  const [addingToCart, setAddingToCart] = useState(false)
  const [reviewForm, setReviewForm] = useState({ rating: 5, comment: '' })
  const [showReviewForm, setShowReviewForm] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  useEffect(() => {
    if (id) {
      loadProduct()
      loadReviews()
    }
  }, [id])

  const loadProduct = async () => {
    try {
      const response = await productsAPI.getProduct(parseInt(id!))
      setProduct(response.data)
    } catch (error) {
      console.error('Failed to load product:', error)
      setMessage({ type: 'error', text: 'Не удалось загрузить товар' })
    } finally {
      setLoading(false)
    }
  }

  const loadReviews = async () => {
    try {
      const response = await reviewsAPI.getProductReviews(parseInt(id!))
      setReviews(response.data.items || response.data || [])
    } catch (error: any) {
      console.error('Failed to load reviews:', error)
      setReviews([])
    }
  }

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }

    setAddingToCart(true)
    setMessage(null)
    try {
      await cartAPI.addToCart(product!.id, quantity)
      setMessage({ type: 'success', text: 'Товар добавлен в корзину!' })
      setTimeout(() => setMessage(null), 3000)
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Не удалось добавить в корзину' })
      setTimeout(() => setMessage(null), 5000)
    } finally {
      setAddingToCart(false)
    }
  }

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage(null)
    try {
      await reviewsAPI.createReview({
        product_id: product!.id,
        rating: reviewForm.rating,
        comment: reviewForm.comment || undefined,
      })
      setShowReviewForm(false)
      setReviewForm({ rating: 5, comment: '' })
      setMessage({ type: 'success', text: 'Отзыв успешно отправлен!' })
      setTimeout(() => setMessage(null), 3000)
      await loadReviews()
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Не удалось отправить отзыв' })
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

  if (!product) {
    return <div className="text-center py-12">Товар не найден</div>
  }

  return (
    <div className="max-w-6xl mx-auto">
      {message && (
        <div className={`px-4 py-3 rounded mb-4 ${
          message.type === 'success' 
            ? 'bg-green-100 border border-green-400 text-green-700' 
            : 'bg-red-100 border border-red-400 text-red-700'
        }`}>
          {message.text}
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        {/* Product Image */}
        <div>
          {product.image_url ? (
            <img
              src={product.image_url}
              alt={product.name}
              className="w-full rounded-lg shadow-md"
            />
          ) : (
            <div className="w-full h-96 bg-gray-200 rounded-lg flex items-center justify-center">
              <span className="text-gray-400">Нет изображения</span>
            </div>
          )}
        </div>

        {/* Product Info */}
        <div>
          <h1 className="text-3xl font-bold mb-4">{product.name}</h1>
          {product.category && (
            <p className="text-gray-600 mb-4">Категория: {product.category.name}</p>
          )}
          <p className="text-4xl font-bold text-blue-600 mb-4">
            {parseFloat(product.price).toFixed(2)} ₽
          </p>
          <p className="text-gray-700 mb-6">{product.description}</p>
          
          <div className="mb-6">
            <span
              className={`inline-block px-3 py-1 rounded ${
                product.stock > 0
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}
            >
              {product.stock > 0 ? `В наличии: ${product.stock} шт.` : 'Нет в наличии'}
            </span>
          </div>

          {product.stock > 0 && (
            <div className="mb-6">
              <label className="block mb-2">Количество:</label>
              <input
                type="number"
                min="1"
                max={product.stock}
                value={quantity}
                onChange={(e) => setQuantity(parseInt(e.target.value))}
                className="w-20 px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
          )}

          <button
            onClick={handleAddToCart}
            disabled={product.stock === 0 || addingToCart}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {addingToCart ? 'Добавление...' : 'Добавить в корзину'}
          </button>
        </div>
      </div>

      {/* Reviews Section */}
      <div className="mt-12">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Отзывы</h2>
          {isAuthenticated && (
            <button
              onClick={() => setShowReviewForm(!showReviewForm)}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              {showReviewForm ? 'Отмена' : 'Написать отзыв'}
            </button>
          )}
        </div>

        {showReviewForm && (
          <form onSubmit={handleSubmitReview} className="bg-white p-6 rounded-lg shadow-md mb-6">
            <div className="mb-4">
              <label className="block mb-2">Оценка:</label>
              <select
                value={reviewForm.rating}
                onChange={(e) =>
                  setReviewForm({ ...reviewForm, rating: parseInt(e.target.value) })
                }
                className="px-3 py-2 border border-gray-300 rounded-md"
              >
                {[5, 4, 3, 2, 1].map((r) => (
                  <option key={r} value={r}>
                    {r} {r === 1 ? 'звезда' : r < 5 ? 'звезды' : 'звезд'}
                  </option>
                ))}
              </select>
            </div>
            <div className="mb-4">
              <label className="block mb-2">Комментарий:</label>
              <textarea
                value={reviewForm.comment}
                onChange={(e) =>
                  setReviewForm({ ...reviewForm, comment: e.target.value })
                }
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <button
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Отправить отзыв
            </button>
          </form>
        )}

        {reviews.length === 0 ? (
          <p className="text-gray-500">Отзывов пока нет</p>
        ) : (
          <div className="space-y-4">
            {reviews.map((review) => (
              <div key={review.id} className="bg-white p-4 rounded-lg shadow-md">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <p className="font-bold">{review.user?.name || 'Анонимный пользователь'}</p>
                    <div className="flex items-center">
                      {[...Array(5)].map((_, i) => (
                        <span
                          key={i}
                          className={i < review.rating ? 'text-yellow-400' : 'text-gray-300'}
                        >
                          ★
                        </span>
                      ))}
                    </div>
                  </div>
                  <span className="text-sm text-gray-500">
                    {new Date(review.created_at).toLocaleDateString('ru-RU')}
                  </span>
                </div>
                {review.comment && <p className="text-gray-700">{review.comment}</p>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ProductDetail

