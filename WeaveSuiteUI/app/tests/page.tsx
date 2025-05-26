'use client';

import { useEffect, useState } from 'react';
import TestItem from '@/app/components/TestItem';

export interface SystemTest {
  id: string;
  name: string;
  status: 'passed' | 'failed' | 'pending';
  code: string;
  endpoint: {
    path: string;
    method: string;
    params?: Record<string, string>;
  };
  lastRun: string;
  duration: number; // in milliseconds
  errorMessage?: string;
  servicesVisited: string[];
}

export default function TestsPage() {
  const [tests, setTests] = useState<SystemTest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [filter, setFilter] = useState<'all' | 'passed' | 'failed' | 'pending'>('all');

  useEffect(() => {
    const fetchTests = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const res = await fetch('/api/tests');
        
        if (!res.ok) {
          // Handle specific error cases
          const errorData = await res.json();
          
          if (res.status === 404 && errorData.error?.includes('No system tests available')) {
            setError('No tests available yet. Retrying...');
            
            // Wait a second and retry
            setTimeout(() => {
              setRetryCount(prev => prev + 1);
            }, 1000);
            return;
          }
          
          throw new Error(errorData.error || 'Failed to fetch tests');
        }
        
        const data = await res.json();
        console.log('Raw API response:', data);
        let testsData: SystemTest[];
        
        // Check if the data is wrapped in a 'data' property (from the API response)
        if (data.data?.tests) {
          testsData = data.data.tests;
        } else {
          testsData = data.tests || data;
        }
        
        // Convert numeric ids to string for TestItem compatibility
        testsData = testsData.map(t => ({ ...t, id: String(t.id) }));
        
        setTests(testsData);
        setError(null);
      } catch (error) {
        console.error('Error fetching tests data:', error);
        setError('Failed to load tests data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchTests();
  }, [retryCount]);

  const filteredTests = tests.filter(test => {
    if (filter === 'all') return true;
    return test.status === filter;
  });

  const counts = {
    all: tests.length,
    passed: tests.filter(t => t.status === 'passed').length,
    failed: tests.filter(t => t.status === 'failed').length,
    pending: tests.filter(t => t.status === 'pending').length,
  };

  const FilterButton = ({ type }: { type: 'all' | 'passed' | 'failed' | 'pending' }) => {
    const labels = {
      all: 'All',
      passed: 'Passed',
      failed: 'Failed',
      pending: 'Pending',
    };
    
    const colorClasses = {
      all: filter === 'all' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800',
      passed: filter === 'passed' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800',
      failed: filter === 'failed' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800',
      pending: filter === 'pending' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800',
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

  if (error) {
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
      <h1 className="text-2xl font-bold mb-6">System Tests</h1>
      
      <div className="mb-6">
        <FilterButton type="all" />
        <FilterButton type="passed" />
        <FilterButton type="failed" />
        <FilterButton type="pending" />
      </div>
      
      {filteredTests.length === 0 ? (
        <div className="text-center py-10 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No tests found matching the selected filter.</p>
        </div>
      ) : (
        <div>
          {filteredTests.map(test => (
            <TestItem key={test.id} test={test} />
          ))}
        </div>
      )}
    </div>
  );
}