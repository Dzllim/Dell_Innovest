
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Route for the home page
@app.route('/')
def home():
    return render_template('/index.html')

@app.route('/scan')
def scan():
    return render_template('/scan.html')

@app.route('/dailyTasks')
def task():
    return render_template('/dailyTasks.html')

@app.route('/leaderboard')
def leaderboard():
    return render_template('/leaderboard.html')

@app.route('/myRewards')
def myRewards():
    return render_template('/myRewards.html')
# Route to handle form submission or other POST requests
@app.route('/submit', methods=['POST'])
def submit():
    data = request.form['data']
    # Process the data here
    return redirect(url_for('home'))

# Additional routes can be added here

if __name__ == '__main__':
    app.run(debug=True)
