'use client';

import { useState } from 'react';
import { CheckCircle, XCircle, Clock, ChevronDown, ChevronUp } from 'lucide-react';

interface SystemTest {
  id: string;
  name: string;
  status: 'passed' | 'failed' | 'pending';
  endpoint: {
    path: string;
    method: string;
    params?: Record<string, string>;
  };
  lastRun: string;
  duration: number;
  errorMessage?: string;
}

interface TestItemProps {
  test: SystemTest;
}

export default function TestItem({ test }: TestItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const formatDuration = (ms: number) => {
    if (ms === 0) return 'Pending';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  // Format the endpoint path with params
  const getFormattedEndpoint = () => {
    let formattedPath = test.endpoint.path;
    
    if (test.endpoint.params) {
      // Replace path parameters
      Object.entries(test.endpoint.params).forEach(([key, value]) => {
        if (formattedPath.includes(`:${key}`)) {
          formattedPath = formattedPath.replace(`:${key}`, value);
        }
      });
      
      // Add query parameters if method is GET
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
      case 'passed':
        return <CheckCircle className="text-green-500" size={20} />;
      case 'failed':
        return <XCircle className="text-red-500" size={20} />;
      case 'pending':
        return <Clock className="text-yellow-500" size={20} />;
      default:
        return null;
    }
  };

  const getStatusClass = () => {
    switch (test.status) {
      case 'passed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
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
        <div className="flex items-center space-x-6">
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
              <p className="text-sm font-medium text-gray-500">Endpoint</p>
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
          </div>
        </div>
      )}
    </div>
  );
}