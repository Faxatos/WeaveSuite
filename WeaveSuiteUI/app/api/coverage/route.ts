import axios, { AxiosError } from 'axios';
import { NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'http://weavesuite-backend:8000';

// Types
interface CoverageSummary {
  total_endpoints: number;
  covered_endpoints: number;
  uncovered_endpoints: number;
  coverage_percentage: number;
}

interface MicroserviceCoverage {
  microservice_id: number;
  microservice_name: string;
  namespace: string;
  total_endpoints: number;
  covered_endpoints: number;
  coverage_percentage: number;
}

interface EndpointInfo {
  endpoint_id: number;
  path: string;
  method: string;
  operation_id?: string;
  summary?: string;
  tags?: string[];
  is_covered?: boolean;
}

interface TestCoverage {
  test: {
    id: number;
    name: string;
    status: string | null;
  };
  endpoints: EndpointInfo[];
}

interface UncoveredResponse {
  count: number;
  endpoints: EndpointInfo[];
}

interface MicroserviceResponse {
  microservices: MicroserviceCoverage[];
}

interface ApiResponse<T> {
  data: T | null;
  error?: string;
}

type CoverageAction = 
  | 'summary' 
  | 'by-microservice' 
  | 'uncovered' 
  | 'endpoints' 
  | 'test-coverage' 
  | 'endpoint-coverage';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const action = searchParams.get('action') as CoverageAction || 'summary';
  const specId = searchParams.get('spec_id');
  const testId = searchParams.get('test_id');
  const endpointId = searchParams.get('endpoint_id');
  const method = searchParams.get('method');
  const covered = searchParams.get('covered');

  const response: ApiResponse<
    CoverageSummary | 
    MicroserviceResponse | 
    UncoveredResponse | 
    TestCoverage | 
    unknown
  > = { data: null };
  let status = 200;

  try {
    switch (action) {
      case 'summary':
        response.data = await fetchCoverageSummary(specId);
        break;

      case 'by-microservice':
        response.data = await fetchCoverageByMicroservice();
        break;

      case 'uncovered':
        response.data = await fetchUncoveredEndpoints(specId);
        break;

      case 'endpoints':
        response.data = await fetchEndpoints(specId, method, covered);
        break;

      case 'test-coverage':
        if (!testId) {
          status = 400;
          response.error = 'test_id parameter is required';
          break;
        }
        response.data = await fetchTestCoverage(testId);
        break;

      case 'endpoint-coverage':
        if (!endpointId) {
          status = 400;
          response.error = 'endpoint_id parameter is required';
          break;
        }
        response.data = await fetchEndpointCoverage(endpointId);
        break;

      default:
        status = 400;
        response.error = 'Invalid action parameter';
    }
  } catch (error) {
    console.error('Error in coverage API:', error);

    if (error instanceof Error) {
      if (error.message.includes('not found') || error.message.includes('404')) {
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
  const action = searchParams.get('action') || 'refresh';
  const testId = searchParams.get('test_id');

  const response: ApiResponse<unknown> = { data: null };
  let status = 200;

  try {
    switch (action) {
      case 'refresh':
        response.data = await refreshCoverage();
        break;

      case 'analyze-test':
        if (!testId) {
          status = 400;
          response.error = 'test_id parameter is required';
          break;
        }
        response.data = await analyzeTestCoverage(testId);
        break;

      default:
        status = 400;
        response.error = 'Invalid action parameter';
    }
  } catch (error) {
    console.error('Error in coverage API:', error);

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

// API Functions

async function fetchCoverageSummary(specId: string | null): Promise<CoverageSummary> {
  try {
    const params = specId ? `?spec_id=${specId}` : '';
    const res = await axios.get(`${API_BASE_URL}/api/coverage/summary${params}`);
    return res.data as CoverageSummary;
  } catch (error) {
    console.error('Error fetching coverage summary:', error);
    throw new Error('Failed to fetch coverage summary');
  }
}

async function fetchCoverageByMicroservice(): Promise<MicroserviceResponse> {
  try {
    const res = await axios.get(`${API_BASE_URL}/api/coverage/by-microservice`);
    return res.data as MicroserviceResponse;
  } catch (error) {
    console.error('Error fetching coverage by microservice:', error);
    throw new Error('Failed to fetch coverage by microservice');
  }
}

async function fetchUncoveredEndpoints(specId: string | null): Promise<UncoveredResponse> {
  try {
    const params = specId ? `?spec_id=${specId}` : '';
    const res = await axios.get(`${API_BASE_URL}/api/coverage/uncovered${params}`);
    return res.data as UncoveredResponse;
  } catch (error) {
    console.error('Error fetching uncovered endpoints:', error);
    throw new Error('Failed to fetch uncovered endpoints');
  }
}

async function fetchEndpoints(
  specId: string | null, 
  method: string | null, 
  covered: string | null
): Promise<unknown> {
  try {
    const params = new URLSearchParams();
    if (specId) params.append('spec_id', specId);
    if (method) params.append('method', method);
    if (covered !== null) params.append('covered', covered);
    
    const queryString = params.toString() ? `?${params.toString()}` : '';
    const res = await axios.get(`${API_BASE_URL}/api/coverage/endpoints${queryString}`);
    return res.data;
  } catch (error) {
    console.error('Error fetching endpoints:', error);
    throw new Error('Failed to fetch endpoints');
  }
}

async function fetchTestCoverage(testId: string): Promise<TestCoverage> {
  try {
    const res = await axios.get(`${API_BASE_URL}/api/coverage/tests/${testId}`);
    return res.data as TestCoverage;
  } catch (error) {
    if (axios.isAxiosError(error as AxiosError) && (error as AxiosError).response?.status === 404) {
      throw new Error('Test not found');
    }
    console.error('Error fetching test coverage:', error);
    throw new Error('Failed to fetch test coverage');
  }
}

async function fetchEndpointCoverage(endpointId: string): Promise<unknown> {
  try {
    const res = await axios.get(`${API_BASE_URL}/api/coverage/endpoints/${endpointId}`);
    return res.data;
  } catch (error) {
    if (axios.isAxiosError(error as AxiosError) && (error as AxiosError).response?.status === 404) {
      throw new Error('Endpoint not found');
    }
    console.error('Error fetching endpoint coverage:', error);
    throw new Error('Failed to fetch endpoint coverage');
  }
}

async function refreshCoverage(): Promise<unknown> {
  try {
    const res = await axios.post(`${API_BASE_URL}/api/coverage/refresh`);
    return res.data;
  } catch (error) {
    console.error('Error refreshing coverage:', error);
    throw new Error('Failed to refresh coverage analysis');
  }
}

async function analyzeTestCoverage(testId: string): Promise<unknown> {
  try {
    const res = await axios.post(`${API_BASE_URL}/api/coverage/analyze/${testId}`);
    return res.data;
  } catch (error) {
    if (axios.isAxiosError(error as AxiosError) && (error as AxiosError).response?.status === 404) {
      throw new Error('Test not found');
    }
    console.error('Error analyzing test coverage:', error);
    throw new Error('Failed to analyze test coverage');
  }
}