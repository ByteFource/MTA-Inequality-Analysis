from flask import Flask, render_template, request, jsonify
import pandas as pd
import geopandas as gpd
import folium

app = Flask(__name__)

route_id_to_stops = pd.read_csv('data/route_id_to_stops.csv')
stops_delay_count = pd.read_csv('data/stops_delay_count.csv')
gdf_stops_delay_count = gpd.GeoDataFrame(stops_delay_count, geometry=gpd.points_from_xy(stops_delay_count['GTFS Longitude'], stops_delay_count['GTFS Latitude']), crs='EPSG:4326')
gdf_subway = gpd.read_file('data/my_subway_lines.geojson')
gdf_avg_inc = gpd.read_file('data/average_income_2021.geojson')
total_delays_by_line = pd.read_csv('data/total_delay_time_by_lines.csv')
total_delays_by_stop = pd.read_csv('data/total_delay_time_by_stops.csv')
race = gpd.read_file('data/nyc-race.geojson')
on_time = pd.read_csv("data/avg_terminal_on_time_performance.csv")


def make_map(line, default_map):
    
    rt_id_to_stops = route_id_to_stops.set_index('route_id').T.to_dict('list')
    rt_id_to_stops = {k: v[0].split(', ') for k, v in rt_id_to_stops.items()}
    
    if line:
        zoom = 12
        center = gdf_stops_delay_count[gdf_stops_delay_count['stop_id'].isin(rt_id_to_stops[line])][['GTFS Latitude', 'GTFS Longitude']].mean().tolist()
    else:
        center = [40.7128, -74.0060]
        zoom = 11
    
    base_map = 'CartoDB Voyager'
    m = folium.Map(location=center, zoom_start=zoom, control_scale=True, prefer_canvas=True, tiles=base_map)
    
    income_choropleth = folium.Choropleth(
        geo_data=gdf_avg_inc,
        name='Income by Zip Code',
        data=gdf_avg_inc,
        columns=['ZipCode', 'B19013001'],
        key_on='feature.properties.ZipCode',
        fill_color='YlGnBu',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Average Income',
        highlight=True,
        smooth_factor=0
    )
    
    income_tooltip = folium.GeoJsonTooltip(
        fields=['ZipCode', 'B19013001', 'Neighborhood', 'Borough'], 
        aliases=['Zip Code:', 'Average Income:', 'Neighborhood:', 'Borough:'],
        sticky=True, 
        opacity=0.9, 
        direction='top',
        style="font-size: 12px; max-width: 300px;",
    )
    
    income_choropleth.geojson.add_child(income_tooltip)
    
    race_choropleth = folium.Choropleth(
        geo_data=race,
        name='NYC Race Map',
        data=race,
        columns=['name', 'Total Population'],
        key_on='feature.properties.name',
        fill_color='YlOrBr',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Total Population',
        highlight=True,
        smooth_factor=1.0
    )

    fields = ['Total Population', 'White alone', 'Black or African American Alone', 'American Indian and Alaska Native alone', 'Asian alone', 'Native Hawaiian and Other Pacific Islander Alone', 'Some other race alone', 'Two or more races','Hispanic or Latino (Total)']
    aliases = [field + ':' for field in fields]
    race_tooltip = folium.GeoJsonTooltip(
        fields=['name', *fields],
        aliases=['Zip Code:', *aliases],
        sticky=True, 
        opacity=0.9, 
        direction='top',
        style="font-size: 12px; width: 100 vw;",
    )

    if default_map == "income":
        m.add_child(income_choropleth)
    else:
        m.add_child(race_choropleth)

    race_choropleth.geojson.add_child(race_tooltip)
        
    if line:
        gdf_line = gdf_subway[gdf_subway['name'].str.contains(line)]
    else:
        gdf_line = gdf_subway
    
    folium.GeoJson(data=gdf_line,
                   name='Subway Lines',
                   style_function=lambda feature: {
                       'color': feature['properties']['RGB Hex'],
                       'weight': 7,
                       'opacity': 1,
                    },
                   tooltip=folium.GeoJsonTooltip(
                       fields=['Line/Branch'], 
                       aliases=['Subway Line:'], 
                       sticky=True, 
                       opacity=0.9, 
                       direction='top',
                       style="font-size: 12px;",
                       labels=True
                    )
    ).add_to(m)
       
    if line:
        stops = rt_id_to_stops[line]
        gdf_stops = gdf_stops_delay_count[gdf_stops_delay_count['stop_id'].isin(stops)]
    else:
        gdf_stops = gdf_stops_delay_count
        
    markers = folium.FeatureGroup(name='Stops')
    m.add_child(markers)
    marker_tooltip = 'Click for more info.'
    
    for _, row in gdf_stops.iterrows():
        delay = row['Average Delay per Line']
        
        if delay <= 0:
            color = 'blue'
        elif delay <= 60:
            color = 'green'
        else:
            color = 'red'
        
        # remove '[' and ']' from the list of branches
        branch = row['branch'].replace('[', '').replace(']', '')
        
        pop_up = f"""<p style='font-size: 16px'><b>Stop</b>: {row['Stop Name']}</p>
                    <p style='font-size: 14px'><b>Borough</b>: {row['Borough']}</p>
                    <p style='font-size: 14px'><b>Train Lines</b>: {branch}</p>
                    <p style='font-size: 14px'><b>Average Delay per Line</b>: {row['Average Delay per Line (mins)']}</p>
                    <p style='font-size: 14px'><b>Delays</b>: {row['Delay Count']}</p>
                """
        
        marker = folium.Marker(
                    location=[row['GTFS Latitude'], row['GTFS Longitude']], 
                    popup=folium.Popup(pop_up, max_width=300),
                    icon=folium.Icon(color=color, icon='info-sign'),
                    tooltip=marker_tooltip
                ).add_to(m)
        marker.add_to(markers)
    
    # explain the colors of the subway lines
    legend_html = '''
         <div style="position: fixed; 
         bottom: 50px; left: 50px; width: 200px; height: 230px; z-index:9999; font-size:14px;
         ">&nbsp; Subway Lines <br>
         &nbsp; 1 2 3 &nbsp; <i class="fa fa-circle" style="color:#EE352E"></i><br>
         &nbsp; 4 5 6 &nbsp; <i class="fa fa-circle" style="color:#00933C"></i><br>
         &nbsp; 7 &nbsp; <i class="fa fa-circle" style="color:#B933AD"></i><br>
         &nbsp; A/C/E &nbsp; <i class="fa fa-circle" style="color:#0039A6"></i><br>
         &nbsp; B/D/F/M &nbsp; <i class="fa fa-circle" style="color:#FF6319"></i><br>
         &nbsp; G &nbsp; <i class="fa fa-circle" style="color:#6CBE45"></i><br>
         &nbsp; J/Z &nbsp; <i class="fa fa-circle" style="color:#996633"></i><br>
         &nbsp; L &nbsp; <i class="fa fa-circle" style="color:#A7A9AC"></i><br>
         &nbsp; N/Q/R &nbsp; <i class="fa fa-circle" style="color:#FCCC0A"></i><br>
         &nbsp; S &nbsp; <i class="fa fa-circle" style="color:#808183"></i><br>
            </div>
            '''
    
    mp = m.get_name()
    mrk = markers.get_name()

    js_callback = f'''
    function show_hide_markers() {{

        var map = {mp};
        var markers = {mrk};
        
        function show_markers() {{
            var zoomlevel = map.getZoom();
            if (zoomlevel < 13) {{
                markers.removeFrom(map);
            }} else {{
                markers.addTo(map);
            }}
        }}

        map.on('zoomend', show_markers);
        show_markers();
    }}

    window.onload = show_hide_markers;
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    m.get_root().script.add_child(folium.Element(js_callback))
    
    folium.LayerControl().add_to(m)
    return m

@app.route('/', methods=['GET', 'POST'])
def index():
    # Define your project title
    project_title = "Is The Mta Racist?"
    # Pass the project title to the template
    
    
    if request.method == 'POST':
        selected_line = request.form.get('train_line')
        default = request.form.get('map_type')
        print(default)
    else:
        selected_line = 'default'
        default = 'race'
    
    context = {
        'title': project_title,
        'default_map': default,
        'train_lines': get_train_lines(),
        'selected_train_line': selected_line
    }
    
    line = get_train_lines().get(selected_line)
    
    m = make_map(line, default_map=default)
    context['map'] = m.get_root().render()

    return render_template("index.html", **context)

@app.route('/delay_list')
def get_delay_list():
    delay_lines = total_delays_by_line.set_index('Line')['Total Delay Time'].to_dict()
    return jsonify(delay_lines)

@app.route('/performance_list')
def get_performance_list():
    performance_lines = on_time.set_index('Line')['Average Terminal On-Time Performance'].to_dict()
    return jsonify(performance_lines)


def get_train_lines():
    return {
        "1 train (Broadway-7 Avenue local)" : "1",
        "2 train (7 Avenue express)" : "2",
        "3 train (7 Avenue express)" : "3",
        "4 train (Lexington Avenue express)" : "4",
        "5 train (Lexington Avenue express)" : "5",
        "6 train (Lexington Avenue local/Pelham express)" : "6",
        "7 train  (Flushing local and Flushing express)" : "7",
        "A train (8 Avenue express)" : "A",
        "B train (Central Park West local/6 Avenue express)" : "B",
        "C train (8 Avenue local)" : "C",
        "D train (6 Avenue express)" : "D",
        "E train (8 Avenue local)" : "E",
        "F train (6 Avenue local)" : "F",
        "G train (Brooklyn-Queens crosstown local)" : "G",
        "J train (Nassau Street express)" : "J",
        "L train (14 Street-Canarsie local)" : "L",
        "M train (Queens Boulevard local/6 Avenue local/Myrtle Avenue local)" : "M",
        "N train (Broadway express)" : "N",
        "Q train (2 Avenue/Broadway express)" : "Q",
        "R train (Queens Boulevard/Broadway/4 Avenue local)" : "R",
       "S 42 St Shuttle, Franklin Av Shuttle, and Rockaway Park Shuttle trains (shuttle service)" : "S",
       "W train (Broadway local)" : "W",
        "Z train (Nassau Street express) " : "Z",
        "default": None
    }

@app.route('/about')
def about():
    return render_template('about-us.html')

if __name__ == '__main__':
    app.run(debug=True)
