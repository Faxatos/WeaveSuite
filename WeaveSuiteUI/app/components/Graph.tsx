'use client';

import { useState, useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import '../styles/graph.css';

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

interface GraphProps {
  initialData: GraphData;
  onSave: (data: GraphData) => void;
}

export default function Graph({ initialData, onSave }: GraphProps) {
  const [graphData, setGraphData] = useState<GraphData>(initialData);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [editMode, setEditMode] = useState(false);
  const [showNodeModal, setShowNodeModal] = useState(false);
  const [showEdgeModal, setShowEdgeModal] = useState(false);
  const [newNodeName, setNewNodeName] = useState('');
  const [edgeSource, setEdgeSource] = useState<string | null>(null);
  const [edgeTarget, setEdgeTarget] = useState<string | null>(null);
  const [edgeLabel, setEdgeLabel] = useState('calls');
  const [saveStatus, setSaveStatus] = useState('');
  
  const cyRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const cytoscapeStylesheet = [
    {
      selector: 'node',
      style: {
        'background-color': '#4299e1',
        'label': 'data(label)',
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
      selector: 'node[serviceType = "gateway"]',
      style: {
        'background-color': '#f6ad55',
      }
    },
    {
      selector: 'edge',
      style: {
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
        'text-background-padding': 3,
      }
    },
    {
      selector: '.selected',
      style: {
        'border-width': 3,
        'border-color': '#ff0000'
      }
    }
  ];

  useEffect(() => {
    if (!containerRef.current) return;

    // Initialize cytoscape
    const cy = cytoscape({
      container: containerRef.current,
      elements: [...graphData.nodes, ...graphData.edges],
      style: cytoscapeStylesheet,
      layout: { name: 'preset' },
      userZoomingEnabled: true,
      userPanningEnabled: true,
      boxSelectionEnabled: false,
    });

    cyRef.current = cy;

    // Event listeners
    cy.on('tap', 'node, edge', (event) => {
      if (!editMode) return;
      
      const target = event.target;
      
      // Remove existing selection
      cy.elements().removeClass('selected');
      
      // Add selection to current element
      target.addClass('selected');
      setSelectedNode(target);

      // If a node is selected, set it as edge source for potential edge creation
      if (target.isNode()) {
        setEdgeSource(target.id());
      }
    });
    
    cy.on('tap', function(event) {
      // If clicking on background, deselect
      if (event.target === cy) {
        cy.elements().removeClass('selected');
        setSelectedNode(null);
      }
    });

    // Cleanup
    return () => {
      if (cy) {
        cy.destroy();
      }
    };
  }, [graphData, editMode]);

  // Find a suitable position for a new node
  const findNewNodePosition = () => {
    // Default position
    let position = { x: 300, y: 300 };
    
    // If there are existing nodes, try to find a position that doesn't overlap
    if (graphData.nodes.length > 0) {
      // Calculate the center of existing nodes
      const center = graphData.nodes.reduce(
        (acc, node) => ({
          x: acc.x + node.position.x / graphData.nodes.length,
          y: acc.y + node.position.y / graphData.nodes.length
        }),
        { x: 0, y: 0 }
      );
      
      // Place the new node in a random direction from center
      const angle = Math.random() * Math.PI * 2;
      const distance = 150 + Math.random() * 100; // Distance from center
      
      position = {
        x: center.x + Math.cos(angle) * distance,
        y: center.y + Math.sin(angle) * distance
      };
    }
    
    return position;
  };

  const openAddNodeModal = () => {
    setNewNodeName('');
    setShowNodeModal(true);
  };

  const addNode = () => {
    const name = newNodeName.trim() || 'New Service';
    const position = findNewNodePosition();
    
    const newNode: GraphNode = {
      data: {
        id: `service-${Date.now()}`,
        label: name,
        serviceType: 'microservice'
      },
      position
    };
    
    setGraphData(prev => ({
      nodes: [...prev.nodes, newNode],
      edges: [...prev.edges]
    }));
    
    setShowNodeModal(false);
  };

  const openAddEdgeModal = () => {
    if (!selectedNode || !selectedNode.isNode()) {
      alert('Please select a source node first');
      return;
    }
    
    setEdgeTarget(null);
    setEdgeLabel('calls');
    setShowEdgeModal(true);
  };

  const addEdge = () => {
    if (!edgeSource || !edgeTarget) {
      return;
    }
    
    const newEdge: GraphEdge = {
      data: {
        id: `edge-${Date.now()}`,
        source: edgeSource,
        target: edgeTarget,
        label: edgeLabel.trim() || 'calls'
      }
    };
    
    setGraphData(prev => ({
      nodes: [...prev.nodes],
      edges: [...prev.edges, newEdge]
    }));
    
    setShowEdgeModal(false);
    setEdgeTarget(null);
  };

  const removeSelected = () => {
    if (!selectedNode) return;
    
    const id = selectedNode.id();
    
    // Check if it's a node or edge
    if (selectedNode.isNode()) {
      // Also remove connected edges
      setGraphData(prev => ({
        nodes: prev.nodes.filter(node => node.data.id !== id),
        edges: prev.edges.filter(edge => edge.data.source !== id && edge.data.target !== id)
      }));
    } else {
      // It's an edge
      setGraphData(prev => ({
        nodes: [...prev.nodes],
        edges: prev.edges.filter(edge => edge.data.id !== id)
      }));
    }
    
    setSelectedNode(null);
  };

  const handleSave = () => {
    // Get the current positions from cytoscape
    const cy = cyRef.current;
    if (!cy) return;

    const updatedNodes = graphData.nodes.map(node => {
      const cyNode = cy.getElementById(node.data.id);
      return {
        data: node.data,
        position: cyNode.position()
      };
    });
    
    const updatedData = {
      nodes: updatedNodes,
      edges: graphData.edges
    };
    
    onSave(updatedData);
  };

  return (
    <div className="h-full flex flex-col">
      <div className="control-panel">
        <button 
          className="btn btn-primary"
          onClick={() => setEditMode(!editMode)}
        >
          {editMode ? 'Exit Edit Mode' : 'Edit Graph'}
        </button>
        
        {editMode && (
          <>
            <button 
              className="btn btn-success"
              onClick={openAddNodeModal}
            >
              Add Node
            </button>
            <button 
              className="btn btn-purple"
              onClick={openAddEdgeModal}
              disabled={!selectedNode || !selectedNode.isNode()}
            >
              Add Edge
            </button>
            <button 
              className="btn btn-danger"
              onClick={removeSelected}
              disabled={!selectedNode}
            >
              Remove Selected
            </button>
            <button 
              className="btn btn-warning"
              onClick={handleSave}
            >
              Save Changes
            </button>
          </>
        )}
      </div>
      
      <div className="flex-1 graph-container" ref={containerRef}>
        {/* Cytoscape will render here */}
      </div>

      {/* Add Node Modal */}
      {showNodeModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3 className="modal-title">Add New Microservice</h3>
              <button 
                className="close-button"
                onClick={() => setShowNodeModal(false)}
              >
                &times;
              </button>
            </div>
            <div className="form-group">
              <label className="form-label">Service Name</label>
              <input
                type="text"
                className="form-control"
                value={newNodeName}
                onChange={(e) => setNewNodeName(e.target.value)}
                placeholder="Enter service name"
              />
            </div>
            <div className="modal-footer">
              <button 
                className="btn cancel-btn"
                onClick={() => setShowNodeModal(false)}
              >
                Cancel
              </button>
              <button 
                className="btn btn-success"
                onClick={addNode}
              >
                Add Service
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Edge Modal */}
      {showEdgeModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3 className="modal-title">Add New Connection</h3>
              <button 
                className="close-button"
                onClick={() => setShowEdgeModal(false)}
              >
                &times;
              </button>
            </div>
            <div className="form-group">
              <label className="form-label">From Service</label>
              <input
                type="text"
                className="form-control"
                value={edgeSource ? graphData.nodes.find(n => n.data.id === edgeSource)?.data.label || edgeSource : ''}
                disabled
              />
            </div>
            <div className="form-group">
              <label className="form-label">To Service</label>
              <div className="radio-group">
                {graphData.nodes.filter(node => node.data.id !== edgeSource).map((node) => (
                  <div key={node.data.id} className="radio-option">
                    <input
                      type="radio"
                      id={`node-${node.data.id}`}
                      name="targetNode"
                      value={node.data.id}
                      checked={edgeTarget === node.data.id}
                      onChange={() => setEdgeTarget(node.data.id)}
                    />
                    <label htmlFor={`node-${node.data.id}`}>{node.data.label}</label>
                  </div>
                ))}
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Connection Label</label>
              <input
                type="text"
                className="form-control"
                value={edgeLabel}
                onChange={(e) => setEdgeLabel(e.target.value)}
                placeholder="e.g., calls, authenticates, processes"
              />
            </div>
            <div className="modal-footer">
              <button 
                className="btn cancel-btn"
                onClick={() => setShowEdgeModal(false)}
              >
                Cancel
              </button>
              <button 
                className="btn btn-success"
                onClick={addEdge}
                disabled={!edgeTarget}
              >
                Add Connection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}