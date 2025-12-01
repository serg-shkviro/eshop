# Frontend for E-Commerce API

This directory contains the frontend application for the E-Commerce API.

## Framework Options

You can use any modern frontend framework. Here are some popular choices:

### React (Recommended)
```bash
npx create-react-app . --template typescript
# or
npm create vite@latest . -- --template react-ts
```

### Vue.js
```bash
npm create vue@latest .
# or
npm create vite@latest . -- --template vue-ts
```

### Svelte
```bash
npm create vite@latest . -- --template svelte-ts
```

### Next.js (React with SSR)
```bash
npx create-next-app@latest . --typescript --tailwind --app
```

## Setup Instructions

1. **Choose your framework** and initialize it in this directory
2. **Install dependencies**: `npm install` or `yarn install`
3. **Configure API endpoint**: Update your API base URL to `http://localhost:8000`
4. **Start development server**: `npm run dev` or `yarn dev`

## API Integration

### Base URL
```
http://localhost:8000
```

### Authentication
The API uses JWT Bearer tokens. Store the token after login:

```javascript
// After login
const response = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    username: email,
    password: password
  })
});

const { access_token } = await response.json();
localStorage.setItem('token', access_token);
```

### Making Authenticated Requests
```javascript
const token = localStorage.getItem('token');
const response = await fetch('http://localhost:8000/cart', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

## Example API Client

Create an API client utility:

```javascript
// api/client.js
const API_BASE = 'http://localhost:8000';

export const apiClient = {
  async request(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    
    return response.json();
  },
  
  // Auth
  register(data) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ username: email, password }),
    });
  },
  
  // Products
  getProducts(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/products/?${query}`);
  },
  
  // Cart
  getCart() {
    return this.request('/cart');
  },
  
  addToCart(productId, quantity) {
    return this.request('/cart/items', {
      method: 'POST',
      body: JSON.stringify({ product_id: productId, quantity }),
    });
  },
  
  // Orders
  createOrder(orderData) {
    return this.request('/orders', {
      method: 'POST',
      body: JSON.stringify(orderData),
    });
  },
};
```

## Development

### Option 1: Separate Frontend Service (Recommended)

Run frontend and backend separately:

```bash
# Terminal 1: Backend
docker compose up

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Option 2: Build and Serve from FastAPI

1. Build your frontend:
```bash
cd frontend
npm run build
```

2. The built files will be served automatically by FastAPI at the root URL

## Docker Integration

See `docker-compose.yml` for frontend service configuration.

