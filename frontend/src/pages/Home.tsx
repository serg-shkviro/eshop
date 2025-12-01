import { Link } from 'react-router-dom'

const Home = () => {
  return (
    <div className="text-center">
      <h1 className="text-4xl font-bold text-gray-800 mb-4">
        Добро пожаловать в интернет-магазин
      </h1>
      <p className="text-xl text-gray-600 mb-8">
        Откройте для себя удивительные товары по отличным ценам
      </p>
      <div className="flex justify-center space-x-4">
        <Link
          to="/products"
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 text-lg"
        >
          Просмотреть товары
        </Link>
      </div>
    </div>
  )
}

export default Home

