from constructionGraphDrawing import CityGridConstruction
from graphDrawing import CityGrid
from dijkstraAnalysis import analyze_emergency_response, find_optimal_path, visualize_response_times, reconstruct_path

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
    