'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import cytoscape from 'cytoscape';
import '../styles/graph.css';

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

interface GraphProps {
  initialData: GraphData;
  onSave: (data: GraphData) => void;
}

export default function Graph({ initialData, onSave }: GraphProps) {
  const [graphData, setGraphData] = useState<GraphData>(initialData);
  const [selectedElement, setSelectedElement] = useState<cytoscape.SingularElementReturnValue | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [showNodeModal, setShowNodeModal] = useState(false);
  const [showEdgeModal, setShowEdgeModal] = useState(false);
  const [newNodeData, setNewNodeData] = useState({
    name: '',
    namespace: 'default',
    endpoint: '',
    service_type: 'microservice'
  });
  const [edgeData, setEdgeData] = useState({
    source: 0,
    target: 0,
    label: 'calls'
  });
  
  const cyRef = useRef<cytoscape.Core | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const cytoscapeStylesheet: cytoscape.StylesheetCSS[] = [
    {
      selector: 'node',
      css: {
        'background-color': '#4299e1',
        'label': 'data(name)',
        'color': '#000000',
        'text-valign': 'center',
        'text-halign': 'center',
        'width': 120,
        'height': 50,
        'shape': 'roundrectangle',
        'font-size': 12,
        'text-wrap': 'wrap',
      }
    },
    {
      selector: 'node[service_type = "gateway"]',
      css: {
        'background-color': '#f6ad55',
      }
    },
    {
      selector: 'edge',
      css: {
        'width': 2,
        'line-color': '#a0aec0',
        'target-arrow-color': '#a0aec0',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'label': 'data(label)',
        'font-size': 10,
        'text-rotation': 'autorotate',
        'text-background-opacity': 1,
        'text-background-color': 'white',
        'text-background-padding': '3',
      }
    },
    {
      selector: '.selected',
      css: {
        'border-width': 3,
        'border-color': '#ff0000'
      }
    }
  ];

  // Function to properly convert graph data for Cytoscape
  const convertDataForCytoscape = () => {
    // Create a set of valid node IDs for validation
    const validNodeIds = new Set(graphData.nodes.map(node => node.data.id));
    
    // Log all node IDs to verify what we have
    console.log("Valid node IDs:", [...validNodeIds]);
    
    // Format nodes with string IDs for Cytoscape
    const nodes = graphData.nodes.map(node => ({
      data: {
        id: String(node.data.id),
        name: node.data.name,
        namespace: node.data.namespace,
        endpoint: node.data.endpoint,
        service_type: node.data.service_type
      },
      position: {
        x: Number(node.position.x),
        y: Number(node.position.y)
      }
    }));
    
    // Filter and format edges with string IDs and correct source/target references
    // Make edge IDs unique by prefixing them with 'e' to avoid collision with node IDs
    const edges = graphData.edges
      .map(edge => {
        return {
          data: {
            id: `e${edge.data.id}`, // Prefix with 'e' to make unique
            source: String(edge.data.source),
            target: String(edge.data.target),
            label: edge.data.label || '' // Ensure label exists
          }
        };
      });
    
    console.log("Converted nodes:", nodes);
    console.log("Converted edges:", edges);
    
    return [...nodes, ...edges];
  };

  // Function to initialize or update the graph
  const initializeGraph = useCallback(() => {
    if (!containerRef.current) return;
    
    // Clean up existing instance if it exists
    if (cyRef.current) {
      cyRef.current.destroy();
    }
    
    console.log("Initializing graph with data:", graphData);
    
    // Create a clean container to avoid initialization issues
    while (containerRef.current.firstChild) {
      containerRef.current.removeChild(containerRef.current.firstChild);
    }
    
    // Convert the data to the format Cytoscape expects
    const elements = convertDataForCytoscape();
    
    try {
      // Create new Cytoscape instance with all elements
      const cy = cytoscape({
        container: containerRef.current,
        elements: elements as cytoscape.ElementDefinition[], // Properly typed instead of any
        style: cytoscapeStylesheet,
        layout: { name: 'preset' },
        userZoomingEnabled: true,
        userPanningEnabled: true,
        boxSelectionEnabled: false,
      });
      
      // Store reference
      cyRef.current = cy;
      
      // Set up event handlers
      cy.on('tap', 'node, edge', (event) => {
        if (!editMode) return;
        
        const target = event.target;
        cy.elements().removeClass('selected');
        target.addClass('selected');
        setSelectedElement(target);
        
        if (target.isNode()) {
          const nodeId = parseInt(target.id(), 10);
          setEdgeData(prev => ({ ...prev, source: nodeId }));
        }
      });
      
      cy.on('tap', (event) => {
        if (event.target === cy) {
          cy.elements().removeClass('selected');
          setSelectedElement(null);
        }
      });
      
      // Force a layout refresh
      cy.layout({ name: 'preset' }).run();
    } catch (error) {
      console.error("Error initializing Cytoscape:", error);
    }
  }, [graphData, editMode]);

  // Initialize graph when data changes
  useEffect(() => {
    initializeGraph();
    
    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
      }
    };
  }, [initializeGraph]);

  const findNewNodePosition = () => {
    const position = { x: 300, y: 300 };
    if (graphData.nodes.length > 0) {
      const center = graphData.nodes.reduce(
        (acc, node) => ({
          x: acc.x + node.position.x / graphData.nodes.length,
          y: acc.y + node.position.y / graphData.nodes.length
        }),
        { x: 0, y: 0 }
      );
      
      const angle = Math.random() * Math.PI * 2;
      const distance = 150 + Math.random() * 100;
      
      position.x = center.x + Math.cos(angle) * distance;
      position.y = center.y + Math.sin(angle) * distance;
    }
    return position;
  };

  const addNode = () => {
    const newNodeId = Math.max(0, ...graphData.nodes.map(n => n.data.id)) + 1;
    const position = findNewNodePosition();
    
    const newNode: MicroserviceNode = {
      data: {
        id: newNodeId,
        name: newNodeData.name || `service-${newNodeId}`,
        namespace: newNodeData.namespace,
        endpoint: newNodeData.endpoint || `http://service-${newNodeId}:8080`, //ToDo: allow user to set endpoint
        service_type: newNodeData.service_type
      },
      position
    };
    
    setGraphData(prev => ({
      nodes: [...prev.nodes, newNode],
      edges: prev.edges
    }));
    
    setShowNodeModal(false);
    setNewNodeData({
      name: '',
      namespace: 'default',
      endpoint: '',
      service_type: 'microservice'
    });
  };

  const addEdge = () => {
    if (edgeData.source === 0 || edgeData.target === 0 || edgeData.source === edgeData.target) {
      alert('Please select valid source and target nodes');
      return;
    }
    
    // Check if this edge already exists
    const edgeExists = graphData.edges.some(
      e => e.data.source === edgeData.source && e.data.target === edgeData.target
    );
    
    if (edgeExists) {
      alert('This connection already exists');
      return;
    }
    
    const newEdgeId = Math.max(0, ...graphData.edges.map(e => e.data.id)) + 1;
    
    const newEdge: ServiceLink = {
      data: {
        id: newEdgeId,
        source: edgeData.source,
        target: edgeData.target,
        label: edgeData.label.trim() || 'calls'
      }
    };
    
    setGraphData(prev => ({
      nodes: prev.nodes,
      edges: [...prev.edges, newEdge]
    }));
    
    setShowEdgeModal(false);
    setEdgeData({ source: 0, target: 0, label: 'calls' });
  };

  const removeSelected = () => {
    if (!selectedElement) return;
    
    const elementId = parseInt(selectedElement.data('id'), 10);
    
    setGraphData(prev => ({
      nodes: prev.nodes.filter(n => 
        selectedElement.isNode() ? n.data.id !== elementId : true
      ),
      edges: prev.edges.filter(e => 
        selectedElement.isEdge() ? e.data.id !== elementId : 
        !(e.data.source === elementId || e.data.target === elementId)
      )
    }));
    
    setSelectedElement(null);
  };

  const handleSave = () => {
    const cy = cyRef.current;
    if (!cy) return;

    const updatedNodes = graphData.nodes.map(node => {
      const element = cy.getElementById(node.data.id.toString());
      return {
        data: node.data,
        position: element.length ? element.position() : node.position
      };
    });

    const normalizedData = {
      nodes: updatedNodes.map(node => ({
        ...node,
        position: {
          x: Number(node.position.x),
          y: Number(node.position.y)
        }
      })),
      edges: graphData.edges
    };
  
    onSave(normalizedData);
  };

  return (
    <div className="h-full flex flex-col">
      <div className="control-panel">
        <button onClick={() => setEditMode(!editMode)}>
          {editMode ? 'Exit Edit Mode' : 'Edit Graph'}
        </button>
        
        {editMode && (
          <>
            <button onClick={() => setShowNodeModal(true)}>
              Add Node
            </button>
            <button 
              onClick={() => setShowEdgeModal(true)}
              disabled={!selectedElement?.isNode()}
            >
              Add Edge
            </button>
            <button 
              onClick={removeSelected}
              disabled={!selectedElement}
            >
              Remove Selected
            </button>
            <button onClick={handleSave}>
              Save Changes
            </button>
          </>
        )}
      </div>
      
      <div className="flex-1 graph-container" ref={containerRef} />

      {/* Node Creation Modal */}
      {showNodeModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>Add New Microservice</h3>
            <div className="form-group">
              <label>Service Name</label>
              <input
                value={newNodeData.name}
                onChange={e => setNewNodeData({ ...newNodeData, name: e.target.value })}
                placeholder="Service name"
              />
            </div>
            <div className="form-group">
              <label>Endpoint URL</label>
              <input
                value={newNodeData.endpoint}
                onChange={e => setNewNodeData({ ...newNodeData, endpoint: e.target.value })}
                placeholder="http://service:port"
              />
            </div>
            <div className="form-group">
              <label>Service Type</label>
              <select
                value={newNodeData.service_type}
                onChange={e => setNewNodeData({ ...newNodeData, service_type: e.target.value })}
              >
                <option value="microservice">Microservice</option>
                <option value="gateway">Gateway</option>
              </select>
            </div>
            <div className="modal-actions">
              <button onClick={() => setShowNodeModal(false)}>Cancel</button>
              <button onClick={addNode}>Add Service</button>
            </div>
          </div>
        </div>
      )}

      {/* Edge Creation Modal */}
      {showEdgeModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>Create Connection</h3>
            <div className="form-group">
              <label>Source Service</label>
              <input 
                value={graphData.nodes.find(n => n.data.id === edgeData.source)?.data.name || ''}
                disabled 
              />
            </div>
            <div className="form-group">
              <label>Target Service</label>
              <select
                value={edgeData.target}
                onChange={e => setEdgeData({ ...edgeData, target: Number(e.target.value) })}
              >
                <option value={0}>Select target</option>
                {graphData.nodes
                  .filter(n => n.data.id !== edgeData.source)
                  .map(node => (
                    <option key={node.data.id} value={node.data.id}>
                      {node.data.name}
                    </option>
                  ))}
              </select>
            </div>
            <div className="form-group">
              <label>Connection Label</label>
              <input
                value={edgeData.label}
                onChange={e => setEdgeData({ ...edgeData, label: e.target.value })}
                placeholder="Connection label"
              />
            </div>
            <div className="modal-actions">
              <button onClick={() => setShowEdgeModal(false)}>Cancel</button>
              <button onClick={addEdge} disabled={!edgeData.target}>
                Create Connection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 