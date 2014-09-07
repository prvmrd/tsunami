from flask import render_template, send_file, Flask, url_for
import pandas as pd
import os
app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(__file__)) 
@app.route('/')
@app.route('/index')
def index():
	data = pd.read_csv(os.path.join(BASE_DIR + '/app/static/report/', 'data_table.csv'))
	report = open(os.path.join(BASE_DIR + '/app/static/report/', 'report.cfg'))
	if report.read() == "True":
		alert = True
	else:
		alert = False
	print alert
	return render_template('index.html',
	alert = alert,
	minheight = data.minheight[0],
	mintime = data.mintime[0],
	maxheight = data.maxheight[0],
	maxtime = data.maxtime[0],
	meanheight = data.meanheight[0],
	lastHeight = data.lastHeight[0],
	lasttime = data.lasttime[0],
	today = data.today[0]	
	)
@app.route('/about')
def about():
	return render_template('about.html')
@app.route('/contact')
def contact():
	return render_template('contact.html')
@app.route('/plot')
def plot():
	img = os.path.join(BASE_DIR + '/app/data/WCH.png')
	return send_file(img, mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)
