import unittest
import finalproject
from finalproject import *

class TestClassConstruction(unittest.TestCase):
	def testConstructor(self):
		r1 = finalproject.Restaurant("North Quad", "105 S State Street", "Ann Arbor", "MI", "48109")
		r2 = finalproject.Restaurant(street_address="105 S State Street", city="Ann Arbor", zip_code="48109", name="North Quad", state="MI")
#1
		self.assertEqual(r1.name, "North Quad")
#2
		self.assertEqual(r1.address, "105 S State Street Ann Arbor MI 48109")
#3
		self.assertEqual(r2.name, "North Quad")
#4
		self.assertEqual(r2.address, "105 S State Street Ann Arbor MI 48109")

class TestYelpData(unittest.TestCase):
	def test_restaurants_basic_table(self):
		conn = sqlite.connect(DBNAME)
		cur = conn.cursor()
		statement = 'SELECT Name from Restaurants_Basic'
		cur.execute(statement)
		results1 = []
		for x in cur:
			results1.append(x[0])
#5
		self.assertIn('eat', results1)
#6
		self.assertGreater(len(results1), 0)

		statement = 'SELECT City from Restaurants_Basic'
		cur.execute(statement)
		results2 = []
		for x in cur:
			results2.append(x[0])
#7
		self.assertEqual(results2[30], "Ann Arbor")

		statement = 'SELECT Price from Restaurants_Basic'
		cur.execute(statement)
		results3 = []
		for x in cur:
			results3.append(x[0])
#8
		self.assertIn("$", results3[6])
		self.assertEqual(results3[0], "$$")		

		conn.close()

class TestZomatoData(unittest.TestCase):
	def test_restaurants_detailed_table(self):
		conn = sqlite.connect(DBNAME)
		cur = conn.cursor()
		statement = 'SELECT Zomato_Id from Restaurants_Detailed'
		cur.execute(statement)
		results1 = []
		for x in cur:
			results1.append(x[0])
#9
		self.assertEqual(len(str(results1[0])), 8)
#10
		self.assertEqual(str(results1[0])[0], "1")

		statement = 'SELECT Menu, Photo from Restaurants_Detailed'
		cur.execute(statement)
		results2 = []
		results3 = []
		for x in cur:
			results2.append(x[0])
			results3.append(x[1])
#11
		self.assertIn("www.", results2[2])
#12
		self.assertIn("www.", results3[1])
#test that process_command has supplied correct info into table
#13
		self.assertEqual(results2[0], "https://www.zomato.com/detroit/aventura-ann-arbor/menu?utm_source=api_basic_user&utm_medium=api&utm_campaign=v2.1&openSwipeBox=menu&showMinimal=1#tabtop")
#14
		self.assertEqual(results3[0], "https://www.zomato.com/detroit/aventura-ann-arbor/photos?utm_source=api_basic_user&utm_medium=api&utm_campaign=v2.1#tabtop")

		conn.close()

unittest.main()
