import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

class CityGrid:
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        self.graph = defaultdict(list)  # adjacency list
        self.fire_station = None
        
        # Road types and their weights
        self.HIGHWAY = 1      # Green lines
        self.NORMAL = 2       # Orange lines  
        self.CONGESTED = 4    # Red lines
        
        self.setup_grid_from_image()
        
    def coord_to_id(self, row, col):
        """Convert (row, col) coordinates to a single ID"""
        return row * self.cols + col
    
    def id_to_coord(self, node_id):
        """Convert node ID back to (row, col) coordinates"""
        return node_id // self.cols, node_id % self.cols
    
    def add_connection(self, r1, c1, r2, c2, weight):
        id1 = self.coord_to_id(r1, c1)
        id2 = self.coord_to_id(r2, c2)
        self.graph[id1].append((id2, weight))
        self.graph[id2].append((id1, weight))
    
    def setup_grid_from_image(self):   
        # HIGHWAY CONNECTIONS (Green lines)
        highway_connections = [
            ((0, 0), (0, 1)),
            ((0, 1), (0, 2)),
            ((0, 2), (1, 2)),
            ((1, 2), (2, 2)),
            ((2, 2), (3, 2)),
            ((3, 2), (4, 2))
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
            ((1, 1), (1, 2)),
            ((2, 0), (2, 1)),
            ((2, 1), (2, 2)),
            ((2, 2), (2, 3)),
            ((1, 3), (2, 3)),
            ((2, 3), (3, 3)),
            ((3, 3), (4, 3)),
            ((1, 0), (2, 0)),
            ((3, 0), (4, 0)),
            ((4, 2), (4, 3)),
            ((3, 2), (3, 3)),
            ((3, 3), (3, 4)),
        ]
        
        # Add all connections
        for (r1, c1), (r2, c2) in highway_connections:
            self.add_connection(r1, c1, r2, c2, self.HIGHWAY)
            
        for (r1, c1), (r2, c2) in normal_connections:
            self.add_connection(r1, c1, r2, c2, self.NORMAL)
            
        for (r1, c1), (r2, c2) in congested_connections:
            self.add_connection(r1, c1, r2, c2, self.CONGESTED)
    
    def set_fire_station(self, row, col):
        self.fire_station = self.coord_to_id(row, col)
        print(f"Fire station set at position ({row}, {col})")
    
    def visualize_grid(self):
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        
        # Create the grid background
        for i in range(self.rows + 1):
            ax.axhline(y=i-0.5, color='lightgray', linewidth=0.5)
        for i in range(self.cols + 1):
            ax.axvline(x=i-0.5, color='lightgray', linewidth=0.5)
        
        # Draw fire station area
        fire_square = plt.Rectangle((-0.5, -0.5), 1, 1, facecolor='red', alpha=0.7, edgecolor='darkred', linewidth=2)
        ax.add_patch(fire_square)
        
        # Draw roads with different colors based on weights
        drawn_edges = set()
        
        for node_id in self.graph:
            r, c = self.id_to_coord(node_id)
            
            for neighbor_id, weight in self.graph[node_id]:
                nr, nc = self.id_to_coord(neighbor_id)
                
                # Create a unique edge identifier (smaller id first)
                edge_key = (min(node_id, neighbor_id), max(node_id, neighbor_id))
                
                if edge_key not in drawn_edges:
                    drawn_edges.add(edge_key)
                    
                    # Choose color and style based on weight
                    if weight == self.HIGHWAY:
                        color = 'green'
                        linewidth = 8
                        alpha = 0.9
                    elif weight == self.NORMAL:
                        color = 'orange'
                        linewidth = 6
                        alpha = 0.8
                    elif weight == self.CONGESTED:
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
        ax.set_title('City Grid - Fire Station Emergency Response Network', fontsize=16, fontweight='bold')
        ax.set_xlabel('Column', fontsize=12)
        ax.set_ylabel('Row', fontsize=12)
        
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color='green', lw=8, label='Highway (weight: 1)', alpha=0.9),
            Line2D([0], [0], color='orange', lw=6, label='Major Road (weight: 2)', alpha=0.8),
            Line2D([0], [0], color='red', lw=6, label='Congested Area (weight: 4)', alpha=0.8),
            Line2D([0], [0], marker='s', color='darkred', lw=0, markersize=14, label='Fire Station', markerfacecolor='darkred', markeredgecolor='white'),
        ]
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1), fontsize=11)
        
        plt.tight_layout()
        plt.show()
    
    def print_graph_info(self):
        """Print information about the graph structure"""
        print("=" * 60)
        print("ENHANCED CITY GRID EMERGENCY RESPONSE NETWORK")
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

if __name__ == "__main__":
    # Create the city grid
    city = CityGrid(5, 5)
    
    # Set fire station at position (0, 0) as shown in the image
    city.set_fire_station(0, 0)
    
    # Print grid information
    city.print_graph_info()
    
    # Visualize the grid
    city.visualize_grid()