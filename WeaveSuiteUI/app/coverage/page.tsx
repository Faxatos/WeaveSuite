'use client';

import { useState, useEffect } from 'react';
import Graph from '../components/Graph';

interface MicroserviceNode {
  data: {
    id: number;
    name: string;
    namespace: string;
    endpoint: string;
    service_type: string;
  };
  position: {
    x: number;
    y: number;
  };
}

interface ServiceLink {
  data: {
    id: number;
    source: number;
    target: number;
    label: string;
  };
}

interface GraphData {
  nodes: MicroserviceNode[];
  edges: ServiceLink[];
}

export default function Home() {
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [saveStatus, setSaveStatus] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch('/api/graph');
        
        if (!response.ok) {
          // Handle specific error cases
          const errorData = await response.json();
          
          if (response.status === 404 && errorData.error?.includes('Service map is empty')) {
            setError('Service map is empty. Retrying...');
            
            // Wait a second and retry
            setTimeout(() => {
              setRetryCount(prev => prev + 1);
            }, 1000);
            return;
          }
          
          throw new Error(errorData.error || 'Failed to fetch graph data');
        }
        
        const data = await response.json();
        console.log('Raw API response:', data);
        
        // Check if the data is wrapped in a data property
        const graphData = data.data ? data.data : data;
        
        setGraphData(graphData);
      } catch (error) {
        console.error('Error fetching graph data:', error);
        setError('Failed to load service map. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [retryCount]);

  const handleSave = async (updatedData: GraphData) => {
    setSaveStatus('Saving...');
    try {
      const response = await fetch('/api/graph', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          nodes: updatedData.nodes.map(node => ({
            ...node,
            // Convert position floats to numbers if needed
            position: {
              x: Number(node.position.x),
              y: Number(node.position.y)
            }
          })),
          edges: updatedData.edges
        }),
      });
      
      if (response.ok) {
        setSaveStatus('Changes saved successfully!');
        setTimeout(() => setSaveStatus(''), 3000);
      } else {
        setSaveStatus('Error saving changes');
      }
    } catch (error) {
      console.error('Error saving graph data:', error);
      setSaveStatus('Error saving changes');
    }
  };

  const handleManualRetry = () => {
    setRetryCount(prev => prev + 1);
  };

  if (loading && !error) {
    return (
      <div className="flex justify-center items-center h-full">
        Loading service map...
      </div>
    );
  }

  if (loading && error) {
    return (
      <div className="flex justify-center items-center h-full flex-col">
        <div className="mb-4">{error}</div>
        <div className="text-sm text-gray-500">Attempting to reconnect...</div>
      </div>
    );
  }

  if (error && !loading) {
    return (
      <div className="flex justify-center items-center h-full flex-col">
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
    <div className="h-full flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Microservices Architecture</h1>
        {saveStatus && (
          <div className={`save-status ${saveStatus.includes('Error') ? 'save-status-error' : 'save-status-success'}`}>
            {saveStatus}
          </div>
        )}
      </div>
      <div className="flex-1 border border-gray-300 rounded overflow-hidden">
        {graphData && <Graph initialData={graphData} onSave={handleSave} />}
      </div>
    </div>
  );
}