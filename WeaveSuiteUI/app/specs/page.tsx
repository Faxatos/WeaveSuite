'use client';

import { useEffect, useState } from 'react';
import SpecItem from '@/app/components/SpecItem';
import { RefreshCw } from 'lucide-react';

export interface MicroserviceSpec {
  id: string;
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

export default function SpecsPage() {
  const [specs, setSpecs] = useState<MicroserviceSpec[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [filter, setFilter] = useState<'all' | 'available' | 'unavailable' | 'error'>('all');
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    const fetchSpecs = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const res = await fetch('/api/specs');
        
        if (!res.ok) {
          // Handle specific error cases
          const errorData = await res.json();
          
          if (res.status === 404 && errorData.error?.includes('No specs available')) {
            setError('No specs available yet. Retrying...');
            
            // Wait a second and retry
            setTimeout(() => {
              setRetryCount(prev => prev + 1);
            }, 1000);
            return;
          }
          
          throw new Error(errorData.error || 'Failed to fetch specs');
        }
        
        const data = await res.json();
        console.log('Raw API response:', data);
        let specsData: MicroserviceSpec[];
        
        // Check if the data is wrapped in a 'data' property (from the API response)
        if (data.data && Array.isArray(data.data)) {
          specsData = data.data;
        } else if (data.specs && Array.isArray(data.specs)) {
          specsData = data.specs;
        } else if (Array.isArray(data)) {
          specsData = data;
        } else {
          specsData = [];
        }
        
        // Convert numeric ids to string and sort by microservice name
        specsData = specsData
          .map(s => ({ ...s, id: String(s.id) }))
          .sort((a, b) => a.microservice.name.localeCompare(b.microservice.name));
        
        setSpecs(specsData);
        setError(null);
      } catch (error) {
        console.error('Error fetching specs data:', error);
        setError('Failed to load specs data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchSpecs();
  }, [retryCount]);

  const handleUpdateSpecs = async () => {
    try {
      setIsUpdating(true);
      setError(null);
      const response = await fetch('/api/specs?action=updateSpecs', {
        method: 'POST',
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to update specs');
      }
      
      // Refresh specs after update
      setTimeout(() => {
        setRetryCount(prev => prev + 1);
      }, 2000);
      
    } catch (error) {
      console.error('Error updating specs:', error);
      setError('Failed to update specs. Please try again.');
    } finally {
      setIsUpdating(false);
    }
  };

  const filteredSpecs = specs.filter(spec => {
    if (filter === 'all') return true;
    return spec.status === filter;
  });

  const counts = {
    all: specs.length,
    available: specs.filter(s => s.status === 'available').length,
    unavailable: specs.filter(s => s.status === 'unavailable').length,
    error: specs.filter(s => s.status === 'error').length,
  };

  const FilterButton = ({ type }: { type: 'all' | 'available' | 'unavailable' | 'error' }) => {
    const labels = {
      all: 'All',
      available: 'Available',
      unavailable: 'Unavailable',
      error: 'Error',
    };
    
    const colorClasses = {
      all: filter === 'all' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800',
      available: filter === 'available' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800',
      unavailable: filter === 'unavailable' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800',
      error: filter === 'error' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800',
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
        <div className="text-lg mb-4">Loading OpenAPI specs...</div>
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
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">OpenAPI Specifications</h1>
        
        {/* Update button on the top right */}
        <div className="flex space-x-3">
          <button
            onClick={handleUpdateSpecs}
            disabled={isUpdating || loading}
            className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              isUpdating || loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                : 'bg-blue-500 text-white hover:bg-blue-600'
            }`}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            {isUpdating ? 'Updating...' : 'Update Specs'}
          </button>
        </div>
      </div>
      
      <div className="mb-6">
        <FilterButton type="all" />
        <FilterButton type="available" />
        <FilterButton type="unavailable" />
        <FilterButton type="error" />
      </div>
      
      {filteredSpecs.length === 0 ? (
        <div className="text-center py-10 bg-gray-50 rounded-lg">
          <p className="text-gray-500">No OpenAPI specs found matching the selected filter.</p>
          {specs.length === 0 && (
            <p className="text-gray-400 text-sm mt-2">
              Try clicking &quot;Update Specs&quot; to discover microservices and fetch their specifications.
            </p>
          )}
        </div>
      ) : (
        <div>
          {filteredSpecs.map(spec => (
            <SpecItem key={spec.id} spec={spec} />
          ))}
        </div>
      )}
    </div>
  );
}