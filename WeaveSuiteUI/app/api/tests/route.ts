import axios, { AxiosError } from 'axios';
import { NextResponse } from 'next/server';

// Define the API endpoint for the backend Python service
const API_BASE_URL = process.env.API_BASE_URL || 'http://weavesuite-backend:8000';

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
}

interface DeleteResponse {
  status: string;
  message: string;
  deleted_count: number;
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
    } else {
      status = 400;
      response.error = 'Invalid action parameter for GET request';
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

export async function POST(req: Request) {
  const { searchParams } = new URL(req.url);
  const action = searchParams.get('action');
  const response: ApiResponse<unknown> = { data: null };
  let status = 200;

  try {
    if (action === 'executeTests') {
      const result = await executeAllTests();
      response.data = result;
    } else if (action === 'executeTest') {
      const body = await req.json();
      const testId = body.testId;
      if (!testId) {
        status = 400;
        response.error = 'Test ID is required';
      } else {
        const result = await executeSingleTest(testId);
        response.data = result;
      }
    } else if (action === 'generateTests') {
      const result = await generateTests();
      response.data = result;
    } else {
      status = 400;
      response.error = 'Invalid action parameter for POST request';
    }
  } catch (error) {
    console.error('Error in tests API:', error);
    // Handle specific error types differently
    if (error instanceof Error) {
      if (error.message.includes('not found')) {
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

export async function DELETE() {
  const response: ApiResponse<DeleteResponse> = { data: null };
  let status = 200;

  try {
    const result = await deleteAllTests();
    response.data = result;
  } catch (error) {
    console.error('Error deleting tests:', error);
    status = 500;
    response.error = error instanceof Error ? error.message : 'Failed to delete tests';
  }

  return NextResponse.json(response, { status });
}

//fetch the test data from the Python backend
async function fetchTestsData(): Promise<TestData[]> {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/system-tests`);
    return response.data.tests as TestData[];
  } catch (error) {
    console.error('Error fetching test data from backend:', error);
    //check if this is a 404 error (no tests found)
    if (axios.isAxiosError(error as AxiosError) && (error as AxiosError).response?.status === 404) {
      throw new Error('No test data available. No tests have been defined or run.');
    }
    throw new Error('Failed to connect to testing backend.');
  }
}

//execute all tests on the backend
async function executeAllTests(): Promise<unknown> {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/execute-tests`);
    return response.data;
  } catch (error) {
    console.error('Error executing all tests:', error);
    throw new Error('Failed to execute all tests.');
  }
}

//execute a single test by ID
async function executeSingleTest(testId: number): Promise<unknown> {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/execute-test/${testId}`);
    return response.data;
  } catch (error) {
    console.error(`Error executing test ${testId}:`, error);
    if (axios.isAxiosError(error as AxiosError) && (error as AxiosError).response?.status === 404) {
      throw new Error(`Test with ID ${testId} not found`);
    }
    throw new Error(`Failed to execute test ${testId}.`);
  }
}

//generate tests from OpenAPI specs
async function generateTests(): Promise<unknown> {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/generate-tests`);
    return response.data;
  } catch (error) {
    console.error('Error generating tests:', error);
    throw new Error('Failed to generate tests.');
  }
}

//delete all tests
async function deleteAllTests(): Promise<DeleteResponse> {
  try {
    const response = await axios.delete(`${API_BASE_URL}/api/system-tests`);
    return response.data as DeleteResponse;
  } catch (error) {
    console.error('Error deleting tests:', error);
    throw new Error('Failed to delete tests.');
  }
}