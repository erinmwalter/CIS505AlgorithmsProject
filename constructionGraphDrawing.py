import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from graphDrawing import CityGrid
import heapq

class CityGridConstruction:
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        self.graph = defaultdict(list)  # adjacency list
        self.fire_station = None
        
        # Road types and their weights
        self.HIGHWAY = 1      # Green lines
        self.NORMAL = 2       # Orange lines  
        self.CONGESTED = 4    # Red lines
        self.CONSTRUCTION = None  # Purple lines 
        self.AFFECTED = None      # Dark Orange lines
        
        # Track construction and affected roads
        self.construction_roads = set()
        self.affected_roads = set()
        
        self.setup_grid()
        
    def coord_to_id(self, row, col):
        """Convert (row, col) coordinates to a single ID"""
        return row * self.cols + col
    
    def id_to_coord(self, node_id):
        """Convert node ID back to (row, col) coordinates"""
        return node_id // self.cols, node_id % self.cols
    
    def add_connection(self, r1, c1, r2, c2, weight, road_type='normal'):
        id1 = self.coord_to_id(r1, c1)
        id2 = self.coord_to_id(r2, c2)
        self.graph[id1].append((id2, weight))
        self.graph[id2].append((id1, weight))
        
        # Track special road types
        edge = tuple(sorted([(r1, c1), (r2, c2)]))
        if road_type == 'construction':
            self.construction_roads.add(edge)
        elif road_type == 'affected':
            self.affected_roads.add(edge)
    
    def setup_grid(self):   
        # Define construction areas (these will get +6 weight)
        construction_segments = [
            ((1, 2), (2, 2)),  # Main construction
            ((2, 2), (3, 2))   # Main construction
        ]
        
        affected_segments = [
            ((0, 2), (1, 2)),  # Connected to construction
            ((1, 2), (1, 1)),  # Connected to construction
            ((2, 2), (2, 1)),  # Connected to construction
            ((2, 2), (2, 3)),  # Connected to construction
            ((3, 2), (4, 2)),  # Connected to construction
            ((3, 2), (3, 3))   # Connected to construction
        ]
        
        # HIGHWAY CONNECTIONS (Green lines)
        highway_connections = [
            ((0, 0), (0, 1)),
            ((0, 1), (0, 2)),
            ((0, 2), (1, 2)),  # This will be affected
            ((1, 2), (2, 2)),  # This is under construction
            ((2, 2), (3, 2)),  # This is under construction
            ((3, 2), (4, 2))   # This will be affected
        ]
        
        # NORMAL ROAD CONNECTIONS (Orange/Yellow lines)
        normal_connections = [
            ((0, 2), (0, 3)),
            ((0, 4), (1, 4)),
            ((0, 3), (0, 4)),
            ((1, 0), (1, 1)),
            ((1, 3), (1, 4)),
            ((2, 3), (2, 4)),
            ((3, 0), (3, 1)),
            ((4, 0), (4, 1)),
            ((4, 1), (4, 2)),
            ((4, 3), (4, 4)),
            ((2, 3), (3, 3)),
            ((2, 4), (3, 4)), 
        ]
        
        # CONGESTED CONNECTIONS (Red lines)
        congested_connections = [
            ((0, 1), (1, 1)),
            ((1, 1), (2, 1)),
            ((2, 1), (3, 1)),
            ((3, 1), (4, 1)),
            ((1, 1), (1, 2)),  # This will be affected
            ((2, 0), (2, 1)),
            ((2, 1), (2, 2)),  # This will be affected
            ((2, 2), (2, 3)),  # This will be affected
            ((1, 3), (2, 3)),
            ((2, 3), (3, 3)),  # This will be affected
            ((3, 3), (4, 3)),
            ((1, 0), (2, 0)),
            ((3, 0), (4, 0)),
            ((4, 2), (4, 3)),
            ((3, 2), (3, 3)),  # This will be affected
            ((3, 3), (3, 4)),
        ]
        
        # Add all connections with appropriate weights
        for (r1, c1), (r2, c2) in highway_connections:
            base_weight = self.HIGHWAY
            road_type = 'normal'
            
            if ((r1, c1), (r2, c2)) in construction_segments or ((r2, c2), (r1, c1)) in construction_segments:
                # Construction: original weight + 6
                weight = base_weight + 6
                road_type = 'construction'
            elif ((r1, c1), (r2, c2)) in affected_segments or ((r2, c2), (r1, c1)) in affected_segments:
                # Affected by construction: original weight + 2
                weight = base_weight + 2
                road_type = 'affected'
            else:
                weight = base_weight
                
            self.add_connection(r1, c1, r2, c2, weight, road_type)
            
        for (r1, c1), (r2, c2) in normal_connections:
            base_weight = self.NORMAL
            road_type = 'normal'
            
            if ((r1, c1), (r2, c2)) in construction_segments or ((r2, c2), (r1, c1)) in construction_segments:
                weight = base_weight + 6
                road_type = 'construction'
            elif ((r1, c1), (r2, c2)) in affected_segments or ((r2, c2), (r1, c1)) in affected_segments:
                weight = base_weight + 2
                road_type = 'affected'
            else:
                weight = base_weight
                
            self.add_connection(r1, c1, r2, c2, weight, road_type)
            
        for (r1, c1), (r2, c2) in congested_connections:
            base_weight = self.CONGESTED
            road_type = 'normal'
            
            if ((r1, c1), (r2, c2)) in construction_segments or ((r2, c2), (r1, c1)) in construction_segments:
                weight = base_weight + 6
                road_type = 'construction'
            elif ((r1, c1), (r2, c2)) in affected_segments or ((r2, c2), (r1, c1)) in affected_segments:
                weight = base_weight + 2
                road_type = 'affected'
            else:
                weight = base_weight
                
            self.add_connection(r1, c1, r2, c2, weight, road_type)
    
    def set_fire_station(self, row, col):
        self.fire_station = self.coord_to_id(row, col)
    
    def visualize_grid(self):
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        
        # Create the grid background
        for i in range(self.rows + 1):
            ax.axhline(y=i-0.5, color='lightgray', linewidth=0.5)
        for i in range(self.cols + 1):
            ax.axvline(x=i-0.5, color='lightgray', linewidth=0.5)
        
        # Draw fire station area
        fr, fc = self.id_to_coord(self.fire_station)
        fire_square = plt.Rectangle((fc-0.5, fr-0.5), 1, 1, facecolor='red', alpha=0.7, edgecolor='darkred', linewidth=2)
        ax.add_patch(fire_square)
        
        # Draw roads with different colors based on weights and construction status
        drawn_edges = set()
        
        for node_id in self.graph:
            r, c = self.id_to_coord(node_id)
            
            for neighbor_id, weight in self.graph[node_id]:
                nr, nc = self.id_to_coord(neighbor_id)
                
                # Create a unique edge identifier (smaller id first)
                edge_key = (min(node_id, neighbor_id), max(node_id, neighbor_id))
                
                if edge_key not in drawn_edges:
                    drawn_edges.add(edge_key)
                    
                    # Check if this is a construction or affected road
                    coord_edge = tuple(sorted([(r, c), (nr, nc)]))
                    
                    if coord_edge in self.construction_roads:
                        color = 'purple'
                        linewidth = 8
                        alpha = 0.9
                    elif coord_edge in self.affected_roads:
                        color = '#FF4500'
                        linewidth = 6
                        alpha = 0.8
                    else:
                        # Original road coloring based on base weight
                        if weight <= 1:
                            color = 'green'
                            linewidth = 8
                            alpha = 0.9
                        elif weight <= 2:
                            color = 'orange'
                            linewidth = 6
                            alpha = 0.8
                        else:
                            color = 'red'
                            linewidth = 6
                            alpha = 0.8
                    
                    # Draw the road
                    ax.plot([c, nc], [r, nr], color=color, linewidth=linewidth, alpha=alpha)
        
        # Mark intersections
        for r in range(self.rows):
            for c in range(self.cols):
                ax.plot(c, r, 'ko', markersize=12, markerfacecolor='white', markeredgecolor='black', markeredgewidth=2)
                ax.text(c+0.15, r+0.15, f'({r},{c})', fontsize=9, fontweight='bold')
        
        # Mark fire station location
        if self.fire_station is not None:
            fr, fc = self.id_to_coord(self.fire_station)
            ax.plot(fc, fr, 'ks', markersize=16, markerfacecolor='darkred', markeredgecolor='white', markeredgewidth=2)
            ax.text(fc-0.3, fr-0.3, 'FIRE\nSTATION', fontsize=8, fontweight='bold', color='white', ha='center', va='center')
        
        # Formatting
        ax.set_xlim(-0.5, self.cols - 0.5)
        ax.set_ylim(-0.5, self.rows - 0.5)
        ax.set_aspect('equal')
        ax.invert_yaxis()  # Make (0,0) at top-left
        ax.set_title('City Grid - Emergency Response Network (CONSTRUCTION SCENARIO)', fontsize=16, fontweight='bold')
        ax.set_xlabel('Column', fontsize=12)
        ax.set_ylabel('Row', fontsize=12)
        
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color='green', lw=8, label='Highway (normal)', alpha=0.9),
            Line2D([0], [0], color='orange', lw=6, label='Major Road (normal)', alpha=0.8),
            Line2D([0], [0], color='red', lw=6, label='Congested Area (normal)', alpha=0.8),
            Line2D([0], [0], color='purple', lw=8, label='CONSTRUCTION (+6 weight)', alpha=0.9),
            Line2D([0], [0], color='#FF4500', lw=6, label='Affected by Construction (+2 weight)', alpha=0.8),
            Line2D([0], [0], marker='s', color='darkred', lw=0, markersize=14, label='Fire Station', markerfacecolor='darkred', markeredgecolor='white'),
        ]
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1), fontsize=11)
        
        plt.tight_layout()
        plt.show()

    def write_graph_to_file(self, f):
        f.write("=" * 60)
        f.write("\n")
        f.write("CITY GRID EMERGENCY RESPONSE NETWORK\n")
        f.write("=" * 60)
        f.write("\n")
        f.write(f"Grid size: {self.rows} x {self.cols}\n")
        f.write(f"Total intersections: {self.rows * self.cols}\n")

        # Count connections and road types
        highway_count = normal_count = congested_count = 0
        total_connections = 0
        
        drawn_edges = set()
        for node_id in self.graph:
            for neighbor_id, weight in self.graph[node_id]:
                edge_key = (min(node_id, neighbor_id), max(node_id, neighbor_id))
                if edge_key not in drawn_edges:
                    drawn_edges.add(edge_key)
                    total_connections += 1
                    
                    if weight == self.HIGHWAY:
                        highway_count += 1
                    elif weight == self.NORMAL:
                        normal_count += 1
                    elif weight == self.CONGESTED:
                        congested_count += 1
        
        f.write(f"Total road segments: {total_connections}\n")
        f.write(f"    Highway segments: {highway_count}\n")
        f.write(f"    Normal road segments: {normal_count}\n")
        f.write(f"    Congested segments: {congested_count}\n")
        
        if self.fire_station is not None:
            fr, fc = self.id_to_coord(self.fire_station)
            f.write(f"Fire station location: ({fr}, {fc})\n")
        
        total_possible_connections = 0
        for r in range(self.rows):
            for c in range(self.cols):
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                for dr, dc in directions:
                    new_r, new_c = r + dr, c + dc
                    if 0 <= new_r < self.rows and 0 <= new_c < self.cols:
                        total_possible_connections += 1
        
            total_possible_connections //= 2
            blocked_connections = total_possible_connections - total_connections
            connectivity_percentage = (total_connections / total_possible_connections) * 100
        
        f.write(f"Blocked road segments: {blocked_connections}\n")
        f.write(f"Grid connectivity: {connectivity_percentage:.1f}%\n")
        f.write("=" * 60)
        f.write("\n")
        
    def print_graph_info(self):
        """Print information about the graph structure"""
        print("=" * 60)
        print("CITY GRID EMERGENCY RESPONSE NETWORK")
        print("=" * 60)
        print(f"Grid size: {self.rows} x {self.cols}")
        print(f"Total intersections: {self.rows * self.cols}")
        
        # Count connections and road types
        highway_count = normal_count = congested_count = 0
        total_connections = 0
        
        drawn_edges = set()
        for node_id in self.graph:
            for neighbor_id, weight in self.graph[node_id]:
                edge_key = (min(node_id, neighbor_id), max(node_id, neighbor_id))
                if edge_key not in drawn_edges:
                    drawn_edges.add(edge_key)
                    total_connections += 1
                    
                    if weight == self.HIGHWAY:
                        highway_count += 1
                    elif weight == self.NORMAL:
                        normal_count += 1
                    elif weight == self.CONGESTED:
                        congested_count += 1
        
        print(f"Total road segments: {total_connections}")
        print(f"  • Highway segments: {highway_count}")
        print(f"  • Normal road segments: {normal_count}")
        print(f"  • Congested segments: {congested_count}")
        
        if self.fire_station is not None:
            fr, fc = self.id_to_coord(self.fire_station)
            print(f"Fire station location: ({fr}, {fc})")
        
        total_possible_connections = 0
        for r in range(self.rows):
            for c in range(self.cols):
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                for dr, dc in directions:
                    new_r, new_c = r + dr, c + dc
                    if 0 <= new_r < self.rows and 0 <= new_c < self.cols:
                        total_possible_connections += 1
        
        total_possible_connections //= 2
        blocked_connections = total_possible_connections - total_connections
        connectivity_percentage = (total_connections / total_possible_connections) * 100
        
        print(f"Blocked road segments: {blocked_connections}")
        print(f"Grid connectivity: {connectivity_percentage:.1f}%")
        print("=" * 60)
        
        # Analyze route options from fire station
        if self.fire_station is not None:
            print("ROUTE ANALYSIS FROM FIRE STATION:")
            fr, fc = self.id_to_coord(self.fire_station)
            direct_connections = len(self.graph[self.fire_station])
            print(f"  • Direct connections from fire station: {direct_connections}")
            
            # Show available route types from fire station
            route_types = []
            for neighbor_id, weight in self.graph[self.fire_station]:
                if weight == self.HIGHWAY:
                    route_types.append("Highway")
                elif weight == self.NORMAL:
                    route_types.append("Normal")
                elif weight == self.CONGESTED:
                    route_types.append("Congested")
            
            print(f"  • Available route types: {', '.join(set(route_types))}")
            print("=" * 60)
