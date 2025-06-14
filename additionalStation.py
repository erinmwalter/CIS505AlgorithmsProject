# scenario: the traffic from construction looks to lead to unacceptable response times from the fire department
# so, the city has surveyed and found two suitable locations for temporary stations (1,4) or (2,0). 
# so let's analyze times using the construction grid with a firestation in both of these locations, find out which
# of these options is more optimal at reducing the response times during construction.

from constructionGraphDrawing import CityGridConstruction
from graphDrawing import CityGrid
from dijkstraAnalysis import analyze_emergency_response, find_optimal_path, visualize_response_times
import numpy as np

def create_dual_station_heatmap(city_original, distances_original, distances_new, new_station_location):
    """
    Create a heatmap showing response times with both stations and which station responds
    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # Create grids for response times and station assignments
    response_grid = np.full((city_original.rows, city_original.cols), -1, dtype=float)
    station_assignment = np.full((city_original.rows, city_original.cols), '', dtype=object)
    
    # For each location, find which station responds faster
    for node_id in range(city_original.rows * city_original.cols):
        row, col = city_original.id_to_coord(node_id)
        
        time_from_original = distances_original.get(node_id, float('inf'))
        time_from_new = distances_new.get(node_id, float('inf'))
        
        # Find which station is faster
        if time_from_original <= time_from_new:
            best_time = time_from_original
            responding_station = "Original"
        else:
            best_time = time_from_new
            responding_station = "New"
        
        response_grid[row, col] = best_time if best_time != float('inf') else np.nan
        station_assignment[row, col] = responding_station
    
    # Create the heatmap
    heatmap_grid = response_grid.copy()
    im = ax.imshow(heatmap_grid, cmap='YlOrRd', interpolation='nearest')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Response Time (minutes)', rotation=270, labelpad=20)
    
    # Add text annotations with response time and which station responds
    for i in range(city_original.rows):
        for j in range(city_original.cols):
            value = response_grid[i, j]
            station = station_assignment[i, j]
            
            if not np.isnan(value):
                # Color text based on heatmap intensity
                text_color = 'white' if value > np.nanmean(heatmap_grid) else 'black'
                
                # Show response time
                ax.text(j, i-0.15, f'{value:.1f}', ha='center', va='center', 
                       color=text_color, fontsize=11, fontweight='bold')
                
                # Show which station responds (smaller text)
                station_text = "O" if station == "Original" else "N"
                station_color = 'blue' if station == "Original" else 'red'
                ax.text(j, i+0.2, station_text, ha='center', va='center',
                       color=station_color, fontsize=9, fontweight='bold')
    
    orig_row, orig_col = city_original.id_to_coord(city_original.fire_station)
    ax.plot(orig_col, orig_row, 's', markersize=20, markerfacecolor='blue', 
           markeredgecolor='white', markeredgewidth=2)
    ax.text(orig_col-0.3, orig_row-0.35, 'ORIG\nSTATION', ha='center', va='center',
           color='white', fontsize=7, fontweight='bold')
    
    # New station
    new_row, new_col = new_station_location
    ax.plot(new_col, new_row, 's', markersize=20, markerfacecolor='red', 
           markeredgecolor='white', markeredgewidth=2)
    ax.text(new_col-0.3, new_row-0.35, 'NEW\nSTATION', ha='center', va='center',
           color='white', fontsize=7, fontweight='bold')
    
    # Formatting
    ax.set_title(f'Dual Fire Station Response Times\nOriginal: (0,0), New: {new_station_location}\nO = Original responds, N = New responds', 
                fontsize=14, fontweight='bold')
    ax.set_xlabel('Column')
    ax.set_ylabel('Row')
    ax.set_xticks(range(city_original.cols))
    ax.set_yticks(range(city_original.rows))
    ax.grid(True, alpha=0.3)
    
    # Add legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='s', color='blue', lw=0, markersize=12, 
               label='Original Station (0,0)', markerfacecolor='blue', markeredgecolor='white'),
        Line2D([0], [0], marker='s', color='red', lw=0, markersize=12, 
               label=f'New Station {new_station_location}', markerfacecolor='red', markeredgecolor='white'),
        Line2D([0], [0], marker='o', color='blue', lw=0, markersize=8,
               label='O = Original responds', markerfacecolor='blue'),
        Line2D([0], [0], marker='o', color='red', lw=0, markersize=8,
               label='N = New responds', markerfacecolor='red')
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=10)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # original city grid with construction and firestation at (0,0)
    city_original = CityGridConstruction(5,5)
    city_original.set_fire_station(0, 0)

    # try out new locations
    city_location_a = CityGridConstruction(5,5)
    city_location_a.set_fire_station(1,4)

    city_location_b = CityGridConstruction(5,5)
    city_location_b.set_fire_station(2,0)

    results = []
    scenario_names = ["Original (0,0)", "Location A (1,4)", "Location B (2,0)"]

    firestation_array = [city_original, city_location_a, city_location_b]
    with open("fireStationAnalysis_multiplelocations.txt", "w") as f:
        for i, city in enumerate(firestation_array):
            scenario_name = scenario_names[i]
            fire_row, fire_col = city.id_to_coord(city.fire_station)

            f.write("FIRE STATION EMERGENCY RESPONSE ANALYSIS\n")
            f.write("=" * 70)
            f.write("\n")
    
            # prints graph of city
            city.print_graph_info()
            city.write_graph_to_file(f)
    
            # use dijkstra's algorithm to get the distances
            distances, previous, response_grid = analyze_emergency_response(city, f)

            # Calculate statistics for comparison
            reachable_distances = [d for d in distances.values() if d != float('inf')]
            if reachable_distances:
                avg_response = np.mean(reachable_distances)
                max_response = max(reachable_distances)
                min_response = min(reachable_distances)
                
                # Count response time categories
                quick = sum(1 for d in reachable_distances if d <= 3)
                medium = sum(1 for d in reachable_distances if 3 < d <= 6)
                slow = sum(1 for d in reachable_distances if d > 6)
                
                # Store results
                results.append({
                    'name': scenario_name,
                    'location': f"({fire_row},{fire_col})",
                    'avg_response': avg_response,
                    'max_response': max_response,
                    'min_response': min_response,
                    'quick_count': quick,
                    'medium_count': medium,
                    'slow_count': slow,
                    'distances': distances
                })

            f.write("\n" + "=" * 70 + "\n")
            f.write("OPTIMAL ROUTES\n")
            f.write("=" * 70)
    
            test_locations = [(row, col) for row in range(city.rows) for col in range(city.cols) 
                            if (row, col) != (fire_row, fire_col)]
    
            for target_row, target_col in test_locations:
                f.write(f"\nRoute to emergency at ({target_row}, {target_col}):")
                find_optimal_path(city, target_row, target_col, f)
    
            f.write("\n" + "=" * 70 + "\n")
    
            # Show the original city grid
            city.visualize_grid()
    
            # Show response time heatmap
            visualize_response_times(city, distances, response_grid)
        
        f.write("\n" + "="*80 + "\n")
        f.write("DUAL FIRE STATION COMPARISON ANALYSIS\n")
        f.write("="*80 + "\n")
        f.write("Comparing two dual-station scenarios:\n")
        f.write("Scenario A: Original (0,0) + Location A (1,4)\n") 
        f.write("Scenario B: Original (0,0) + Location B (2,0)\n")
        f.write("Each emergency handled by whichever station is closer\n")
        f.write("="*80 + "\n")
        
        # Get the distances we calculated for each station
        distances_original = results[0]['distances'] 
        distances_a = results[1]['distances']     
        distances_b = results[2]['distances']      
        
        # For each location, find best response time in each dual-station scenario
        scenario_a_times = []
        scenario_b_times = [] 
        
        f.write("\nRESPONSE TIME COMPARISON BY LOCATION:\n")
        f.write("-"*70 + "\n")
        f.write(f"{'Location':<10} {'Scenario A':<12} {'Scenario B':<12} {'Better':<10}\n")
        f.write(f"{''::<10} {'(0,0)+(1,4)':<12} {'(0,0)+(2,0)':<12} {'Option':<10}\n")
        f.write("-"*70 + "\n")
        
        for node_id in range(city_original.rows * city_original.cols):
            row, col = city_original.id_to_coord(node_id)
            
            # Scenario A: Best time between original (0,0) and location A (1,4)
            time_from_original = distances_original.get(node_id, float('inf'))
            time_from_a = distances_a.get(node_id, float('inf'))
            scenario_a_time = min(time_from_original, time_from_a)
            
            # Scenario B: Best time between original (0,0) and location B (2,0)  
            time_from_b = distances_b.get(node_id, float('inf'))
            scenario_b_time = min(time_from_original, time_from_b)
            
            # Determine which scenario is better for this location
            if scenario_a_time < scenario_b_time:
                better = "A"
            elif scenario_b_time < scenario_a_time:
                better = "B"
            else:
                better = "Tie"
            
            if scenario_a_time != float('inf'):
                scenario_a_times.append(scenario_a_time)
            if scenario_b_time != float('inf'):
                scenario_b_times.append(scenario_b_time)
            
            f.write(f"({row},{col})"
                   f"{scenario_a_time:>12.1f}"
                   f"{scenario_b_time:>12.1f}"
                   f"{better:>10}\n")
        
        # Calculate dual-station statistics
        avg_scenario_a = np.mean(scenario_a_times) if scenario_a_times else 0
        avg_scenario_b = np.mean(scenario_b_times) if scenario_b_times else 0
        max_scenario_a = max(scenario_a_times) if scenario_a_times else 0
        max_scenario_b = max(scenario_b_times) if scenario_b_times else 0
        
        # Count response categories for dual stations
        quick_a = sum(1 for t in scenario_a_times if t <= 3)
        medium_a = sum(1 for t in scenario_a_times if 3 < t <= 6)
        slow_a = sum(1 for t in scenario_a_times if t > 6)
        
        quick_b = sum(1 for t in scenario_b_times if t <= 3)
        medium_b = sum(1 for t in scenario_b_times if 3 < t <= 6)
        slow_b = sum(1 for t in scenario_b_times if t > 6)
        
        f.write("\nDUAL STATION SCENARIO COMPARISON:\n")
        f.write("-"*70 + "\n")
        f.write(f"{'Metric':<25} {'Scenario A':<15} {'Scenario B':<15}\n")
        f.write(f"{''::<25} {'(0,0)+(1,4)':<15} {'(0,0)+(2,0)':<15}\n")
        f.write("-"*70 + "\n")
        f.write(f"{'Average response time':<25} {avg_scenario_a:<15.2f} {avg_scenario_b:<15.2f}\n")
        f.write(f"{'Maximum response time':<25} {max_scenario_a:<15.1f} {max_scenario_b:<15.1f}\n")
        f.write(f"{'Quick responses (<=3 min)':<25} {quick_a:<15} {quick_b:<15}\n")
        f.write(f"{'Medium responses (3-6 min)':<25} {medium_a:<15} {medium_b:<15}\n")
        f.write(f"{'Slow responses (>6 min)':<25} {slow_a:<15} {slow_b:<15}\n")
        
        # Compare to original single station
        original_avg = results[0]['avg_response']
        
        f.write(f"\nIMPROVEMENT OVER SINGLE STATION:\n")
        f.write("-"*50 + "\n")
        f.write(f"Original single station avg: {original_avg:.2f} minutes\n")
        
        improvement_a = original_avg - avg_scenario_a
        improvement_b = original_avg - avg_scenario_b
        improvement_a_pct = (improvement_a / original_avg) * 100
        improvement_b_pct = (improvement_b / original_avg) * 100
        
        f.write(f"Scenario A improvement: {improvement_a:.2f} min ({improvement_a_pct:.1f}%)\n")
        f.write(f"Scenario B improvement: {improvement_b:.2f} min ({improvement_b_pct:.1f}%)\n")
        
        # Final recommendation
        f.write("\n" + "="*50 + "\n")
        f.write("FINAL RECOMMENDATION:\n")
        f.write("="*50 + "\n")
        
        if avg_scenario_a < avg_scenario_b:
            winner = "Add second station at (1,4)"
            winner_avg = avg_scenario_a
            winner_improvement = improvement_a
            winner_improvement_pct = improvement_a_pct
        elif avg_scenario_b < avg_scenario_a:
            winner = "Add second station at (2,0)"
            winner_avg = avg_scenario_b
            winner_improvement = improvement_b
            winner_improvement_pct = improvement_b_pct
        else:
            winner = "Both locations perform equally"
            winner_avg = avg_scenario_a
            winner_improvement = improvement_a
            winner_improvement_pct = improvement_a_pct
        
        f.write(f"RECOMMENDATION: {winner}\n")
        f.write(f"Expected average response time: {winner_avg:.2f} minutes\n")
        f.write(f"Improvement over single station: {winner_improvement:.2f} min ({winner_improvement_pct:.1f}%)\n")
        f.close()
    
    print("Creating dual station heatmap...")
    
    if avg_scenario_a < avg_scenario_b:
        # Scenario A wins: (0,0) + (1,4)
        print("Showing heatmap for winning scenario: Original (0,0) + New (1,4)")
        create_dual_station_heatmap(city_original, distances_original, distances_a, (1,4))
    elif avg_scenario_b < avg_scenario_a:
        # Scenario B wins: (0,0) + (2,0)
        print("Showing heatmap for winning scenario: Original (0,0) + New (2,0)")
        create_dual_station_heatmap(city_original, distances_original, distances_b, (2,0))
    else:
        # Tie - show both
        print("Tie! Showing both scenarios...")
        print("Scenario A: Original (0,0) + New (1,4)")
        create_dual_station_heatmap(city_original, distances_original, distances_a, (1,4))
        print("Scenario B: Original (0,0) + New (2,0)")
        create_dual_station_heatmap(city_original, distances_original, distances_b, (2,0))
    
        