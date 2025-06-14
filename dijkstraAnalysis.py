import heapq
from collections import defaultdict
from graphDrawing import CityGrid
from constructionGraphDrawing import CityGridConstruction
import matplotlib.pyplot as plt
import numpy as np

def dijkstra_all_distances(graph, start_node):
    # Initialize distances and previous nodes
    distances = defaultdict(lambda: float('inf'))
    previous = {}
    distances[start_node] = 0
    
    # Priority queue: (distance, node)
    pq = [(0, start_node)]
    visited = set()
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        # Skip if we've already processed this node
        if current_node in visited:
            continue
            
        visited.add(current_node)
        
        # Check all neighbors
        for neighbor, weight in graph[current_node]:
            if neighbor in visited:
                continue
                
            # Calculate new distance through current node
            new_distance = current_distance + weight
            
            # If we found a shorter path, update it
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (new_distance, neighbor))
    
    return dict(distances), previous

def reconstruct_path(previous, start_node, end_node):
    if end_node not in previous and end_node != start_node:
        return None  # No path exists
    
    path = []
    current = end_node
    
    while current is not None:
        path.append(current)
        current = previous.get(current)
        if current == start_node:
            path.append(start_node)
            break
    
    return path[::-1]  # Reverse to get start->end order

def analyze_emergency_response(city_grid, f):
    if city_grid.fire_station is None:
        f.write("Error: No fire station set!\n")
        return
    
    # Calculate all shortest distances from fire station
    distances, previous = dijkstra_all_distances(city_grid.graph, city_grid.fire_station)
    
    f.write("=" * 70)
    f.write("\n")
    f.write("EMERGENCY RESPONSE TIME ANALYSIS\n")
    f.write("=" * 70)
    f.write("\n")
    
    fire_row, fire_col = city_grid.id_to_coord(city_grid.fire_station)
    f.write(f"Fire Station Location: ({fire_row}, {fire_col})\n")
    
    # Create a grid to display response times
    response_grid = np.full((city_grid.rows, city_grid.cols), -1, dtype=float)
    
    f.write("Shortest Response Times to Each Location:\n")
    f.write("Position     Distance     Response Time\n")
    f.write("-" * 50)
    f.write("\n")
    
    for node_id in range(city_grid.rows * city_grid.cols):
        row, col = city_grid.id_to_coord(node_id)
        distance = distances.get(node_id, float('inf'))
        response_grid[row, col] = distance
        
        if distance == float('inf'):
            f.write(f"({row}, {col})     Unreachable  ∞\n")
        else:
            # Convert distance to time (using weight 1 = 1 min and so on)
            response_time = distance
            f.write(f"({row}, {col})          {distance:.1f}          {response_time:.1f} min\n")
    
    reachable_distances = [d for d in distances.values() if d != float('inf')]
    
    if reachable_distances:
        avg_response = np.mean(reachable_distances)
        max_response = max(reachable_distances)
        min_response = min(reachable_distances)
        
        f.write("\nRESPONSE TIME STATISTICS:\n")
        f.write(f"    Average response time: {avg_response:.2f} minutes\n")
        f.write(f"    Maximum response time: {max_response:.1f} minutes\n")
        f.write(f"    Minimum response time: {min_response:.1f} minutes\n")
        
        # Find locations with longest response times
        max_time_locations = []
        for node_id, distance in distances.items():
            if distance == max_response:
                row, col = city_grid.id_to_coord(node_id)
                max_time_locations.append(f"({row}, {col})")
        
        f.write(f"    Locations with longest response time: {', '.join(max_time_locations)}\n")
        
        # Count locations by response time categories
        quick_response = sum(1 for d in reachable_distances if d <= 3)
        medium_response = sum(1 for d in reachable_distances if 3 < d <= 6)
        slow_response = sum(1 for d in reachable_distances if d > 6)
        
        f.write(f"    Quick response (< 3 min): {quick_response} locations\n")
        f.write(f"    Medium response (3-6 min): {medium_response} locations\n")
        f.write(f"    Slow response (> 6 min): {slow_response} locations\n")
    
    unreachable_count = sum(1 for d in distances.values() if d == float('inf'))
    if unreachable_count > 0:
        f.write(f"    Unreachable locations: {unreachable_count}\n")
    
    f.write("=" * 70)
    f.write("\n")
    
    return distances, previous, response_grid

