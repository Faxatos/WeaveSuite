export async function GET() {
  // Mock data for microservices graph
  const mockGraphData = {
    nodes: [
      { 
        data: { 
          id: 'api-gateway', 
          label: 'API Gateway',
          serviceType: 'gateway'
        },
        position: { x: 300, y: 100 }
      },
      { 
        data: { 
          id: 'auth-service', 
          label: 'Authentication Service',
          serviceType: 'microservice'
        },
        position: { x: 150, y: 200 }
      },
      { 
        data: { 
          id: 'user-service', 
          label: 'User Service',
          serviceType: 'microservice'
        },
        position: { x: 300, y: 300 }
      },
      { 
        data: { 
          id: 'product-service', 
          label: 'Product Service',
          serviceType: 'microservice'
        },
        position: { x: 450, y: 200 }
      },
      { 
        data: { 
          id: 'order-service', 
          label: 'Order Service',
          serviceType: 'microservice'
        },
        position: { x: 500, y: 300 }
      },
      { 
        data: { 
          id: 'notification-service', 
          label: 'Notification Service',
          serviceType: 'microservice'
        },
        position: { x: 200, y: 400 }
      },
      { 
        data: { 
          id: 'payment-service', 
          label: 'Payment Service',
          serviceType: 'microservice'
        },
        position: { x: 400, y: 400 }
      }
    ],
    edges: [
      { 
        data: { 
          id: 'e1', 
          source: 'api-gateway', 
          target: 'auth-service',
          label: 'authenticates'
        } 
      },
      { 
        data: { 
          id: 'e2', 
          source: 'api-gateway', 
          target: 'user-service',
          label: 'routes'
        } 
      },
      { 
        data: { 
          id: 'e3', 
          source: 'api-gateway', 
          target: 'product-service',
          label: 'routes'
        } 
      },
      { 
        data: { 
          id: 'e4', 
          source: 'api-gateway', 
          target: 'order-service',
          label: 'routes'
        } 
      },
      { 
        data: { 
          id: 'e5', 
          source: 'order-service', 
          target: 'payment-service',
          label: 'processes payment'
        } 
      },
      { 
        data: { 
          id: 'e6', 
          source: 'order-service', 
          target: 'notification-service',
          label: 'sends updates'
        } 
      },
      { 
        data: { 
          id: 'e7', 
          source: 'user-service', 
          target: 'notification-service',
          label: 'sends notifications'
        } 
      },
      { 
        data: { 
          id: 'e8', 
          source: 'product-service', 
          target: 'order-service',
          label: 'provides details'
        } 
      }
    ]
  };

  return Response.json(mockGraphData);
}

/*export async function POST(request) {
  // In a real app, this would save to a database
  const data = await request.json();
  
  // For mock purposes, we'll just return success
  return Response.json({ success: true });
}*/