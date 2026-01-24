from sqlalchemy.orm import Session
import logging
from typing import List, Dict, Any
from db.models import Link, Microservice

class CoverageService:
    def __init__(self, db: Session):
        self.db = db
        
    #ToDo: add function for links generation based on test coverage analysis (Istio)

    #ToDo: add function for microservices positions generation based on some layout algorithm (e.g., force-directed)

    def _store_positions(self, positions: List[Dict]) -> int:
        """Update microservice coordinates"""
        logging.info(f"Storing {len(positions)} microservice positions...")
        updated = 0
        for pos in positions:
            ms = self.db.query(Microservice).filter_by(
                name=pos["name"], 
                namespace=pos["namespace"]
            ).first()
            if ms:
                logging.debug(f"Updating position for {pos['name']}/{pos['namespace']}: ({pos.get('x', 0)}, {pos.get('y', 0)})")
                ms.x = pos.get("x", 0.0)
                ms.y = pos.get("y", 0.0)
                updated += 1
            else:
                logging.warning(f"Microservice not found for position update: {pos['name']}/{pos['namespace']}")
        
        self.db.commit()
        logging.info(f"Successfully updated positions for {updated} microservices")
        return updated


    def _store_links(self, links: List[Dict]) -> int:
            """Replace existing links with new ones"""
            logging.info(f"Storing {len(links)} microservice links...")
            created = 0
            for link in links:
                source = self._get_microservice(link["source_name"], link["source_namespace"])
                target = self._get_microservice(link["target_name"], link["target_namespace"])
                if source and target:
                    logging.debug(f"Creating link: {link['source_name']}/{link['source_namespace']} -> {link['target_name']}/{link['target_namespace']} ({link.get('label', 'No label')})")
                    self.db.add(Link(
                        source_id=source.id,
                        target_id=target.id,
                        label=link.get("label", "")
                    ))
                    created += 1
                else:
                    if not source:
                        logging.warning(f"Source microservice not found for link: {link['source_name']}/{link['source_namespace']}")
                    if not target:
                        logging.warning(f"Target microservice not found for link: {link['target_name']}/{link['target_namespace']}")
            
            self.db.commit()
            logging.info(f"Successfully created {created} links")
            return created
    
    def get_graph(self) -> Dict[str, Any]:
        """Get all microservices and their links"""
        try:
            microservices = self.db.query(Microservice).all()
            links = self.db.query(Link).all()
            
            nodes = []
            for ms in microservices:
                node = {
                    "data": {
                        "id": ms.id,
                        "name": ms.name,
                        "namespace": ms.namespace,
                        "endpoint": ms.endpoint,
                        "service_type": ms.service_type
                    },
                    "position": {
                        "x": ms.x,
                        "y": ms.y
                    }
                }
                nodes.append(node)
                
            edges = []
            for link in links:
                edge = {
                    "data": {
                        "id": link.id,
                        "source": link.source_id,
                        "target": link.target_id,
                        "label": link.label or ""
                    }
                }
                edges.append(edge)
                
            print(f"Returning graph with {len(nodes)} nodes and {len(edges)} edges")
            return {
                "nodes": nodes,
                "edges": edges
            }
            
        except Exception as e:
            logging.error(f"Failed to get service map: {str(e)}")
            raise

