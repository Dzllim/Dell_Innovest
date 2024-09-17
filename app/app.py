from flask import Flask, render_template, request, redirect, url_for, send_file
from datetime import datetime
import os

app = Flask(__name__)

# Route for the home page
@app.route('/')
def home():
    # Get today's date
    today = datetime.today().date()
    
    # Set the reference date can be change to the user day
    reference_date = datetime(2024, 9, 1).date()
    
    # Calculate the difference in days
    days_difference = (today - reference_date).days
    
    return render_template('index.html', my_days=days_difference)

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/instructions')
def instructions():
    return render_template('instructions.html')

@app.route('/dailyTasks')
def task():
    return render_template('dailyTasks.html')

@app.route('/leaderboard')
def leaderboard():
    # Example leaderboard data (this could come from a database)
    leaderboard_data = [
        {"rank": 1, "name": "Alice", "score": 1200, "img": "alice.jpg"},
        {"rank": 2, "name": "Bob", "score": 1100, "img": "bob.jpg"},
        {"rank": 3, "name": "Charlie", "score": 1050, "img": "charlie.jpg"},
        {"rank": 4, "name": "Diana", "score": 950, "img": "diana.jpg"},
        {"rank": 5, "name": "Edward", "score": 900, "img": "edward.jpg"}
    ]
    
    top_3 = leaderboard_data[:3]

    return render_template('leaderboard.html', leaderboard=leaderboard_data, top_3=top_3)

@app.route('/myRewards')
def myRewards():
    return render_template('myRewards.html')

# Route to handle form submission or other POST requests
@app.route('/submit', methods=['POST'])
def submit():
    data = request.form['data']
    # Process the data here
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(port=8080, host="0.0.0.0")
