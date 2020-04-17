import json
import openrouteservice as nav
import folium
import sys
import numpy

rnd = numpy.random

#input format: sys.argv[1] -> the routes json file 
#			   sys.argv[2] -> clients json file
#			   sys.argv[3] -> agents json file
#			sys.argv[4] -> outputfile name	

key = '5b3ce3597851110001cf62480bea960faed84e018b953afbd3510ae7'
client = nav.Client(key=key)
colors = ['red', 'blue', 'yellow', 'black']
output_file_name = sys.argv[4]

with open(sys.argv[1]) as fp:
	route_data = json.load(fp)

with open(sys.argv[2]) as fp:
	client_data = json.load(fp)

with open(sys.argv[3]) as fp:
	agent_data = json.load(fp)

routes = route_data['routes']
coords = client_data['coords']
demands = client_data['demands']
depot = coords[0]
#initializing Map
print(depot)
MAP = folium.Map(list(reversed(depot)), zoom_start = 30)
#marking depot
folium.map.Marker(list(reversed(depot)), icon=folium.Icon(color='blue',
                                        icon_color='#cc0000',
                                        icon='home',
                                        prefix='fa',
                                       )).add_to(MAP)

#marking all clients
for i in range(1, len(coords)):
	folium.map.Marker(location = list(reversed(coords[i])),
					  icon = folium.Icon(color='green'),
					  tooltip = 'Demand = {}'.format(demands[i-1])).add_to(MAP)

#plotting all routes in geoJsonformat!
for i in range(len(routes)):
	geojsonroute = nav.directions.directions(client = client,
										coordinates = routes[i],
										profile = 'driving-car',
										format_out = None,
										format = 'geojson',
										preference = 'shortest')
	print(geojsonroute)
	folium.GeoJson(geojsonroute, name='{}'.format(i), style_function = lambda x: {'color': colors[rnd.randint(1, len(colors) - 1)]}, tooltip = 'id {}, capacity {}'.format(agent_data['id'][i], agent_data['capacities'][i])).add_to(MAP)


MAP.save('{}.html'.format(output_file_name.split('.')[0]))

