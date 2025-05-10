import { NextResponse } from 'next/server';

// Return static mock test data shaped for graph visualization
export async function GET() {
  const mockGraphData = [
    {
      id: 1,
      name: 'User Authentication',
      status: 'passed',
      code: "// Test code for login flow\nawait request.post('/api/auth/login').send({ username: 'user', password: 'pass' }).expect(200);",
      endpoint: {
        path: '/auth/login',
        method: 'POST',
      },
      lastRun: '2025-04-15T14:32:00Z',
      duration: 242,
      errorMessage: undefined,
      servicesVisited: ['auth-service'],
    },
    {
      id: 2,
      name: 'Product Listing',
      status: 'passed',
      code: "// Test code for product list\nconst res = await request.get('/api/products?limit=10&category=electronics').expect(200);\nexpect(res.body.length).toBe(10);",
      endpoint: {
        path: '/api/products',
        method: 'GET',
        params: { limit: '10', category: 'electronics' },
      },
      lastRun: '2025-04-15T14:33:10Z',
      duration: 156,
      errorMessage: undefined,
      servicesVisited: ['product-service', 'cache-service'],
    },
    {
      id: 3,
      name: 'Order Creation',
      status: 'failed',
      code: "// Test code for order creation\nawait request.post('/api/orders/create').send({ userId: 'user_123', items: [...] }).expect(201);",
      endpoint: {
        path: '/api/orders/create',
        method: 'POST',
      },
      lastRun: '2025-04-15T14:34:22Z',
      duration: 510,
      errorMessage: 'Timeout waiting for payment processing',
      servicesVisited: ['order-service', 'payment-service'],
    },
    {
      id: 4,
      name: 'User Profile Update',
      status: 'pending',
      code: "// Test code for profile update\n// Not yet implemented",
      endpoint: {
        path: '/api/users/:userId',
        method: 'PUT',
        params: { userId: 'user_12345' },
      },
      lastRun: '2025-04-15T14:35:00Z',
      duration: 0,
      errorMessage: undefined,
      servicesVisited: [],
    },
    {
      id: 5,
      name: 'Product Search',
      status: 'passed',
      code: "// Test code for search\nconst res = await request.get('/api/search?query=smartphone&sort=price_asc').expect(200);\nexpect(res.body.results).toBeDefined();",
      endpoint: {
        path: '/api/search',
        method: 'GET',
        params: { query: 'smartphone', sort: 'price_asc' },
      },
      lastRun: '2025-04-15T14:36:15Z',
      duration: 189,
      errorMessage: undefined,
      servicesVisited: ['search-service'],
    },
  ];

  return NextResponse.json(mockGraphData);
}