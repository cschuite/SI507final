Data sources used:
Zomato API and Yelp API
Both require authentication in the form of API keys. See https://www.yelp.com/developers/documentation/v3/get_started and https://developers.zomato.com/api#headline2. Put your keys in a file called secrets.py under the variable names YELP_KEY and ZOMATO_KEY.

Other information needed:
You will need an account on Mapbox, which partners with Plotly to produce better, more detailed maps. See https://www.mapbox.com/install/. Put your mapbox access token in the secrets.py file under the name MAPBOX_KEY.
You may also need an account on Plotly, although no special credentials need to be passed into the program.

Code structure:
Aside from helper functions that do things like building the database or caching the code, there are four main functions. The first (get_and_store_yelp_data) gets data from the Yelp API or the cache and stores it in the appropriate database table, as well as returning a list of Restaurant objects that I use to pass parameters into the next function, get_and_store_zomato_data, which gets data from the Zomato API or the cache and stores it in the appropriate database table. The third (interactive_prompt) asks users for input, and the fourth (process_command) retrieves the data and presents it for certain commands.

User guide:
Run finalproject.py. A list of the top fifty restaurants in Ann Arbor will be automatically generated. You can then launch the menu or photo page for that restaurant ('menu_xx' or 'photo_xx'), see how many restaurants offer which types of cuisines ('cuisines'), see all of the ratings displayed in a pie chart ('ratings'), see ratings and review numbers plotted on a scatter plot ('reviews'), or see a map of all of the restaurants ('map'). You can also type 'next' to add more restaurants to the list, at which point they will be included in all of the previous commands. Type 'help' for an explanation of all commands and 'quit' to quit the program.