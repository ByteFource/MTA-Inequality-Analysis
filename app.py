from flask import Flask, render_template, request
import pandas as pd
import geopandas as gpd
import folium

app = Flask(__name__)

route_id_to_stops = pd.read_csv('data/route_id_to_stops.csv')
stops_delay_count = pd.read_csv('data/stops_delay_count.csv')
gdf_stops_delay_count = gpd.GeoDataFrame(stops_delay_count, geometry=gpd.points_from_xy(stops_delay_count['GTFS Longitude'], stops_delay_count['GTFS Latitude']), crs='EPSG:4326')
gdf_subway = gpd.read_file('data/my_subway_lines.geojson')


def make_map(line):
    center = [40.7128, -74.0060]
    zoom = 11
    base_map = 'CartoDB Voyager'
    m = folium.Map(location=center, zoom_start=zoom, control_scale=True, prefer_canvas=True, tiles=base_map)
    
    rt_id_to_stops = route_id_to_stops.set_index('route_id').T.to_dict('list')
    rt_id_to_stops = {k: v[0].split(', ') for k, v in rt_id_to_stops.items()}
    
    if line:
        stops = rt_id_to_stops[line]
        gdf_stops = gdf_stops_delay_count[gdf_stops_delay_count['stop_id'].isin(stops)]
    else:
        gdf_stops = gdf_stops_delay_count
    
    for _, row in gdf_stops.iterrows():
        folium.Marker(location=[row['GTFS Latitude'], row['GTFS Longitude']], popup=f"Stop: {row['Stop Name']}").add_to(m)
    
    
    # explain the colors of the subway lines
    legend_html = '''
         <div style="position: fixed; 
         bottom: 50px; left: 50px; width: 200px; height: 230px; 
         border:2px solid grey; z-index:9999; font-size:14px;
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
    m.get_root().html.add_child(folium.Element(legend_html))
    
    if line:
        gdf_line = gdf_subway[gdf_subway['name'].str.contains(line)]
    else:
        gdf_line = gdf_subway
    
    folium.GeoJson(data=gdf_line,
            style_function=lambda feature: {
                'color': feature['properties']['RGB Hex'],
                'weight': 2,
                'opacity': 1,
            },
            tooltip=folium.GeoJsonTooltip(fields=['Line/Branch'], aliases=['Subway Line'], sticky=True, opacity=0.9, direction='top')
            ).add_to(m)
    
    folium.LayerControl().add_to(m)
    
    return m

@app.route('/', methods=['GET', 'POST'])
def index():
    # Define your project title
    project_title = "Is The Mta Racist?"
    # Pass the project title to the template
    
    df = pd.read_csv('data/Median_Incomes.csv')
    
    # Filter by TimeFrame and get unique locations
    locations = df[df['TimeFrame'] == 2018]['Location'].unique().tolist()
    
    context = {
        'title': project_title,
        'locations': locations,
        'train_lines': get_train_lines()
    }
    
    if request.method == 'POST':
        line = get_train_lines()[request.form.get('train_line')]
        m = make_map(line)
        context['map'] = m.get_root().render()
        
    return render_template("index.html", **context)

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

if __name__ == '__main__':
    app.run(debug=True)
