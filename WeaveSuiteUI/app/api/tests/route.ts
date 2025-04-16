/* Mock data for system tests
export interface SystemTest {
    id: string;
    name: string;
    status: 'passed' | 'failed' | 'pending';
    endpoint: {
        path: string;
        method: string;
        params?: Record<string, string>;
    };
    lastRun: string;
    duration: number; // in milliseconds
    errorMessage?: string;
}*/
  
export async function GET() {

    const mockGraphData = [
      {
        id: 'test-001',
        name: 'User Authentication',
        status: 'passed',
        endpoint: {
          path: '/api/auth/login',
          method: 'POST',
        },
        lastRun: '2025-04-15T14:32:00Z',
        duration: 242,
      },
      {
        id: 'test-002',
        name: 'Product Listing',
        status: 'passed',
        endpoint: {
          path: '/api/products',
          method: 'GET',
          params: { limit: '10', category: 'electronics' }
        },
        lastRun: '2025-04-15T14:33:10Z',
        duration: 156,
      },
      {
        id: 'test-003',
        name: 'Order Creation',
        status: 'failed',
        endpoint: {
          path: '/api/orders/create',
          method: 'POST',
        },
        lastRun: '2025-04-15T14:34:22Z',
        duration: 510,
        errorMessage: 'Timeout waiting for payment processing',
      },
      {
        id: 'test-004',
        name: 'User Profile Update',
        status: 'pending',
        endpoint: {
          path: '/api/users/:userId',
          method: 'PUT',
          params: { userId: 'user_12345' }
        },
        lastRun: '2025-04-15T14:35:00Z',
        duration: 0,
      },
      {
        id: 'test-005',
        name: 'Product Search',
        status: 'passed',
        endpoint: {
          path: '/api/search',
          method: 'GET',
          params: { query: 'smartphone', sort: 'price_asc' }
        },
        lastRun: '2025-04-15T14:36:15Z',
        duration: 189,
      }
    ];

    return Response.json(mockGraphData);
}