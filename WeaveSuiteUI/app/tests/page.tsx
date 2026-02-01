'use client';

import { useEffect, useState, useCallback } from 'react';
import TestItem from '@/app/components/TestItem';
import { Play, Zap, Trash2 } from 'lucide-react';

export interface SystemTest {
  id: string;
  name: string;
  status: 'passed' | 'failed' | 'pending' | 'error';
  code: string;
  endpoint: {
    path: string;
    method: string;
    params?: Record<string, string>;
  };
  lastRun: string;
  duration: number;
  errorMessage?: string;
}

export default function TestsPage() {
  const [tests, setTests] = useState<SystemTest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [filter, setFilter] = useState<'all' | 'passed' | 'failed' | 'pending' | 'error'>('all');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isExecutingAll, setIsExecutingAll] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Fetch tests data
  const fetchTests = useCallback(async (): Promise<SystemTest[]> => {
    const res = await fetch('/api/tests');
    
    if (!res.ok) {
      const errorData = await res.json();
      if (res.status === 404) {
        return [];
      }
      throw new Error(errorData.error || 'Failed to fetch tests');
    }
    
    const data = await res.json();
    let testsData: SystemTest[];
    
    if (data.data && Array.isArray(data.data)) {
      testsData = data.data;
    } else if (data.tests && Array.isArray(data.tests)) {
      testsData = data.tests;
    } else if (Array.isArray(data)) {
      testsData = data;
    } else {
      testsData = [];
    }
    
    return testsData
      .map(t => ({ ...t, id: String(t.id) }))
      .sort((a, b) => a.name.localeCompare(b.name));
  }, []);

  useEffect(() => {
    const loadTests = async () => {
      try {
        setLoading(true);
        setError(null);
        const testsData = await fetchTests();
        setTests(testsData);
      } catch (error) {
        console.error('Error fetching tests data:', error);
        setError('Failed to load tests data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    loadTests();
  }, [retryCount, fetchTests]);

  const handleGenerateTests = async () => {
    try {
      setIsGenerating(true);
      setError(null);
      const response = await fetch('/api/tests?action=generateTests', {
        method: 'POST',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to generate tests');
      }
      
      // Refresh tests after generation
      setTimeout(() => {
        setRetryCount(prev => prev + 1);
      }, 2000);
      
    } catch (error) {
      console.error('Error generating tests:', error);
      setError('Failed to generate tests. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExecuteAllTests = async () => {
    try {
      setIsExecutingAll(true);
      setError(null);
      
      // Set all tests to pending status immediately
      setTests(prevTests => 
        prevTests.map(test => ({ 
          ...test, 
          status: 'pending' as const 
        }))
      );
      
      const response = await fetch('/api/tests?action=executeTests', {
        method: 'POST',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to execute tests');
      }
      
      // Poll for results until no tests are pending
      const pollInterval = 2000; // 2 seconds
      const maxAttempts = 60; // Max 2 minutes of polling
      let attempts = 0;
      
      const pollForResults = async () => {
        attempts++;
        
        try {
          const updatedTests = await fetchTests();
          setTests(updatedTests);
          
          // Check if any tests are still pending
          const hasPending = updatedTests.some(t => t.status === 'pending');
          
          if (hasPending && attempts < maxAttempts) {
            // Continue polling
            setTimeout(pollForResults, pollInterval);
          } else {
            // All tests completed or max attempts reached
            setIsExecutingAll(false);
            if (attempts >= maxAttempts && hasPending) {
              setError('Some tests are still running. Refresh to check status.');
            }
          }
        } catch (err) {
          console.error('Error polling for test results:', err);
          setIsExecutingAll(false);
        }
      };
      
      // Start polling after a short delay to let execution begin
      setTimeout(pollForResults, pollInterval);
      
    } catch (error) {
      console.error('Error executing tests:', error);
      setError('Failed to execute all tests. Please try again.');
      setIsExecutingAll(false);
    }
  };

  const handleExecuteSingleTest = async (testId: string) => {
    try {
      setError(null);
      
      // Set the specific test to pending status immediately
      setTests(prevTests => 
        prevTests.map(test => 
          test.id === testId 
            ? { ...test, status: 'pending' as const }
            : test
        )
      );
      
      const response = await fetch('/api/tests?action=executeTest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ testId: parseInt(testId) }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to execute test');
      }
      
      // Poll for this specific test's result
      const pollInterval = 1000;
      const maxAttempts = 30;
      let attempts = 0;
      
      const pollForResult = async () => {
        attempts++;
        
        try {
          const updatedTests = await fetchTests();
          setTests(updatedTests);
          
          const updatedTest = updatedTests.find(t => t.id === testId);
          
          if (updatedTest?.status === 'pending' && attempts < maxAttempts) {
            setTimeout(pollForResult, pollInterval);
          }
        } catch (err) {
          console.error('Error polling for test result:', err);
        }
      };
      
      setTimeout(pollForResult, pollInterval);
      
    } catch (error) {
      console.error('Error executing single test:', error);
      setError(`Failed to execute test. Please try again.`);
      
      // Revert the test status on error
      setTests(prevTests => 
        prevTests.map(test => 
          test.id === testId 
            ? { ...test, status: 'error' as const }
            : test
        )
      );
    }
  };

  const handleDeleteAllTests = async () => {
    if (!confirm('Are you sure you want to delete all tests? This action cannot be undone.')) {
      return;
    }
    
    try {
      setIsDeleting(true);
      setError(null);
      
      const response = await fetch('/api/tests', {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to delete tests');
      }
      
      const data = await response.json();
      const message = data.data?.message || `Deleted ${data.data?.deleted_count || 0} tests`;
      
      // Clear tests from state
      setTests([]);
      
      // Show success message briefly
      alert(message);
      
    } catch (error) {
      console.error('Error deleting tests:', error);
      setError('Failed to delete tests. Please try again.');
    } finally {
      setIsDeleting(false);
    }
  };

  const filteredTests = tests.filter(test => {
    if (filter === 'all') return true;
    return test.status === filter;
  });

  const counts = {
    all: tests.length,
    passed: tests.filter(t => t.status === 'passed').length,
    failed: tests.filter(t => t.status === 'failed').length,
    pending: tests.filter(t => t.status === 'pending').length,
    error: tests.filter(t => t.status === 'error').length,
  };

  const FilterButton = ({ type }: { type: 'all' | 'passed' | 'failed' | 'pending' | 'error' }) => {
    const labels = {
      all: 'All',
      passed: 'Passed',
      failed: 'Failed',
      pending: 'Pending',
      error: 'Error',
    };
    
    const colorClasses = {
      all: filter === 'all' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800',
      passed: filter === 'passed' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800',
      failed: filter === 'failed' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800',
      pending: filter === 'pending' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800',
      error: filter === 'error' ? 'bg-orange-100 text-orange-800' : 'bg-gray-100 text-gray-800',
    };
    
    return (
      <button
        onClick={() => setFilter(type)}
        className={`px-4 py-2 rounded-md ${colorClasses[type]} mr-2 text-sm font-medium`}
      >
        {labels[type]} ({counts[type]})
      </button>
    );
  };

  const handleManualRetry = () => {
    setRetryCount(prev => prev + 1);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] flex-col">
        <div className="text-lg mb-4">Loading tests data...</div>
        {error && (
          <div className="text-yellow-600 text-sm">{error}</div>
        )}
      </div>
    );
  }

  if (error && tests.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[60vh] flex-col">
        <div className="text-red-600 mb-4">{error}</div>
        <button 
          onClick={handleManualRetry}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">System Tests</h1>
        
        {/* Action buttons on the top right */}
        <div className="flex space-x-3">
          <button
            onClick={handleDeleteAllTests}
            disabled={isDeleting || tests.length === 0 || loading || isExecutingAll}
            className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              isDeleting || tests.length === 0 || loading || isExecutingAll
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                : 'bg-red-500 text-white hover:bg-red-600'
            }`}
          >
            <Trash2 className="w-4 h-4 mr-2" />
            {isDeleting ? 'Deleting...' : 'Delete All'}
          </button>
          
          <button
            onClick={handleGenerateTests}
            disabled={isGenerating || loading || isExecutingAll}
            className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              isGenerating || loading || isExecutingAll
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                : 'bg-green-500 text-white hover:bg-green-600'
            }`}
          >
            <Zap className="w-4 h-4 mr-2" />
            {isGenerating ? 'Generating...' : 'Generate Tests'}
          </button>
          
          <button
            onClick={handleExecuteAllTests}
            disabled={isExecutingAll || tests.length === 0 || loading}
            className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              isExecutingAll || tests.length === 0 || loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                : 'bg-blue-500 text-white hover:bg-blue-600'
            }`}
          >
            <Play className="w-4 h-4 mr-2" />
            {isExecutingAll ? 'Running All...' : 'Run All Tests'}
          </button>
        </div>
      </div>
      
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
          {error}
        </div>
      )}
      
      <div className="mb-6">
        <FilterButton type="all" />
        <FilterButton type="passed" />
        <FilterButton type="failed" />
        <FilterButton type="pending" />
        <FilterButton type="error" />
      </div>
      
      {filteredTests.length === 0 ? (
        <div className="text-center py-10 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No tests found matching the selected filter.</p>
        </div>
      ) : (
        <div>
          {filteredTests.map(test => (
            <TestItem 
              key={test.id} 
              test={test} 
              onExecuteTest={handleExecuteSingleTest}
            />
          ))}
        </div>
      )}
    </div>
  );
}