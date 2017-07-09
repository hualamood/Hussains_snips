from selenium import webdriver
from bs4 import BeautifulSoup
from urllib import urlencode
import requests
import couchdb
import hashlib
import time
import sys


class CouchDatabase:
	def __init__(self, DATABASE):
		self.server = couchdb.Server()

		try:
			self.db = self.server[DATABASE]
		except:
			self.db = self.server.create(DATABASE)

		try:
		    print self.db['data']
		except:
		    self.db['data'] = {}

	# This function adds elements into database,
	#it also checks for new elements and adds them, and it checks for duplicates
	def inviteToCouch(self, data):
		doc = self.db.get('data')

		data_keys = [d[0] for d in data.items()]
		db_keys = [d[0] for d in doc.items()]

		# Here we check for all the keys in our list and the keys in the database
		# If the keys dont exist we add them

		for d in data_keys:
			if not d in db_keys:
				doc[d] = []

		for digest in data['digest']:
			if not digest in doc['digest']:
				for d in db_keys:
					print d
					if d in data_keys:
						doc[d].append(data[d][data['digest'].index(digest)])
					else:
						try:
							doc[d].append('')
						except:
							continue

		self.db.save(doc)
		return self.db['data']

class DubizzleScraper:
	def __init__(self, url):

		#These are the parameters that you can use to specify the dubizzle search
		self.params = urlencode({
			#'keywords' : '',
			# 'seller_type' : '',
			# 'is_search' : 1,
			# 'kilometers__gte' : '',
			# 'price__gte' : '',
			# 'price__lte' : '',
			# 'year__gte' : '',
			# 'year__lte' : '',
			# 'kilometers__lte' : '',
			# 'is_basic_search_widget' : 1,
		});
		self.p_url = ''

		self.base_url = url

		self.url = url

		self.driver = webdriver.Firefox()

		self.data = {
			# 'title' : [],
			# 'image' : [],
			# 'link' : [],
			# 'year' : [],
			# 'km' : [],
			# 'price' : [],
			# 'digest' : [],
		}



	def setParams(self, params):
		self.params = urlencode(params)
		self.url = self.base_url + '?' + self.params

	def initScraper(self):
		self.driver.set_window_size(1120, 550)
		self.driver.get(self.url)

	def add(self,List,Item):
		try:
			return self.data[List] + [Item]
		except KeyError:
			return [Item]

	def Scrape(self):
		self.initScraper()
		page=1
		while True:
			#try:
				if self.p_url == self.driver.current_url:
					return 1
				else:
					print "------------------------"
					print "Page: {0}".format(page)
					print "------------------------"
					time.sleep(0.1)

				d = self.driver.page_source

				soup = BeautifulSoup(d, "html5lib").body
				#print soup

				if not soup.findAll('div', {'class' : 'hit-body'}) == []:
					for i in soup.findAll('div', {'class' : 'hit-body'}):
						try:
							desc = i.find('div', {'class' : 'hit-description'})
							info = desc.find('div', {'class':'hit-summary col-count-2'}).findAll('div')

							image_link = i.find('div', {'class' : 'hit-image'}).findAll('a')[0].findAll('img')[0].get('src')
							post_link = desc.findAll('a')[0].get('href')

							title = desc.findAll('a')[0].contents[0]
							price = i.find('div', {'class':'hit-right'}).find('div', {'class':'hit-price'}).findAll('h3')[0].contents[1]
							year = info[0].contents[5]
							km = info[1].contents[5]


							#If anyone ever reads this and is confused over what the digest is
							#Its for the invite function in the database class
							#Its used for checking if the post has already been added to the database.
							#In order to prevent duplicates.

							digest = str(hashlib.sha224(str(title) + str(year) + str(km) + str(price)).hexdigest())

							# self.data['title'].append(title)
							# self.data['image'].append(image_link)
							# self.data['link'].append(post_link)
							# self.data['year'].append(year)
							# self.data['km'].append(km)
							# self.data['price'].append(price)
							# self.data['digest'].append(digest)

							self.data.update({
								'title': self.add('title',title),
								'image' : self.add('image',image_link),
								'link' : self.add('link',post_link),
								'year' : self.add('year',year),
								'km' : self.add('km',km),
								'price' : self.add('price',price),
								'digest' : self.add('digest',digest),
							})

							print "Title: {0}".format(title)
							print "Image: {0}".format(image_link)
							print "Link: {0}".format(post_link)
							print "Year: {0} \nKM: {1}".format(year, km)
							print "Price: {0}".format(price)
							print

						except:
							continue
				elif not soup.findAll('div', {'class' : 'list-item-wrapper'}) == []:
					for i in soup.findAll('div', {'class' : 'list-item-wrapper'}):
						#try:
							title_span = i.find('span', {'class':'title'}).findAll('a')[0]
							title = title_span.contents
							post_link = title_span.get('href')

							price = i.find('div', {'class' : 'price'}).contents[0]
							print price
							price = "".join(price.split()).replace("AED", "")

							main = i.find('div', {'class' : 'block has_photo'})

							image_link = main.find('div', {'class' : 'thumb'}).findAll('a')[0].findAll('div')[0].get('style').replace("background-image:url(","").replace(");", "")
							desc = main.find('div', {'class' : 'description '})

							#Check for none type error here
							#Possibly just use try except
							bread = desc.find('p', {'class' : 'breadcrumbs'})
							print bread
							bread =  bread.replace(" ", "")
							print bread
							bread = bread.split('&#8234;&gt;&#8234;')[-2:]
							print bread

							c_brand = bread[0]
							c_type = bread[1]

							features = desc.findAll('ul', {'class' : 'features'})[0].findAll('li')
							year = features[0].findAll('strong')[0].contents[0]
							km = features[1].findAll('strong')[0].contents[0]

							digest = str(hashlib.sha224(str(title) + str(year) + str(km) + str(price)).hexdigest())


							self.data.update({
								'title': self.add('title',title),
								'image' : self.add('image',image_link),
								'link' : self.add('link',post_link),
								'year' : self.add('year',year),
								'km' : self.add('km',km),
								'price' : self.add('price',price),
								'digest' : self.add('digest',digest),
								'brand' : self.add('brand', c_brand),
								'type' : self.add('type', c_type),
							})

							print "Title: {0}".format(title)
							print "Image: {0}".format(image_link)
							print "Link: {0}".format(post_link)
							print "Year: {0} \nKM: {1}".format(year, km)
							print "Price: {0}".format(price)
							print "Brand: {0}\nType: {1}".format(c_brand, c_type)
							print
						#except:
						#	continue

				self.p_url = self.driver.current_url
				self.driver.find_element_by_css_selector('.ais-Pagination__item.ais-Pagination__itemNext').click()
				page += 1

			#except:
				#return 1
			#	continue

	def Scraper(self):
		self.Scrape()
		self.driver.quit()
		return self.data

couch = CouchDatabase('psearch')
s = DubizzleScraper('https://dubai.dubizzle.com/motors/used-cars/')
s.setParams({
	'keywords' : 'dodge',
})
couch.inviteToCouch(s.Scraper())
