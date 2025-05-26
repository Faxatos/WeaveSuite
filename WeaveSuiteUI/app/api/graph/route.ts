import axios, { AxiosError } from 'axios';
import { NextResponse } from 'next/server';

// Define the API endpoint for the backend Python service
const API_BASE_URL = process.env.API_BASE_URL || 'http://weavesuite-backend.default.svc.cluster.local:8000';

// Define interfaces for the service graph data
interface NodeData {
  id: number;
  name: string;
  namespace: string;
  endpoint: string;
  service_type: string;
}

interface Node {
  data: NodeData;
  position: {
    x: number;
    y: number;
  };
}

interface EdgeData {
  id: number;
  source: number;
  target: number;
  label: string;
}

interface Edge {
  data: EdgeData;
}

interface ServiceGraph {
  nodes: Node[];
  edges: Edge[];
}

// Define a response structure to wrap data or error
interface ApiResponse<T> {
  data: T | null;
  error?: string;
}

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const action = searchParams.get('action') || 'getGraph';
  
  const response: ApiResponse<ServiceGraph | unknown> = { data: null };
  let status = 200;

  try {
    if (action === 'getGraph') {
      const graphData = await fetchServiceGraph();
      response.data = graphData;
    } else if (action === 'updateSpecs') {
      const updateResult = await triggerSpecUpdate();
      response.data = updateResult;
    } else {
      status = 400;
      response.error = 'Invalid action parameter';
    }
  } catch (error) {
    console.error('Error in graph API:', error);
    
    // Handle specific error types differently
    if (error instanceof Error) {
      if (error.message.includes('Service map is empty')) {
        // This is a 404 from the backend - pass it through
        status = 404;
        response.error = error.message;
      } else {
        // Other errors - internal server error
        status = 500;
        response.error = error.message || 'Server error occurred';
      }
    } else {
      // Unknown error type
      status = 500;
      response.error = 'Server error occurred';
    }
  }

  return NextResponse.json(response, { status });
}

// Fetch the service graph from the Python backend
async function fetchServiceGraph(): Promise<ServiceGraph> {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/graph`);
    return response.data as ServiceGraph;
  } catch (error) {
    console.error('Error fetching service graph from backend:', error);
    
    // Check if this is a 404 error (service map is empty)
    if (axios.isAxiosError(error as AxiosError) && (error as AxiosError).response?.status === 404) {
      throw new Error('Service map is empty. No microservices or links found.');
    }
    
    // For other errors
    throw new Error('Failed to connect to service discovery backend.');
  }
}

// Trigger the spec update process on the backend
async function triggerSpecUpdate(): Promise<unknown> {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/update-specs`);
    return response.data;
  } catch (error) {
    console.error('Error triggering spec update:', error);
    throw new Error('Failed to trigger service discovery update.');
  }
}