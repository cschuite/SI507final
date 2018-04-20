import secrets
import requests
import sqlite3 as sqlite
import json
import numpy as np
import plotly.plotly as py
from plotly.graph_objs import *
import plotly.graph_objs as go
import webbrowser
import codecs
import sys
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

#global variables
YELP_API_KEY = secrets.YELP_KEY 
ZOMATO_API_KEY = secrets.ZOMATO_KEY 
MAPBOX_KEY = secrets.MAPBOX_KEY
CACHE_FNAME = 'cache.json'
DBNAME = "restaurants.db"
RESTAURANT_DICT = {}

#class definitions
class Restaurant:
	def __init__(self, name, street_address, city, state, zip_code):
		self.name = name
		self.address = "{} {} {} {}".format(street_address, city, state, zip_code)

#getting data from APIS
#cache code comes from lecture notes
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)


def make_request_using_cache(request_baseurl, request_params, request_headers):
    unique_ident = params_unique_combination(request_baseurl, request_params)
    if unique_ident in CACHE_DICTION:
        return CACHE_DICTION[unique_ident]
    else:
        resp = requests.get(url=request_baseurl, params=request_params, headers=request_headers)
        CACHE_DICTION[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

#create the database
def create_restaurant_db():
	conn = sqlite.connect(DBNAME)
	cur = conn.cursor()

	statement = '''
		DROP TABLE IF EXISTS 'Restaurants_Basic'
	'''
	cur.execute(statement)
	conn.commit()

	statement = '''
		DROP TABLE IF EXISTS 'Restaurants_Detailed'
	'''
	cur.execute(statement)
	conn.commit()

	statement = '''
		CREATE TABLE 'Restaurants_Basic' (
			'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
			'Name' TEXT,
			'Rating' REAL,
			'Rating_Count' INT,
			'Street Address' TEXT,
			'City' TEXT,
			'State' TEXT,
			'Zip' NUMERIC,
			'Latitude' REAL,
			'Longitude' REAL,
			'Price' TEXT,
			'Phone' TEXT,
			'Source' TEXT
			)
	'''
	cur.execute(statement)
	conn.commit()

	statement = '''
		CREATE TABLE 'Restaurants_Detailed' (
			'Restaurant_Id' INT,
			'Zomato_Id' INT,
			'Cuisine' TEXT,
			'Menu' TEXT
			)
	'''
	cur.execute(statement)
	conn.commit()

	conn.close()
	pass


def get_and_store_yelp_data(location="Ann Arbor", term = "restaurant", radius = 3000, limit=50, offset=0, pk=1):
	yelp_baseurl = "https://api.yelp.com/v3/businesses/search"
	yelp_params = {"location":location, "term":term, "radius":radius, "limit":limit, "offset":offset}
	yelp_headers = {"Authorization":"Bearer {}".format(YELP_API_KEY)}
	yelp_string = make_request_using_cache(request_baseurl = yelp_baseurl, request_params = yelp_params, request_headers = yelp_headers)
	list_of_restaurants = []

	conn = sqlite.connect(DBNAME)
	cur = conn.cursor()

	for x in yelp_string["businesses"]:
		try:
			name = x["name"]
		except:
			name = "None"
		try:
			rating = x["rating"]
		except:
			rating = "None"
		try:
			review_count = x["review_count"]
		except:
			review_count = "None"
		try:
			location = "{} {} {}".format(x["location"]["address1"], x["location"]["address2"], x["location"]["address3"])
		except:
			location="None"
		try:
			city = x["location"]["city"]
		except:
			city = "None"
		try:
			state = x["location"]["state"]
		except:
			state="None"
		try:
			zip_code = x["location"]["zip_code"]
		except:
			zip_code = "None"
		try:
			lat = x["coordinates"]["latitude"]
		except:
			lat = "None"
		try:
			lon = x["coordinates"]["longitude"]
		except:
			lon = "None"
		try:
			price = x["price"]
		except:
			price = "None"
		try:
			phone = x["display_phone"]
		except:
			phone = "None"
		source = "Yelp"
#making objects to return
		list_of_restaurants.append(Restaurant(name, location, city, state, zip_code))
#populating the database
		params = (name, rating, review_count, location, city, state, zip_code, lat, lon, price, phone, source)
		statement = '''
			INSERT INTO Restaurants_Basic VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		'''
		global RESTAURANT_DICT
		RESTAURANT_DICT[name] = pk
		pk += 1
		cur.execute(statement, params)
		conn.commit()
	conn.close()
	return list_of_restaurants

def get_and_store_zomato_data(searchterm):
	zomato_baseurl = "https://developers.zomato.com/api/v2.1/search"
	zomato_search_params = {"q":searchterm, "lat":42.279594, "lon":-83.732124, "radius":5000}
	zomato_headers = {"user-key":ZOMATO_API_KEY}
	zomato_search_string = make_request_using_cache(request_baseurl = zomato_baseurl, request_params = zomato_search_params, request_headers = zomato_headers)

	restaurant_id = RESTAURANT_DICT[searchterm]

	zomato_id = int(zomato_search_string["restaurants"][0]["restaurant"]["id"])

	zomato_detailurl = "https://developers.zomato.com/api/v2.1/restaurant"
	zomato_detail_params = {"res_id":zomato_id}
	zomato_detail_string = make_request_using_cache(request_baseurl = zomato_detailurl, request_params = zomato_detail_params, request_headers = zomato_headers)

	try:
		menu_url = zomato_detail_string["menu_url"]
	except:
		menu_url = "No menu items available"
	try:
		cuisine = zomato_detail_string["cuisines"]
	except:
		cuisine = "No cuisine data available"

	conn = sqlite.connect(DBNAME)
	cur = conn.cursor()

	statement = '''
		INSERT INTO Restaurants_Detailed VALUES (?, ?, ?, ?)
	'''
	params = (restaurant_id, zomato_id, cuisine, menu_url) 
	cur.execute(statement, params)
	conn.commit()

	conn.close()
	pass

def process_command(comm, restaurant_list):
	conn = sqlite.connect(DBNAME)
	cur = conn.cursor()
#menu command 
	if comm[0:4].lower() == "menu":
		try: 
			iterator = int(comm[-2:])
		except:
			iterator = int(comm[-1:])
		if iterator > len(restaurant_list):
			print("Number not in data set. Please try again.")
			pass
		try:
			get_and_store_zomato_data(restaurant_list[iterator-1].name)
			select_statement = '''SELECT Restaurants_Basic.Name, Restaurants_Basic.Id, Restaurants_Detailed.Restaurant_Id, Restaurants_Detailed.Menu '''
			from_statement = '''FROM Restaurants_Basic '''
			join_statement = '''JOIN Restaurants_Detailed '''
			on_statement = '''ON Restaurants_Basic.Id = Restaurants_Detailed.Restaurant_Id '''
			where_statement = '''WHERE Restaurants_Basic.Name = "{}" '''.format(restaurant_list[iterator-1].name)
			print(where_statement)
			statement_to_execute = select_statement + from_statement + join_statement + on_statement + where_statement
			cur.execute(statement_to_execute)
			result = cur.fetchone()[3]
			webbrowser.open(result, new=2, autoraise=True)
			pass
		except:
			print("Menu not available")
			pass
#map command
#if time, get this to look better by plotting on mapbox
	elif comm.lower() == "map":
		select_statement = '''SELECT Restaurants_Basic.Name, Restaurants_Basic.Longitude, Restaurants_Basic.Latitude '''
		from_statement = '''FROM Restaurants_Basic '''
		statement_to_execute = select_statement + from_statement
		cur.execute(statement_to_execute)
		result = cur.fetchall()
		sitenames = []
		sitelats = []
		sitelongs = []
		for x in result:
			sitenames.append(x[0])
			sitelongs.append(x[1])
			sitelats.append(x[2])

		if len(sitelats) > 0 and len(sitelongs) > 0:
			minlat = sitelats[0]
			maxlat = sitelats[0]
			minlong = sitelongs[0]
			maxlong = sitelongs[0]
		else:
			print("No restaurants to plot.")
			return None

		for x in sitelats:
			if x <= minlat:
				minlat = x
		for x in sitelats:
			if x >= maxlat:
				maxlat = x
		for x in sitelongs:
			if x <= minlong:
				minlong = x
		for x in sitelongs:
			if x >= maxlong:
				maxlong = x

		max_range = max(abs(maxlat-minlat), abs(maxlong-minlong))
		padding = max_range * .50

		lat_axis = [minlat-padding, maxlat+padding]
		long_axis = [minlong-padding, maxlong+padding]
		centerlat = (maxlat + minlat) / 2
		centerlong = (maxlong + minlong) / 2

		data = Data([
			Scattermapbox(
				lat = sitelats,
				lon = sitelongs,
				mode = 'markers',
				marker=Marker(
					size=6
					),
				text=sitenames,
				)
			])

		layout = Layout(
			autosize=True,
			hovermode="closest",
			mapbox = dict(
				accesstoken=MAPBOX_KEY,
				bearing=0,
				center=dict(
					lat=centerlat,
					lon=centerlong
				),
				pitch=0,
				zoom=12
				),
			)


		# trace1 = dict(
		# 	type = "scattergeo",
		# 	locationmode = "USA-states",
		# 	lon = sitelongs,
		# 	lat = sitelats,
		# 	text = sitenames,
		# 	mode = "markers",
		# 	marker = dict(
		# 		size = 10,
		# 		symbol = "circle",
		# 		color = "blue"
		#  	))

		# data = [trace1]


		# layout = dict(
		# 	title = "Restaurants in Ann Arbor (Hover for Restaurant Name)",
		# 	geo = dict(
		# 		scope = "usa",
		# 		projection = dict(type="albers usa"),
		# 		showland = True,
		# 		landcolor = "rgb(250, 250, 250)",
		# 		subunitcolor = "rgb(100, 217, 217)",
		# 		countrycolor = "rgb(217, 100, 217)",
		# 		lataxis = {"range": lat_axis},
		# 		lonaxis = {"range": long_axis},
		# 		center = {"lat":centerlat, "lon":centerlong},
		# 		countrywidth = 3,
		# 		subunitwidth = 3
		# 		)
		# 	)

		
		fig = dict(data=data, layout=layout)
		py.plot(fig, validate=False)
		pass
#ratings command
	elif comm.lower() == "ratings":
		select_statement = '''SELECT Restaurants_Basic.Name, Restaurants_Basic.Rating '''
		from_statement = '''FROM Restaurants_Basic'''
		statement_to_execute = select_statement + from_statement
		cur.execute(statement_to_execute)
		result = cur.fetchall()
		ratings_dict = {}
		for x in result:
			if x[1] in ratings_dict:
				ratings_dict[x[1]] += 1
			else:
				ratings_dict[x[1]] = 1
		ratings_list = []
		numbers_list = []
		for x in ratings_dict:
			ratings_list.append(x)
			numbers_list.append(ratings_dict[x])
		trace = go.Pie(labels = ratings_list, values = numbers_list)
		py.plot([trace])
#reviews command
	elif comm.lower() == "reviews":
		select_statement = '''SELECT Restaurants_Basic.Name, Restaurants_Basic.Rating, Restaurants_Basic.Rating_Count '''
		from_statement = '''FROM Restaurants_Basic'''
		statement_to_execute = select_statement + from_statement
		cur.execute(statement_to_execute)
		result = cur.fetchall()
		ratings = []
		rating_count = []
		names = []
		for x in result:
			names.append(x[0])
			ratings.append(x[1])
			rating_count.append(x[2])
		trace = go.Scatter(
			x = rating_count,
			y = ratings,
			mode = 'markers',
			text = names
			)

		data = [trace]
		py.plot(data)
		pass
#error handling
	else:
		print("Command not recognized. Please try again.")
	conn.close()
#something with cuisines if time
def interactive_prompt():
	print("Welcome to the Ann Arbor restaurant guide! Here is a list of some of the restaurants in Ann Arbor.")
	iterator = 1
	offset_iterator = 50
	create_restaurant_db()
	a2_rests = get_and_store_yelp_data()
	for x in a2_rests:
		print(str(iterator) + ". {}".format(x.name))
		iterator += 1
	print("Enter 'menu_xx' to see a particular restaurant's menu. Enter 'map' to see a map of the restaurants. Enter 'ratings' to see a pie chart of all ratings, and 'reviews' to see the ratings and number of ratings plotted on a scatter plot. 'Next' will give you the next fifty restaurants in Ann Arbor. Enter 'quit' to quit and 'help' to see this text again.")
	comm = ""
	while comm.lower() != 'exit':
		comm = input("What would you like to do?: ")
		if comm.lower() == "help":
			print("Enter 'menu_xx' to see a particular restaurant's menu. Enter 'map' to see a map of the restaurants. Enter 'ratings' to see a pie chart of all ratings, and 'reviews' to see the ratings and number of ratings plotted on a scatter plot. 'Next' will give you the next fifty restaurants in Ann Arbor. Enter 'quit' to quit and 'help' to see this text again.")
			continue
		elif comm.lower() == "next":
			results = get_and_store_yelp_data(offset = offset_iterator, pk=offset_iterator + 1)
			offset_iterator += 50
			for x in results:
				print(str(iterator) + ". {}".format(x.name))
				iterator += 1
			a2_rests += results
		elif comm.lower() == "quit":
			break
		else:
			process_command(comm, a2_rests)

if __name__=="__main__":
    interactive_prompt()
