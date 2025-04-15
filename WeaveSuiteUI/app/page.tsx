'use client';
import { useEffect, useState } from 'react';
import Graph from './components/Graph';

export default function Home() {
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch('/api/graph');
        const data = await response.json();
        setGraphData(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching graph data:', error);
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  return (
    <div className="space-y-6 h-full flex flex-col">
      <h1 className="text-2xl font-bold">Microservices Architecture</h1>
      <div className="bg-white p-6 rounded-lg shadow-md flex-1">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : graphData ? (
          <div className="h-full">
            <Graph data={graphData} />
          </div>
        ) : (
          <p>Failed to load graph data.</p>
        )}
      </div>
    </div>
  );
}