'use client';

import { useState } from 'react';
import { CheckCircle, XCircle, AlertCircle, ChevronDown, ChevronUp} from 'lucide-react';

interface MicroserviceSpec {
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

interface SpecItemProps {
  spec: MicroserviceSpec;
}

export default function SpecItem({ spec }: SpecItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const getStatusIcon = () => {
    switch (spec.status) {
      case 'available': return <CheckCircle className="text-green-500" size={20} />;
      case 'unavailable': return <XCircle className="text-yellow-500" size={20} />;
      case 'error': return <AlertCircle className="text-red-500" size={20} />;
    }
  };

  const getStatusClass = () => {
    switch (spec.status) {
      case 'available': return 'bg-green-100 text-green-800';
      case 'unavailable': return 'bg-yellow-100 text-yellow-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSpecInfo = () => {
    try {
      const specObj = spec.spec as Record<string, unknown>;
      const info = specObj?.info as Record<string, unknown> | undefined;
      const paths = specObj?.paths as Record<string, unknown> | undefined;
      const components = specObj?.components as Record<string, unknown> | undefined;
      
      return {
        title: (info?.title as string) || spec.microservice.name,
        version: (info?.version as string) || spec.microservice.version || 'Unknown',
        description: (info?.description as string) || 'No description available',
        pathCount: paths ? Object.keys(paths).length : 0,
        componentCount: components ? Object.keys(components).length : 0,
      };
    } catch {
      return {
        title: spec.microservice.name,
        version: spec.microservice.version || 'Unknown',
        description: 'Error parsing spec',
        pathCount: 0,
        componentCount: 0,
      };
    }
  };

  const specInfo = getSpecInfo();

  const copySpecToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(spec.spec, null, 2));
      // You might want to add a toast notification here
    } catch (error) {
      console.error('Failed to copy spec:', error);
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
          <div>
            <span className="font-medium">{spec.microservice.name}</span>
            {spec.microservice.version && (
              <span className="ml-2 text-xs text-gray-500">v{spec.microservice.version}</span>
            )}
          </div>
          <span className={`text-xs px-2 py-1 rounded-full ${getStatusClass()}`}>
            {spec.status.charAt(0).toUpperCase() + spec.status.slice(1)}
          </span>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-500">
            {specInfo.pathCount} endpoints
          </div>
          <div className="text-sm text-gray-500">
            {formatDate(spec.fetched_at)}
          </div>
          {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </div>
      </div>

      {isExpanded && (
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-sm font-medium text-gray-500">Service URL</p>
              <p className="mt-1 text-sm">{spec.microservice.url}</p>
            </div>

            <div>
              <p className="text-sm font-medium text-gray-500">API Version</p>
              <p className="mt-1 text-sm">{specInfo.version}</p>
            </div>

            <div>
              <p className="text-sm font-medium text-gray-500">Endpoints</p>
              <p className="mt-1 text-sm">{specInfo.pathCount} paths</p>
            </div>

            <div>
              <p className="text-sm font-medium text-gray-500">Components</p>
              <p className="mt-1 text-sm">{specInfo.componentCount} schemas</p>
            </div>

            {specInfo.description && specInfo.description !== 'No description available' && (
              <div className="col-span-2">
                <p className="text-sm font-medium text-gray-500">Description</p>
                <p className="mt-1 text-sm text-gray-700">{specInfo.description}</p>
              </div>
            )}
          </div>

          {/* OpenAPI Spec Display */}
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-gray-500">OpenAPI Specification</p>
              <button
                onClick={copySpecToClipboard}
                className="px-3 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
              >
                Copy JSON
              </button>
            </div>
            <div className="relative">
              <pre className="p-4 bg-gray-800 text-gray-100 rounded text-xs overflow-x-auto max-h-96 overflow-y-auto">
                {JSON.stringify(spec.spec, null, 2)}
              </pre>
            </div>
          </div>

          {/* Quick Spec Summary */}
          {(() => {
            const specObj = spec.spec as Record<string, unknown>;
            const paths = specObj?.paths as Record<string, Record<string, unknown>> | undefined;
            return spec.spec && typeof spec.spec === 'object' && paths && Object.keys(paths).length > 0 ? (
              <div className="mt-4">
                <p className="text-sm font-medium text-gray-500 mb-2">Available Endpoints</p>
                <div className="grid grid-cols-1 gap-2 max-h-40 overflow-y-auto">
                  {Object.entries(paths).map(([path, methods]) => (
                    <div key={path} className="flex items-center justify-between p-2 bg-white rounded border">
                      <code className="text-xs text-gray-700">{path}</code>
                      <div className="flex space-x-1">
                        {Object.keys(methods).map((method: string) => (
                          <span
                            key={method}
                            className={`inline-block px-2 py-1 text-xs font-medium rounded ${
                              method.toUpperCase() === 'GET' ? 'bg-blue-100 text-blue-800' : 
                              method.toUpperCase() === 'POST' ? 'bg-green-100 text-green-800' : 
                              method.toUpperCase() === 'PUT' ? 'bg-yellow-100 text-yellow-800' : 
                              method.toUpperCase() === 'DELETE' ? 'bg-red-100 text-red-800' : 
                              'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {method.toUpperCase()}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : null;
          })()}
        </div>
      )}
    </div>
  );
}