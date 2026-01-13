"""
Graph-based pedestrian network router using HK's 3D Pedestrian Network.
Builds a routable graph from GeoJSON and provides A* pathfinding.
"""

import json
import heapq
import math
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

@dataclass
class Node:
    """A node in the pedestrian network"""
    id: str
    lat: float
    lng: float
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return self.id == other.id

@dataclass
class Edge:
    """An edge between two nodes"""
    from_node: Node
    to_node: Node
    distance: float
    
    def __lt__(self, other):
        return self.distance < other.distance

class PedestrianNetworkGraph:
    """Graph representation of the pedestrian network"""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, List[Edge]] = {}
        self.loaded = False
    
    @staticmethod
    def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance in meters between two lat/lng points"""
        R = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lng2 - lng1)
        
        a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    def load_from_geojson(self, geojson_file: Path) -> bool:
        """Load the pedestrian network from a GeoJSON file"""
        try:
            with open(geojson_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different GeoJSON structures
            features = data.get('features', [])
            
            node_counter = 0
            
            # First pass: extract all nodes from line features
            for feature in features:
                if feature.get('type') != 'Feature':
                    continue
                
                geometry = feature.get('geometry', {})
                geom_type = geometry.get('type')
                coords = geometry.get('coordinates', [])
                
                if geom_type == 'LineString' and coords:
                    # Create nodes at each vertex of the linestring
                    for i, (lng, lat) in enumerate(coords):
                        node_id = f"node_{node_counter}_{i}"
                        if node_id not in self.nodes:
                            self.nodes[node_id] = Node(id=node_id, lat=lat, lng=lng)
                            self.edges[node_id] = []
                        node_counter += 1
            
            # Second pass: create edges along linestrings
            for feature in features:
                geometry = feature.get('geometry', {})
                geom_type = geometry.get('type')
                coords = geometry.get('coordinates', [])
                
                if geom_type == 'LineString' and len(coords) > 1:
                    # Connect consecutive vertices
                    for i in range(len(coords) - 1):
                        lng1, lat1 = coords[i]
                        lng2, lat2 = coords[i + 1]
                        
                        # Find or create nodes
                        node1_id = self._find_or_create_node(lat1, lng1)
                        node2_id = self._find_or_create_node(lat2, lng2)
                        
                        if node1_id and node2_id:
                            node1 = self.nodes[node1_id]
                            node2 = self.nodes[node2_id]
                            distance = self.haversine(lat1, lng1, lat2, lng2)
                            
                            # Add bidirectional edges (pedestrians can walk both ways)
                            self.edges[node1_id].append(Edge(node1, node2, distance))
                            self.edges[node2_id].append(Edge(node2, node1, distance))
            
            self.loaded = True
            print(f"✓ Loaded pedestrian network: {len(self.nodes)} nodes")
            return True
        
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Warning: Error loading pedestrian network: {e}")
            return False
    
    def _find_or_create_node(self, lat: float, lng: float, tolerance: float = 0.0001) -> Optional[str]:
        """Find existing node within tolerance or create new one"""
        for node_id, node in self.nodes.items():
            if abs(node.lat - lat) < tolerance and abs(node.lng - lng) < tolerance:
                return node_id
        
        node_id = f"node_{len(self.nodes)}"
        self.nodes[node_id] = Node(id=node_id, lat=lat, lng=lng)
        self.edges[node_id] = []
        return node_id
    
    def find_nearest_node(self, lat: float, lng: float, max_distance: float = 500) -> Optional[Node]:
        """Find the nearest node within max_distance meters"""
        nearest = None
        min_dist = max_distance
        
        for node in self.nodes.values():
            dist = self.haversine(lat, lng, node.lat, node.lng)
            if dist < min_dist:
                nearest = node
                min_dist = dist
        
        return nearest
    
    def a_star(self, start: Node, end: Node) -> Tuple[Optional[List[Node]], float]:
        """
        A* pathfinding algorithm.
        Returns: (path as list of nodes, total distance in meters) or (None, 0)
        """
        if not self.loaded:
            return None, 0
        
        # Find start node ID
        start_id = None
        end_id = None
        for nid, node in self.nodes.items():
            if node == start:
                start_id = nid
            if node == end:
                end_id = nid
        
        if not start_id or not end_id:
            return None, 0
        
        # A* algorithm
        open_set = []
        heapq.heappush(open_set, (0, start_id))
        
        came_from = {}
        g_score = {node_id: float('inf') for node_id in self.nodes}
        g_score[start_id] = 0
        
        f_score = {node_id: float('inf') for node_id in self.nodes}
        f_score[start_id] = self.haversine(
            self.nodes[start_id].lat, self.nodes[start_id].lng,
            self.nodes[end_id].lat, self.nodes[end_id].lng
        )
        
        closed_set = set()
        
        while open_set:
            _, current_id = heapq.heappop(open_set)
            
            if current_id in closed_set:
                continue
            
            if current_id == end_id:
                # Reconstruct path
                path = []
                node_id = end_id
                while node_id in came_from:
                    path.append(self.nodes[node_id])
                    node_id = came_from[node_id]
                path.append(self.nodes[start_id])
                path.reverse()
                return path, g_score[end_id]
            
            closed_set.add(current_id)
            
            for edge in self.edges.get(current_id, []):
                neighbor_id = None
                for nid, node in self.nodes.items():
                    if node == edge.to_node:
                        neighbor_id = nid
                        break
                
                if not neighbor_id or neighbor_id in closed_set:
                    continue
                
                tentative_g = g_score[current_id] + edge.distance
                
                if tentative_g < g_score[neighbor_id]:
                    came_from[neighbor_id] = current_id
                    g_score[neighbor_id] = tentative_g
                    h_score = self.haversine(
                        self.nodes[neighbor_id].lat, self.nodes[neighbor_id].lng,
                        self.nodes[end_id].lat, self.nodes[end_id].lng
                    )
                    f_score[neighbor_id] = tentative_g + h_score
                    heapq.heappush(open_set, (f_score[neighbor_id], neighbor_id))
        
        return None, 0
    
    def find_route(self, start_lat: float, start_lng: float, 
                   end_lat: float, end_lng: float) -> Tuple[Optional[List[Tuple[float, float]]], float]:
        """
        Find walking route between two points using the pedestrian network.
        Returns: (polyline as [(lat, lng), ...], distance in meters) or (None, 0)
        """
        if not self.loaded:
            return None, 0
        
        # Find nearest nodes
        start_node = self.find_nearest_node(start_lat, start_lng)
        end_node = self.find_nearest_node(end_lat, end_lng)
        
        if not start_node or not end_node:
            return None, 0
        
        # Run A*
        path, distance = self.a_star(start_node, end_node)
        
        if path:
            polyline = [(node.lat, node.lng) for node in path]
            return polyline, distance
        
        return None, 0


# Global instance
_network = None

def load_pedestrian_network(geojson_file: str = "data/hk_pedestrian_network.geojson") -> bool:
    """Initialize the global pedestrian network"""
    global _network
    _network = PedestrianNetworkGraph()
    try:
        return _network.load_from_geojson(Path(geojson_file))
    except Exception as e:
        print(f"Warning: Could not load pedestrian network: {e}")
        return False

def route_walking(start_lat: float, start_lng: float, 
                  end_lat: float, end_lng: float) -> Tuple[Optional[List[Tuple[float, float]]], float]:
    """Get walking route using pedestrian network"""
    if not _network or not _network.loaded:
        return None, 0
    return _network.find_route(start_lat, start_lng, end_lat, end_lng)
