'use client';

import { useState, useEffect } from 'react';

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

interface TestInfo {
  id: number;
  name: string;
  status: string | null;
  last_execution: string | null;
  endpoints: EndpointInfo[];
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

interface UncoveredEndpoint {
  endpoint_id: number;
  spec_id: number;
  path: string;
  method: string;
  operation_id?: string;
  summary?: string;
  tags?: string[];
}

export default function CoveragePage() {
  const [summary, setSummary] = useState<CoverageSummary | null>(null);
  const [microservices, setMicroservices] = useState<MicroserviceCoverage[]>([]);
  const [tests, setTests] = useState<TestInfo[]>([]);
  const [uncovered, setUncovered] = useState<UncoveredEndpoint[]>([]);
  const [selectedTests, setSelectedTests] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'tests' | 'gaps'>('overview');

  // Fetch all coverage data
  const fetchCoverageData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [summaryRes, msRes, uncoveredRes] = await Promise.all([
        fetch('/api/coverage?action=summary'),
        fetch('/api/coverage?action=by-microservice'),
        fetch('/api/coverage?action=uncovered')
      ]);

      if (!summaryRes.ok || !msRes.ok || !uncoveredRes.ok) {
        throw new Error('Failed to fetch coverage data');
      }

      const summaryData = await summaryRes.json();
      const msData = await msRes.json();
      const uncoveredData = await uncoveredRes.json();

      setSummary(summaryData.data);
      setMicroservices(msData.data?.microservices || []);
      setUncovered(uncoveredData.data?.endpoints || []);

      // Fetch tests with their coverage
      await fetchTestsWithCoverage();

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load coverage data');
    } finally {
      setLoading(false);
    }
  };

  // Fetch tests and their endpoint coverage
  const fetchTestsWithCoverage = async () => {
    try {
      const testsRes = await fetch('/api/tests');
      if (!testsRes.ok) {
        if (testsRes.status === 404) {
          setTests([]);
          return;
        }
        throw new Error('Failed to fetch tests');
      }

      const testsData = await testsRes.json();
      const testsList = testsData.data?.tests || testsData.tests || [];
      const testsWithCoverage: TestInfo[] = [];

      // Fetch coverage for each test
      for (const test of testsList) {
        try {
          const coverageRes = await fetch(`/api/coverage?action=test-coverage&test_id=${test.id}`);
          if (coverageRes.ok) {
            const coverageData = await coverageRes.json();
            testsWithCoverage.push({
              id: test.id,
              name: test.name,
              status: test.status,
              last_execution: test.lastRun,
              endpoints: coverageData.data?.endpoints || []
            });
          } else {
            testsWithCoverage.push({
              id: test.id,
              name: test.name,
              status: test.status,
              last_execution: test.lastRun,
              endpoints: []
            });
          }
        } catch {
          testsWithCoverage.push({
            id: test.id,
            name: test.name,
            status: test.status,
            last_execution: test.lastRun,
            endpoints: []
          });
        }
      }

      setTests(testsWithCoverage);
    } catch (err) {
      console.error('Error fetching tests:', err);
    }
  };

  // Refresh coverage analysis
  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      const res = await fetch('/api/coverage?action=refresh', { method: 'POST' });
      if (!res.ok) throw new Error('Refresh failed');
      await fetchCoverageData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Refresh failed');
    } finally {
      setRefreshing(false);
    }
  };

  // Toggle test selection
  const toggleTestSelection = (testId: number) => {
    setSelectedTests(prev => {
      const next = new Set(prev);
      if (next.has(testId)) {
        next.delete(testId);
      } else {
        next.add(testId);
      }
      return next;
    });
  };

  // Select/deselect all tests
  const toggleAllTests = () => {
    if (selectedTests.size === tests.length) {
      setSelectedTests(new Set());
    } else {
      setSelectedTests(new Set(tests.map(t => t.id)));
    }
  };

  // Get endpoints covered by selected tests
  const getSelectedCoverage = (): EndpointInfo[] => {
    const endpointMap = new Map<number, EndpointInfo>();
    
    tests
      .filter(t => selectedTests.has(t.id))
      .forEach(t => {
        t.endpoints.forEach(ep => {
          if (!endpointMap.has(ep.endpoint_id)) {
            endpointMap.set(ep.endpoint_id, ep);
          }
        });
      });
    
    return Array.from(endpointMap.values());
  };

  useEffect(() => {
    fetchCoverageData();
  }, []);

  // Method badge color
  const getMethodColor = (method: string) => {
    const colors: Record<string, string> = {
      GET: 'bg-green-100 text-green-800',
      POST: 'bg-blue-100 text-blue-800',
      PUT: 'bg-yellow-100 text-yellow-800',
      PATCH: 'bg-orange-100 text-orange-800',
      DELETE: 'bg-red-100 text-red-800',
    };
    return colors[method.toUpperCase()] || 'bg-gray-100 text-gray-800';
  };

  // Status badge color
  const getStatusColor = (status: string | null) => {
    const colors: Record<string, string> = {
      passed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      error: 'bg-orange-100 text-orange-800',
      pending: 'bg-gray-100 text-gray-800',
    };
    return colors[status || 'pending'] || 'bg-gray-100 text-gray-800';
  };

  // Coverage bar color
  const getCoverageColor = (percentage: number) => {
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="text-lg">Loading coverage data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col justify-center items-center h-full">
        <div className="text-red-600 mb-4">{error}</div>
        <button
          onClick={fetchCoverageData}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Retry
        </button>
      </div>
    );
  }

  const selectedCoverage = getSelectedCoverage();

  return (
    <div className="h-full flex flex-col p-6 overflow-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">API Endpoint Coverage</h1>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {refreshing ? 'Refreshing...' : 'Refresh Analysis'}
        </button>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">Total Endpoints</div>
            <div className="text-2xl font-bold">{summary.total_endpoints}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">Covered</div>
            <div className="text-2xl font-bold text-green-600">{summary.covered_endpoints}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">Uncovered</div>
            <div className="text-2xl font-bold text-red-600">{summary.uncovered_endpoints}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-500">Coverage</div>
            <div className="text-2xl font-bold">{summary.coverage_percentage}%</div>
            <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full ${getCoverageColor(summary.coverage_percentage)}`}
                style={{ width: `${summary.coverage_percentage}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b mb-4">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'overview'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          By Microservice
        </button>
        <button
          onClick={() => setActiveTab('tests')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'tests'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Tests ({tests.length})
        </button>
        <button
          onClick={() => setActiveTab('gaps')}
          className={`px-4 py-2 font-medium ${
            activeTab === 'gaps'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Uncovered Gaps ({uncovered.length})
        </button>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-auto">
        {/* Overview Tab - By Microservice */}
        {activeTab === 'overview' && (
          <div className="space-y-3">
            {microservices.length === 0 ? (
              <div className="text-gray-500 text-center py-8">
                No microservices found. Run coverage refresh to analyze.
              </div>
            ) : (
              microservices.map(ms => (
                <div key={ms.microservice_id} className="bg-white rounded-lg shadow p-4">
                  <div className="flex justify-between items-center mb-2">
                    <div>
                      <span className="font-medium">{ms.microservice_name}</span>
                      <span className="text-gray-500 text-sm ml-2">({ms.namespace})</span>
                    </div>
                    <div className="text-sm">
                      <span className="text-green-600 font-medium">{ms.covered_endpoints}</span>
                      <span className="text-gray-400"> / </span>
                      <span>{ms.total_endpoints}</span>
                      <span className="ml-2 font-medium">{ms.coverage_percentage}%</span>
                    </div>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getCoverageColor(ms.coverage_percentage)}`}
                      style={{ width: `${ms.coverage_percentage}%` }}
                    />
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Tests Tab */}
        {activeTab === 'tests' && (
          <div className="flex gap-4 h-full">
            {/* Tests List */}
            <div className="w-1/2 bg-white rounded-lg shadow overflow-hidden flex flex-col">
              <div className="p-3 border-b bg-gray-50 flex items-center">
                <input
                  type="checkbox"
                  checked={selectedTests.size === tests.length && tests.length > 0}
                  onChange={toggleAllTests}
                  className="mr-3 h-4 w-4"
                />
                <span className="font-medium">
                  Select Tests ({selectedTests.size} selected)
                </span>
              </div>
              <div className="flex-1 overflow-auto">
                {tests.length === 0 ? (
                  <div className="text-gray-500 text-center py-8">No tests found</div>
                ) : (
                  tests.map(test => (
                    <div
                      key={test.id}
                      className={`p-3 border-b hover:bg-gray-50 cursor-pointer ${
                        selectedTests.has(test.id) ? 'bg-blue-50' : ''
                      }`}
                      onClick={() => toggleTestSelection(test.id)}
                    >
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          checked={selectedTests.has(test.id)}
                          onChange={() => toggleTestSelection(test.id)}
                          onClick={e => e.stopPropagation()}
                          className="mr-3 h-4 w-4"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="font-medium truncate">{test.name}</div>
                          <div className="flex items-center gap-2 mt-1">
                            <span className={`text-xs px-2 py-0.5 rounded ${getStatusColor(test.status)}`}>
                              {test.status || 'pending'}
                            </span>
                            <span className="text-xs text-gray-500">
                              {test.endpoints.length} endpoint{test.endpoints.length !== 1 ? 's' : ''}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Selected Tests Coverage */}
            <div className="w-1/2 bg-white rounded-lg shadow overflow-hidden flex flex-col">
              <div className="p-3 border-b bg-gray-50">
                <span className="font-medium">
                  Covered Endpoints ({selectedCoverage.length})
                </span>
              </div>
              <div className="flex-1 overflow-auto">
                {selectedTests.size === 0 ? (
                  <div className="text-gray-500 text-center py-8">
                    Select tests to see their coverage
                  </div>
                ) : selectedCoverage.length === 0 ? (
                  <div className="text-gray-500 text-center py-8">
                    Selected tests don&apos;t cover any endpoints
                  </div>
                ) : (
                  selectedCoverage.map(ep => (
                    <div key={ep.endpoint_id} className="p-3 border-b">
                      <div className="flex items-center gap-2">
                        <span className={`text-xs px-2 py-0.5 rounded font-mono ${getMethodColor(ep.method)}`}>
                          {ep.method}
                        </span>
                        <span className="font-mono text-sm">{ep.path}</span>
                      </div>
                      {ep.summary && (
                        <div className="text-xs text-gray-500 mt-1 ml-14">{ep.summary}</div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* Gaps Tab - Uncovered Endpoints */}
        {activeTab === 'gaps' && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            {uncovered.length === 0 ? (
              <div className="text-green-600 text-center py-8">
                🎉 All endpoints are covered by tests!
              </div>
            ) : (
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Method</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Path</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Operation ID</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Summary</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {uncovered.map(ep => (
                    <tr key={ep.endpoint_id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-0.5 rounded font-mono ${getMethodColor(ep.method)}`}>
                          {ep.method}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-mono text-sm">{ep.path}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">{ep.operation_id || '-'}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">{ep.summary || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>
    </div>
  );
}