def visualize_response_times(city_grid, distances, response_grid):
    """
    Create a heatmap visualization of emergency response times.
    """
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    # Create response time heatmap
    # if NaN for any, just make it "infinity" for simplicity
    heatmap_grid = response_grid.copy()
    heatmap_grid[heatmap_grid == float('inf')] = np.nan
    
    im = ax.imshow(heatmap_grid, cmap='YlOrRd', interpolation='nearest')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Response Time (minutes)', rotation=270, labelpad=20)
    
    # Add text annotations
    for i in range(city_grid.rows):
        for j in range(city_grid.cols):
            value = response_grid[i, j]
            if value == float('inf'):
                text = '∞'
                color = 'white'
            else:
                text = f'{value:.1f}'
                color = 'white' if value > np.nanmean(heatmap_grid) else 'black'
            
            ax.text(j, i, text, ha='center', va='center', 
                    color=color, fontsize=12, fontweight='bold')
    
    # Mark fire station
    fire_row, fire_col = city_grid.id_to_coord(city_grid.fire_station)
    ax.plot(fire_col, fire_row, 'bs', markersize=25, markerfacecolor='red', 
             markeredgecolor='white', markeredgewidth=2)
    ax.text(fire_col, fire_row-0.3, 'FIRE\nSTATION', ha='center', va='center',
             color='black', fontsize=8, fontweight='bold')
    
    ax.set_title('Emergency Response Time Heatmap', fontsize=14, fontweight='bold')
    ax.set_xlabel('Column')
    ax.set_ylabel('Row')
    ax.set_xticks(range(city_grid.cols))
    ax.set_yticks(range(city_grid.rows))
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def find_optimal_path(city_grid, target_row, target_col, f):
    if city_grid.fire_station is None:
        f.write("Error: No fire station set!\n")
        return
    
    target_id = city_grid.coord_to_id(target_row, target_col)
    distances, previous = dijkstra_all_distances(city_grid.graph, city_grid.fire_station)
    
    path = reconstruct_path(previous, city_grid.fire_station, target_id)
    
    if path is None:
        f.write(f"No path found from fire station to ({target_row}, {target_col})\n")
        return
    
    f.write(f"\n   Optimal path from fire station to ({target_row}, {target_col}):")
    f.write("\n   Path: ")
    
    total_time = 0
    for i, node_id in enumerate(path):
        row, col = city_grid.id_to_coord(node_id)
        f.write(f"({row},{col}) ")
        
        if i < len(path) - 1:
            # Find the edge weight between consecutive nodes
            next_node = path[i + 1]
            for neighbor, weight in city_grid.graph[node_id]:
                if neighbor == next_node:
                    total_time += weight
                    break
            f.write(" -> ")
    
    f.write(f"\n   Total response time: {total_time} minutes\n")
    return path

