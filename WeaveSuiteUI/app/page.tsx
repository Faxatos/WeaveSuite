'use client';

import { useState, useEffect } from 'react';
import Graph from './components/Graph';

interface GraphNode {
  data: {
    id: string;
    label: string;
    serviceType: string;
  };
  position: {
    x: number;
    y: number;
  };
}

interface GraphEdge {
  data: {
    id: string;
    source: string;
    target: string;
    label: string;
  };
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
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
        body: JSON.stringify(updatedData),
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