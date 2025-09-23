import axios, { AxiosError } from 'axios';
import { NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'http://weavesuite-backend.default.svc.cluster.local:8000';

//interface for the spec data
interface MicroserviceSpec {
  id: number;
  spec: object;
  fetched_at: string;
  microservice_id: number;
  microservice: {
    id: number;
    name: string;
    url: string;
    version?: string;
  };
  status: 'available' | 'unavailable' | 'error';
}

interface ApiResponse<T> {
  data: T | null;
  error?: string;
}

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const action = searchParams.get('action') || 'getSpecs';
  const response: ApiResponse<MicroserviceSpec[] | unknown> = { data: null };
  let status = 200;

  try {
    if (action === 'getSpecs') {
      const specsData = await fetchSpecsData();
      response.data = specsData;
    } else {
      status = 400;
      response.error = 'Invalid action parameter for GET request';
    }
  } catch (error) {
    console.error('Error in specs API:', error);
    if (error instanceof Error) {
      if (error.message.includes('No specs available')) {
        status = 404;
        response.error = error.message;
      } else {
        status = 500;
        response.error = error.message || 'Server error occurred';
      }
    } else {
      status = 500;
      response.error = 'Server error occurred';
    }
  }

  return NextResponse.json(response, { status });
}

export async function POST(req: Request) {
  const { searchParams } = new URL(req.url);
  const action = searchParams.get('action');
  const response: ApiResponse<unknown> = { data: null };
  let status = 200;

  try {
    if (action === 'updateSpecs') {
      const result = await updateSpecs();
      response.data = result;
    } else {
      status = 400;
      response.error = 'Invalid action parameter for POST request';
    }
  } catch (error) {
    console.error('Error in specs API:', error);
    if (error instanceof Error) {
      status = 500;
      response.error = error.message || 'Server error occurred';
    } else {
      status = 500;
      response.error = 'Server error occurred';
    }
  }

  return NextResponse.json(response, { status });
}

//fetch the specs data from backend
async function fetchSpecsData(): Promise<MicroserviceSpec[]> {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/specs`);
    return response.data.specs as MicroserviceSpec[];
  } catch (error) {
    console.error('Error fetching specs data from backend:', error);
    // Check if this is a 404 error (no specs found)
    if (axios.isAxiosError(error as AxiosError) && (error as AxiosError).response?.status === 404) {
      throw new Error('No specs available. No microservices have been discovered yet.');
    }
    // For other errors
    throw new Error('Failed to connect to backend service.');
  }
}

//ppdate specs by triggering discovery and spec fetching
async function updateSpecs(): Promise<unknown> {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/update-specs`);
    return response.data;
  } catch (error) {
    console.error('Error updating specs:', error);
    throw new Error('Failed to update specs.');
  }
}