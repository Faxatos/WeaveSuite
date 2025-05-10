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
  const [filter, setFilter] = useState<'all' | 'passed' | 'failed' | 'pending'>('all');

  useEffect(() => {
    const fetchTests = async () => {
      try {
        const res = await fetch('/api/tests');
        const raw: any[] = await res.json();
        // convert numeric ids to string for TestItem compatibility
        const data: SystemTest[] = raw.map(t => ({ ...t, id: String(t.id) }));
        setTests(data);
      } catch (error) {
        console.error('Error fetching tests data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTests();
  }, []);

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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-lg">Loading tests data...</div>
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