if __name__ == "__main__":
    with open("fireStationAnalysis.txt", "w") as f:
        f.write("FIRE STATION EMERGENCY RESPONSE ANALYSIS\n")
        f.write("=" * 70)
        f.write("\n")
    
        # Create the city grid
        city = CityGrid(5, 5)
    
        # Set fire station at position (0, 0)
        city.set_fire_station(0, 0)
        f.write(f"Fire station set at position (0, 0)\n")
    
        # prints graph of city
        city.print_graph_info()
        city.write_graph_to_file(f)
    
        # use dijkstra's algorithm to get the distances
        distances, previous, response_grid = analyze_emergency_response(city, f)
    
        f.write("\n" + "=" * 70 + "\n")
        f.write("OPTIMAL ROUTES\n")
        f.write("=" * 70)
    
        test_locations = [(row, col) for row in range(city.rows) for col in range(city.cols) if (row, col) != (0, 0)]
    
        for target_row, target_col in test_locations:
            f.write(f"\nRoute to emergency at ({target_row}, {target_col}):")
            find_optimal_path(city, target_row, target_col, f)
    
        f.write("\n" + "=" * 70 + "\n")
    
        # Show the original city grid
        city.visualize_grid()
    
        # Show response time heatmap
        visualize_response_times(city, distances, response_grid)
        f.close()

    # redoing the scenario with construction on the highway
    with open("constructionFirestationAnalysis.txt", "w") as f:
        f.write("FIRE STATION EMERGENCY RESPONSE ANALYSIS (WITH CONSTRUCTION)\n")
        f.write("=" * 70)
        f.write("\n")
    
        # Create the city grid
        constructionCity = CityGridConstruction(5, 5)
    
        # Set fire station at position (0, 0)
        constructionCity.set_fire_station(0, 0)
        f.write(f"Fire station set at position (0, 0)\n")
    
        # prints graph of city
        constructionCity.print_graph_info()
        constructionCity.write_graph_to_file(f)
    
        # use dijkstra's algorithm to get the distances
        constructionDistances, constructionPrevious, construction_response_grid = analyze_emergency_response(constructionCity, f)
    
        f.write("\n" + "=" * 70 + "\n")
        f.write("OPTIMAL ROUTES\n")
        f.write("=" * 70)
    
        test_locations = [(row, col) for row in range(constructionCity.rows) for col in range(constructionCity.cols) if (row, col) != (0, 0)]
    
        for target_row, target_col in test_locations:
            f.write(f"\nRoute to emergency at ({target_row}, {target_col}):")
            find_optimal_path(constructionCity, target_row, target_col, f)
    
        f.write("\n" + "=" * 70 + "\n")
    
        # Show the original city grid
        constructionCity.visualize_grid()
    
        # Show response time heatmap
        visualize_response_times(constructionCity, constructionDistances, construction_response_grid)
        f.close()

    with open("comparisonAnalysis.txt", "w") as f:
        f.write("CONSTRUCTION IMPACT COMPARISON\n")
        f.write("=" * 70 + "\n")
        f.write("Fire Station at (0,0) - Normal vs Construction Scenario\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("RESPONSE TIME COMPARISON BY LOCATION:\n")
        f.write("-" * 70 + "\n")
        f.write(f"{'Location':<10} {'Normal':<8} {'Construction':<12} {'Increase':<9} {'% Increase':<10}\n")
        f.write("-" * 70 + "\n")
        
        total_normal = 0
        total_construction = 0
        count = 0
        
        for node_id in range(city.rows * city.cols):
            row, col = city.id_to_coord(node_id)
            
            # Skip the fire station location (distance = 0)
            if node_id == city.fire_station:
                continue
            
            normal_time = distances.get(node_id, float('inf'))
            construction_time = constructionDistances.get(node_id, float('inf'))
            
            if normal_time != float('inf') and construction_time != float('inf') and normal_time > 0:
                increase = construction_time - normal_time
                percent_increase = (increase / normal_time) * 100
                
                total_normal += normal_time
                total_construction += construction_time
                count += 1
                
                f.write(f"({row},{col})"
                       f"{normal_time:>10.1f}"
                       f"{construction_time:>12.1f}"
                       f"{increase:>9.1f}"
                       f"{percent_increase:>9.1f}%\n")
        
        # Calculate overall statistics
        avg_normal = total_normal / count
        avg_construction = total_construction / count
        overall_increase = avg_construction - avg_normal
        overall_percent = (overall_increase / avg_normal) * 100
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("OVERALL IMPACT SUMMARY:\n")
        f.write("=" * 70 + "\n")
        f.write(f"Average response time (normal):       {avg_normal:.2f} minutes\n")
        f.write(f"Average response time (construction):  {avg_construction:.2f} minutes\n")
        f.write(f"Average increase:                     {overall_increase:.2f} minutes\n") 
        f.write(f"Overall percentage increase:          {overall_percent:.1f}%\n")
        
        # Find most affected location
        max_increase = 0
        max_location = ""
        max_percent = 0
        
        for node_id in range(city.rows * city.cols):
            row, col = city.id_to_coord(node_id)
            normal_time = distances.get(node_id, float('inf'))
            construction_time = constructionDistances.get(node_id, float('inf'))
            
            if normal_time != float('inf') and construction_time != float('inf') and normal_time != 0:
                increase = construction_time - normal_time
                percent_increase = (increase / normal_time) * 100
                
                if percent_increase > max_percent:
                    max_percent = percent_increase
                    max_increase = increase
                    max_location = f"({row},{col})"
        
        f.write(f"\nMost affected location: {max_location}\n")
        f.write(f"  - Increase: +{max_increase:.1f} minutes (+{max_percent:.1f}%)\n")
        
        # ROUTE CHANGE ANALYSIS
        f.write("\n" + "=" * 70 + "\n")
        f.write("ROUTE CHANGE ANALYSIS:\n")
        f.write("=" * 70 + "\n")
        
        routes_changed = 0
        routes_same = 0
        routes_avoiding_construction = 0
        
        f.write("Locations with route changes:\n")
        f.write("-" * 50 + "\n")
        
        for node_id in range(city.rows * city.cols):
            if node_id == city.fire_station:  # Skip fire station itself
                continue
                
            row, col = city.id_to_coord(node_id)
            
            # Get paths for both scenarios
            normal_path = reconstruct_path(previous, city.fire_station, node_id)
            construction_path = reconstruct_path(constructionPrevious, constructionCity.fire_station, node_id)
            
            if normal_path and construction_path:
                normal_coords = [city.id_to_coord(node) for node in normal_path]
                construction_coords = [constructionCity.id_to_coord(node) for node in construction_path]
                
                # Check if paths are different
                if normal_coords != construction_coords:
                    routes_changed += 1
                    
                    # Check if the new route avoids construction zones
                    construction_zones = [((1,2), (2,2)), ((2,2), (3,2))]
                    avoids_construction = True
                    
                    # Check each segment in construction path
                    for i in range(len(construction_coords) - 1):
                        segment = (construction_coords[i], construction_coords[i+1])
                        reverse_segment = (construction_coords[i+1], construction_coords[i])
                        
                        if segment in construction_zones or reverse_segment in construction_zones:
                            avoids_construction = False
                            break
                    
                    if avoids_construction:
                        routes_avoiding_construction += 1
                    
                    f.write(f"({row},{col}): Route changed\n")
                    f.write(f"  Normal:       {' -> '.join([f'({r},{c})' for r,c in normal_coords])}\n")
                    f.write(f"  Construction: {' -> '.join([f'({r},{c})' for r,c in construction_coords])}\n")
                    if avoids_construction:
                        f.write(f"  * Avoids construction zones\n")
                    f.write("\n")
                else:
                    routes_same += 1
        
        f.write("\n" + "-" * 50 + "\n")
        f.write("ROUTE CHANGE SUMMARY:\n")
        f.write("-" * 50 + "\n")
        f.write(f"Total destinations analyzed:           {routes_changed + routes_same}\n")
        f.write(f"Routes that changed:                   {routes_changed}\n")
        f.write(f"Routes that stayed the same:           {routes_same}\n")
        f.write(f"Routes now avoiding construction:      {routes_avoiding_construction}\n")
        f.write(f"Percentage of routes changed:          {(routes_changed/(routes_changed + routes_same))*100:.1f}%\n")
        
        # Identify which routes still go through construction
        f.write("\nRoutes still using construction zones:\n")
        routes_through_construction = 0
        
        for node_id in range(constructionCity.rows * constructionCity.cols):
            if node_id == constructionCity.fire_station:
                continue
                
            row, col = constructionCity.id_to_coord(node_id)
            construction_path = reconstruct_path(constructionPrevious, constructionCity.fire_station, node_id)
            
            if construction_path:
                construction_coords = [constructionCity.id_to_coord(node) for node in construction_path]
                construction_zones = [((1,2), (2,2)), ((2,2), (3,2))]
                
                uses_construction = False
                for i in range(len(construction_coords) - 1):
                    segment = (construction_coords[i], construction_coords[i+1])
                    reverse_segment = (construction_coords[i+1], construction_coords[i])
                    
                    if segment in construction_zones or reverse_segment in construction_zones:
                        uses_construction = True
                        break
                
                if uses_construction:
                    routes_through_construction += 1
                    f.write(f"  ({row},{col}): Still uses construction zone\n")
        
        f.write(f"\nRoutes still using construction zones: {routes_through_construction}\n")
    