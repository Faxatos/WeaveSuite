'use client';

import { useState, useEffect } from 'react';
import Graph from './components/Graph';

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
  const [saveStatus, setSaveStatus] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/graph');
        const data = await response.json();
        setGraphData(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching graph data:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

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

  if (loading) {
    return <div className="flex justify-center items-center h-full">Loading...</div>;
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