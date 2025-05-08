export async function GET() {
  // Mock data aligned with database schema
  const mockGraphData = {
    nodes: [
      { 
        data: { 
          id: 1,
          name: 'api-gateway',
          namespace: 'default',
          endpoint: 'http://api-gateway:8080',
          service_type: 'gateway'
        },
        position: { x: 300, y: 100 }
      },
      { 
        data: { 
          id: 2,
          name: 'auth-service',
          namespace: 'default',
          endpoint: 'http://auth-service:8080',
          service_type: 'microservice'
        },
        position: { x: 150, y: 200 }
      },
      { 
        data: { 
          id: 3,
          name: 'user-service',
          namespace: 'default',
          endpoint: 'http://user-service:8080',
          service_type: 'microservice'
        },
        position: { x: 300, y: 300 }
      },
      { 
        data: { 
          id: 4,
          name: 'product-service',
          namespace: 'default',
          endpoint: 'http://product-service:8080',
          service_type: 'microservice'
        },
        position: { x: 450, y: 200 }
      },
      { 
        data: { 
          id: 5,
          name: 'order-service',
          namespace: 'default',
          endpoint: 'http://order-service:8080',
          service_type: 'microservice'
        },
        position: { x: 500, y: 300 }
      },
      { 
        data: { 
          id: 6,
          name: 'notification-service',
          namespace: 'default',
          endpoint: 'http://notification:8080',
          service_type: 'microservice'
        },
        position: { x: 200, y: 400 }
      },
      { 
        data: { 
          id: 7,
          name: 'payment-service',
          namespace: 'default',
          endpoint: 'http://payment:8080',
          service_type: 'microservice'
        },
        position: { x: 400, y: 400 }
      }
    ],
    edges: [
      { 
        data: { 
          id: 1,
          source: 1,
          target: 2,
          label: 'authenticates'
        } 
      },
      { 
        data: { 
          id: 2,
          source: 1,
          target: 3,
          label: 'routes'
        } 
      },
      { 
        data: { 
          id: 3,
          source: 1,
          target: 4,
          label: 'routes'
        } 
      },
      { 
        data: { 
          id: 4,
          source: 1,
          target: 5,
          label: 'routes'
        } 
      },
      { 
        data: { 
          id: 5,
          source: 5,
          target: 7,
          label: 'processes payment'
        } 
      },
      { 
        data: { 
          id: 6,
          source: 5,
          target: 6,
          label: 'sends updates'
        } 
      },
      { 
        data: { 
          id: 7,
          source: 3,
          target: 6,
          label: 'sends notifications'
        } 
      },
      { 
        data: { 
          id: 8,
          source: 4,
          target: 5,
          label: 'provides details'
        } 
      }
    ]
  };

  return Response.json(mockGraphData);
}