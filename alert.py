# Tsunami Warning System By Mohammad Moradi All Rights Reserved
# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup as bsp
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import matplotlib.dates as md
import matplotlib.pyplot as plt
from dateutil import parser
from math import sqrt
import pandas as pd
import numpy as np
import matplotlib
import datetime
import smtplib
import urllib
import time
import pytz
import os

# Buoy station number
station = 23227
# Normal Water columns height at buoy position
Hmean = 3792.662
# Hieght that will add to mean height to raise alert if heigher levels detected
Iheight = 10
dataframe, df1, d15, d15s, time_serie, data = [], [], [], [], [], []
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
data_dir = BASE_DIR + "app/data/"
def get():
	print "Downloading Latest Data..."
	url = "http://www.ndbc.noaa.gov/station_page.php?station=%s" % station
	url = urllib.urlopen(url)
	html = bsp(url)
	raw_data = html.pre.contents
	# Writing extracted contents to disk
	f = open(os.path.join(data_dir, 'Data.dart'), 'wb', 2048)
	for i in raw_data:
		i = str(i)
		f.write(i)
	f.close()
#get()
def read():
	global dataframe, heights, data
	data = pd.read_table(os.path.join(data_dir, 'Data.dart'), delimiter=r'\s+', skiprows=(1), skipfooter=True, engine='python')
	Data = pd.read_table(os.path.join(data_dir, 'Data.dart'), delimiter=r'\s+', skiprows=(1), skipfooter=True, engine='python')
	heights = np.array(Data['m'])
	year = np.array(Data['#yr'])
	month = np.array(Data['mo'])
	day = np.array(Data['dy'])
	hour = np.array(Data['hr'])
	minute = np.array(Data['mn'])
	second = np.array(Data['s'])
	time = np.array([year, month, day, hour, minute, second])
	time = time.transpose()
	timedata = np.array(xrange(len(time)))
	timedata = timedata.tolist()
	#print "Adjusting Date and Time..."
	for i in xrange(len(time)):
	    s = '%d-%d-%d %d:%d:%d'%(time[i][0],time[i][1],time[i][2], time[i][3],time[i][4], time[i][5])
	    timedata[i] = s
	dt = np.array(xrange(len(timedata)))
	dt = dt.tolist()
	tlen = len(timedata)
	for i in xrange(tlen):
	    dt[i] = parser.parse(timedata[i])
	#print "Putting data to dataframe structure..."
	dataframe = pd.DataFrame({'Height':heights, 'time':dt})

def splitter(DF, YR, MO, DY, HR, MN, S, M, YRd, MOd, DYd, HRd, MNd, Sd, H, T):
	global df15
	for i in xrange(len(DF)):
		j = i + 1
		if j == len(DF):
			break
		if DF[i]-DF[j] == T:
			YRd.append(YR[i])
			MOd.append(MO[i])
			DYd.append(DY[i])
			HRd.append(HR[i])
			MNd.append(MN[i])
			Sd.append(S[i])
			H.append(M[i])
			if DF[j] == 0:
				YRd.append(YR[i])
				MOd.append(MO[i])
				DYd.append(DY[i])
				HRd.append(HR[i])
				MNd.append(MN[i])
				Sd.append(S[i])
				H.append(M[i])

def add_nan(DF, T):
	global df1
	start = DF.time[len(DF)-1]
	stop = DF.time[0]
	rng = pd.date_range(start, stop, freq=T)
	DF = DF.drop_duplicates('time').set_index('time').reindex(rng).ffill(limit=True)
	return DF

def make_dataframes(DF, label):
	heights = np.array(DF['m'])
	year = np.array(DF['#yr'])
	month = np.array(DF['mo'])
	day = np.array(DF['dy'])
	hour = np.array(DF['hr'])
	minute = np.array(DF['mn'])
	second = np.array(DF['s'])
	time = np.array([year, month, day, hour, minute, second])
	time = time.transpose()
	timedata = np.array(xrange(len(time)))
	timedata = timedata.tolist()
	#print "Adjusting Date and Time..."
	for i in xrange(len(time)):
		s = '%d-%d-%d %d:%d:%d'%(time[i][0],time[i][1],time[i][2], time[i][3],time[i][4], time[i][5])
		timedata[i] = s
	dt = np.array(xrange(len(timedata)))
	dt = dt.tolist()
	tlen = len(timedata)
	for i in xrange(tlen):
		dt[i] = parser.parse(timedata[i])
	#print "Putting data to dataframe structure..."
	DF = pd.DataFrame({label:heights, 'time':dt})
	return DF

def init_dataframes():
	global df15, df1, df15s
	YRd, MOd, DYd, HRd, MNd, Sd, H = [], [], [], [], [], [], []
	splitter(data.mn, data['#yr'], data.mo, data.dy, data.hr, data.mn, data.s, data.m, YRd, MOd, DYd, HRd, MNd, Sd, H, 15)
	df15 = pd.DataFrame({"#yr": YRd, "mo":MOd, "dy": DYd, "hr":HRd, "mn":MNd, "s":Sd, "m":H})

	YRd, MOd, DYd, HRd, MNd, Sd, H = [], [], [], [], [], [], []
	splitter(data.mn, data['#yr'], data.mo, data.dy, data.hr, data.mn, data.s, data.m, YRd, MOd, DYd, HRd, MNd, Sd, H, 1)
	df1 = pd.DataFrame({"#yr": YRd, "mo":MOd, "dy": DYd, "hr":HRd, "mn":MNd, "s":Sd, "m":H})

	YRd, MOd, DYd, HRd, MNd, Sd, H = [], [], [], [], [], [], []
	splitter(data.s, data['#yr'], data.mo, data.dy, data.hr, data.mn, data.s, data.m, YRd, MOd, DYd, HRd, MNd, Sd, H, 15)
	df15s = pd.DataFrame({"#yr": YRd, "mo":MOd, "dy": DYd, "hr":HRd, "mn":MNd, "s":Sd, "m":H})

