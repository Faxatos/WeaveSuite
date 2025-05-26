import axios, { AxiosError } from 'axios';
import { NextResponse } from 'next/server';

// Define the API endpoint for the backend Python service
const API_BASE_URL = process.env.API_BASE_URL || 'http://weavesuite-backend.default.svc.cluster.local:8000';

// Define interfaces for the test data
interface TestEndpoint {
  path: string;
  method: string;
  params?: Record<string, string>;
}

interface TestData {
  id: number;
  name: string;
  status: 'passed' | 'failed' | 'pending';
  code: string;
  endpoint: TestEndpoint;
  lastRun: string;
  duration: number;
  errorMessage?: string;
  servicesVisited: string[];
}

// Define a response structure to wrap data or error
interface ApiResponse<T> {
  data: T | null;
  error?: string;
}

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const action = searchParams.get('action') || 'getTests';
  
  const response: ApiResponse<TestData[] | unknown> = { data: null };
  let status = 200;

  try {
    if (action === 'getTests') {
      const testsData = await fetchTestsData();
      response.data = testsData;
    } else if (action === 'runTests') {
      const runResult = await triggerTestRun();
      response.data = runResult;
    } else {
      status = 400;
      response.error = 'Invalid action parameter';
    }
  } catch (error) {
    console.error('Error in tests API:', error);
    
    // Handle specific error types differently
    if (error instanceof Error) {
      if (error.message.includes('No test data available')) {
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

// Fetch the test data from the Python backend
async function fetchTestsData(): Promise<TestData[]> {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/tests`);
    return response.data as TestData[];
  } catch (error) {
    console.error('Error fetching test data from backend:', error);
    
    // Check if this is a 404 error (no tests found)
    if (axios.isAxiosError(error as AxiosError) && (error as AxiosError).response?.status === 404) {
      throw new Error('No test data available. No tests have been defined or run.');
    }
    
    // For other errors
    throw new Error('Failed to connect to testing backend.');
  }
}

// Trigger the test run process on the backend
async function triggerTestRun(): Promise<unknown> {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/run-tests`);
    return response.data;
  } catch (error) {
    console.error('Error triggering test run:', error);
    throw new Error('Failed to trigger test execution.');
  }
}