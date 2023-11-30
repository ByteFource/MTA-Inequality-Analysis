from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    # Define your project title
    project_title = "Is The Mta Racist?"
    # Pass the project title to the template
    train_lines = [
        "1 train (Broadway-7 Avenue local)",
        "2 train (7 Avenue express)",
        "3 train (7 Avenue express)",
        "4 train (Lexington Avenue express)",
        "5 train (Lexington Avenue express)",
        "6 train (Lexington Avenue local/Pelham express)",
        "7 train  (Flushing local and Flushing express)",
        "A train (8 Avenue express)",
        "B train (Central Park West local/6 Avenue express)",
        "C train (8 Avenue local)",
        "D train (6 Avenue express)",
        "E train (8 Avenue local)",
        "F train (6 Avenue local)",
        "G train (Brooklyn-Queens crosstown local)",
        "J train (Nassau Street express)",
        "L train (14 Street-Canarsie local)",
        "M train (Queens Boulevard local/6 Avenue local/Myrtle Avenue local)",
        "N train (Broadway express)",
        "Q train (2 Avenue/Broadway express)",
        "R train (Queens Boulevard/Broadway/4 Avenue local)",
       "S 42 St Shuttle, Franklin Av Shuttle, and Rockaway Park Shuttle trains (shuttle service)",
       "W train (Broadway local)",
        "Z train (Nassau Street express)"
    ]
    df = pd.read_csv('Median_Incomes.csv')
    
    # Filter by TimeFrame and get unique locations
    locations = df[df['TimeFrame'] == 2018]['Location'].unique().tolist()
   

    return render_template("index.html", title=project_title,locations=locations, train_lines=train_lines)
  

if __name__ == '__main__':
    app.run(debug=True)
