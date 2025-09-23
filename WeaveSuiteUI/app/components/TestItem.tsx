'use client';

import { useState } from 'react';
import { CheckCircle, XCircle, Clock, ChevronDown, ChevronUp, AlertCircle, Play } from 'lucide-react';

interface SystemTest {
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
  servicesVisited?: string[];
}

interface TestItemProps {
  test: SystemTest;
  onExecuteTest: (testId: string) => Promise<void>;
}

export default function TestItem({ test, onExecuteTest }: TestItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const formatDuration = (seconds: number) => {
    if (seconds === 0) return 'Pending';
    if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`;
    return `${seconds.toFixed(2)}s`;
  };

  const getFormattedEndpoint = () => {
    let formattedPath = test.endpoint.path;
    if (test.endpoint.params) {
      Object.entries(test.endpoint.params).forEach(([key, value]) => {
        if (formattedPath.includes(`:${key}`)) {
          formattedPath = formattedPath.replace(`:${key}`, value);
        }
      });
      if (test.endpoint.method === 'GET') {
        const queryParams = Object.entries(test.endpoint.params)
          .filter(([key]) => !formattedPath.includes(`:${key}`))
          .map(([key, value], index) => `${index === 0 ? '?' : '&'}${key}=${value}`)
          .join('');
        formattedPath += queryParams;
      }
    }
    return formattedPath;
  };

  const getStatusIcon = () => {
    switch (test.status) {
      case 'passed': return <CheckCircle className="text-green-500" size={20} />;
      case 'failed': return <XCircle className="text-red-500" size={20} />;
      case 'pending': return <Clock className="text-yellow-500" size={20} />;
      case 'error': return <AlertCircle className="text-orange-500" size={20} />;
    }
  };

  const getStatusClass = () => {
    switch (test.status) {
      case 'passed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'error': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleExecuteTest = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent expanding/collapsing when clicking the button
    try {
      setIsExecuting(true);
      await onExecuteTest(test.id);
    } catch (error) {
      console.error('Error executing test:', error);
    } finally {
      // Don't set isExecuting to false immediately - let the parent component handle state updates
      setTimeout(() => {
        setIsExecuting(false);
      }, 2000);
    }
  };

  return (
    <div className="mb-4 bg-white rounded-lg shadow-md overflow-hidden">
      <div
        className="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center space-x-3">
          {getStatusIcon()}
          <span className="font-medium">{test.name}</span>
          <span className={`text-xs px-2 py-1 rounded-full ${getStatusClass()}`}>
            {test.status.charAt(0).toUpperCase() + test.status.slice(1)}
          </span>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={handleExecuteTest}
            disabled={isExecuting || test.status === 'pending'}
            className={`flex items-center px-3 py-1 rounded text-xs font-medium transition-colors ${
              isExecuting || test.status === 'pending'
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-500 text-white hover:bg-blue-600'
            }`}
          >
            <Play className="w-3 h-3 mr-1" />
            {isExecuting || test.status === 'pending' ? 'Running...' : 'Run'}
          </button>
          <div className="text-sm text-gray-500">
            {formatDuration(test.duration)}
          </div>
          {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </div>
      </div>

      {isExpanded && (
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-gray-500">Method</p>
              <div className="mt-1 flex items-center">
                <span className={`inline-block px-2 py-1 text-xs font-medium rounded mr-2 ${
                  test.endpoint.method === 'GET' ? 'bg-blue-100 text-blue-800' : 
                  test.endpoint.method === 'POST' ? 'bg-green-100 text-green-800' : 
                  test.endpoint.method === 'PUT' ? 'bg-yellow-100 text-yellow-800' : 
                  test.endpoint.method === 'DELETE' ? 'bg-red-100 text-red-800' : 
                  'bg-gray-100 text-gray-800'
                }`}>
                  {test.endpoint.method}
                </span>
                <code className="text-sm">{getFormattedEndpoint()}</code>
              </div>
            </div>

            <div>
              <p className="text-sm font-medium text-gray-500">Last Run</p>
              <p className="mt-1 text-sm">{formatDate(test.lastRun)}</p>
            </div>

            {test.errorMessage && (
              <div className="col-span-2">
                <p className="text-sm font-medium text-gray-500">Error Message</p>
                <div className="mt-1 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                  {test.errorMessage}
                </div>
              </div>
            )}

            {test.endpoint.params && Object.keys(test.endpoint.params).length > 0 && (
              <div className="col-span-2">
                <p className="text-sm font-medium text-gray-500">Parameters</p>
                <div className="mt-1 grid grid-cols-2 gap-2">
                  {Object.entries(test.endpoint.params).map(([key, value]) => (
                    <div key={key} className="flex">
                      <span className="text-sm font-medium text-gray-700">{key}:</span>
                      <span className="text-sm ml-1">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Services Visited */}
            {test.servicesVisited && test.servicesVisited.length > 0 && (
              <div className="col-span-2">
                <p className="text-sm font-medium text-gray-500">Services Visited</p>
                <div className="mt-1 flex flex-wrap gap-2">
                  {test.servicesVisited.map(s => (
                    <span key={s} className="inline-block bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Test Code */}
            <div className="col-span-2">
              <p className="text-sm font-medium text-gray-500">Test Code</p>
              <pre className="mt-1 p-2 bg-gray-800 text-gray-100 rounded text-xs overflow-x-auto">
                {test.code}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}