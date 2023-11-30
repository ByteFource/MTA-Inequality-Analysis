from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # Define your project title
    project_title = "Is The Mta Racist?"
    # Pass the project title to the template
    return render_template('index.html', title=project_title)

if __name__ == '__main__':
    app.run(debug=True)
