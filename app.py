from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)



@app.route('/', methods=['GET', 'POST'])
def index():
    # Define your project title
    project_title = "Is The Mta Racist?"
    # Pass the project title to the template
    train_lines = {
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
    }
    df = pd.read_csv('data/Median_Incomes.csv')
    
    # Filter by TimeFrame and get unique locations
    locations = df[df['TimeFrame'] == 2018]['Location'].unique().tolist()
    
    # print the value once a line is selected from the dropdown
    if request.method == 'POST':
        print(train_lines[request.form.get('train_line')])

    return render_template("index.html", title=project_title,locations=locations, train_lines=train_lines)
  

if __name__ == '__main__':
    app.run(debug=True)
