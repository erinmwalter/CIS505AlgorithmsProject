# Firestation Emergency Response Routing

### Overview
This project simulates a fire station's emergency response system, by finding the shortest routes through a city, where different routes have different weights (highway, normal road, congested downtown). 

There is a 5x5 grid for the city with the firestation located in (0, 0). There are also lines between grid spots to show the roads.
- Green = Highway, weight of 1
- Orange = Normal road, weight of 2
- Red = Congested road, weight of 4

### Graph of Road Layout
![City Grid Network](cityGraphic.png)


### Project Options:
1. Looking for an optimal route for the firetruck to take between the firestation to a given point..
2. Finding the response time for all points along the route, and looking for the best location for a second firestation and seeing how this would affect response time
3. A Whatif analysis of "whatif there is road construction along certain routes and this changes the weight, how would this affect response time of the firestation, are there alternate routes that become a better option to get to each point?"

### Algorithms that could work for each
- Dijkstra's algorithm could work for any of these and would probably be the simplest way to go.
- Backtracking could be used if we want to avoid specific areas and see what the best way to "avoid congestion" or "avoid construction" or avoid both. 