def mode_detector():
	print "Checking buoy state mode..."
	init_dataframes()
	if len(df1) > 0:
		return True

def data_table():
	#Latest Height
	lastHeight = dataframe.Height[0]
	lasttime = pd.to_datetime(str(dataframe.time[np.where(dataframe.Height == lastHeight)[0][0]]))
	
	#Maximum Height
	maxheight = np.nanmax(dataframe.Height)
	maxtime = pd.to_datetime(str(dataframe.time[np.where(dataframe.Height == maxheight)[0][0]]))

	#Minimum Height
	minheight = np.nanmin(dataframe.Height)
	mintime = pd.to_datetime(str(dataframe.time[np.where(dataframe.Height == minheight)[0][0]]))

	#Mean Height
	meanheight = '%.3f' % np.nanmean(dataframe.Height)
	
	#Today
	os.environ['TZ'] = 'GMT'
	time.tzset()
	today = time.strftime('%Y-%m-%d %H:%M:%S')
	#date_time = datetime.datetime.today()
	#tl = list(date_time.timetuple())
	#today = "%d-%d-%d %d:%d:%d" % (tl[0],tl[1],tl[2],tl[3],tl[4],tl[5])
	
		
	dic ={"lastHeight":lastHeight , "lasttime":lasttime, "maxheight":maxheight, "maxtime":maxtime, "minheight":minheight,
	"mintime":mintime, "meanheight":meanheight, "today":today}
	D = pd.DataFrame(dic, index=[0])
	D.to_csv(os.path.join(BASE_DIR + "app/static/report/", "data_table.csv"))

def plot():
	print "Plotting Graph..."
	if len(df1) > 0:
		pass
		df1m = make_dataframes(df1, '1-min')
		df1m = add_nan(df1m, '1min')
	if len(df15):
		df15m = make_dataframes(df15, '15-min')
		df15m = add_nan(df15m, '15min')
	if len(df15s) > 0:
		df15S = make_dataframes(df15s, '15-sec')
		df15S = add_nan(df15S, '15S')	
	
	try:
		ax = df1m.plot(color='g', figsize=(9,4), x_compat=True)
		df15m.plot(ax=ax, color='b', x_compat=True)
		df15S.plot(ax=ax, style='.-r', x_compat=True)
	except NameError:
		ax = df15m.plot(color='b', figsize=(9,4), x_compat=True)
	ax.set_yticklabels(ax.get_yticks())
	ax.set_title('Water Column Height at Station %s' % station)
	ax.set_ylabel('meters')
	ax.set_xlabel('Event Mode')
	box = ax.get_position()
	ax.set_position([box.x0, box.y0 + box.height * 0.055, box.width, box.height * 0.9])
	ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5, borderaxespad=1.4,
	fontsize='large')
	ax.xaxis.set_major_formatter(md.DateFormatter('%m/%d'))
	plt.tight_layout()
	plt.savefig(os.path.join(BASE_DIR +'app/data', 'WCH.png'))
	plt.show()

def send_alert():
	print "Sending Alert..."
	receiver = 'prvmrd@gmail.com'
	msg = MIMEMultipart()
	msg['From'] = 'tswsystem@gmail.com'
	msg['To'] = 'prvmrd@gmail.com'
	msg['Subject'] = 'Tsunami Warning '
	message = """
	هشدار سونامی در ایستگاه %s
	
	ارتفاع ستون آب: %.2f m
	سرعت سونامی: %.2f km/h
	سونامی %d ساعت و %d دقیقه دیگر به چابهار خواهد رسید.
	""" % (station, latest_mean, speed, hour, minute)
	
	msg.attach(MIMEText(message))

	mailserver = smtplib.SMTP('smtp.gmail.com',587)
	# identify ourselves to smtp gmail client
	mailserver.ehlo()
	# secure email with tls encryption
	mailserver.starttls()
	# re-identify as an encrypted connection
	mailserver.ehlo()
	mailserver.login('tswsystem@gmail.com', 'tsunami@me')
	mailserver.sendmail('',receiver ,msg.as_string())
	mailserver.quit()
	print "Alert sent"

def alert():
	print "Checking Tsunami Event..."
	global latest_mean, speed, hour, minute
	
	#mean = np.nanmean(dataframe.Height)
	alert_mean = Hmean + Iheight
	latest_mean = np.nanmean(dataframe.Height[:10])
	speed = sqrt(latest_mean * 9.80665) * 3600/1000
	travel_time = 1500.564 / speed * 60
	hour, minute = divmod(travel_time, 60)
	hour, minute = int(hour), int(minute)
	if latest_mean >= alert_mean:
		send_alert()
		f = open(os.path.join(BASE_DIR + 'app/static/report/', 'report.cfg'), 'w')
		f.write('True')
		f.close()
		print 'True'
		return True
	else:
		f = open(os.path.join(BASE_DIR + 'app/static/report/', 'report.cfg'), 'w')
		f.write('False')
		f.close()
		print 'False'
		


def run():
	read()
	data_table()
	if mode_detector() == True:
		init_dataframes()
		alert()
		plot()
	else:
		plot()

#run()
