import urllib, traceback, os, logging, pdb
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from bs4 import BeautifulSoup
from scraping.models import *

CACHE_PATH = '/tmp'
URLS = (
	'http://www.fda.gov/Drugs/DrugSafety/DrugShortages/ucm314743.htm',
	'http://www.fda.gov/Drugs/DrugSafety/DrugShortages/ucm314739.htm',
	'http://www.fda.gov/Drugs/DrugSafety/DrugShortages/ucm314740.htm',
	'http://www.fda.gov/Drugs/DrugSafety/DrugShortages/ucm314741.htm',
	'http://www.fda.gov/Drugs/DrugSafety/DrugShortages/ucm314742.htm',
	
)

class Command(BaseCommand):

	def handle(self, **options):
		Drug.objects.all().delete()
		for url in URLS:
			self.url = url
			self.scrape_url(url)

	def scrape_url(self, url):
		pdb.set_trace()
		page = self.fetch(url)
		pdb.set_trace()
		self.soup = BeautifulSoup(page, 'html5lib')
		drug_tables = self.soup.select('div[class="middle-column"] > table')

		for table in drug_tables:
			if 'summary' in table.attrs and table['summary'] == 'drug shortage details':
				try:
					self.parse_drug_table(table)
				except:
					print 'Could not parse drug table'
					traceback.print_exc()
					continue

	def parse_drug_table(self, table):
		print '--' * 20
		drug_name = self.get_drug_name(table)
		if not drug_name:
			raise 'Drug Name not found'
		self.drug = Drug.objects.create(
			name = drug_name,
			url = self.url
		)
		rows = table.find_all('tr')[1:]
		for row in rows:
			if len(row.find_all('td')) > 2:
				self.parse_supplier(row)
			self.parse_dosage(row)

	def parse_supplier(self, row):
		print row.find_all('td')
		supplier_name = row.find('td').text
		related_info = row.find_all('td')[3].text
		reason = row.find_all('td')[4].text
		date_updated = row.find_all('td')[5].text.replace('Reverified', '').replace('Revised', '').strip()
		try:
			m, d, y = date_updated.split('/')
			reverified_datetime = datetime(int(y), int(m), int(d))
		except:
			reverified_datetime = None

		self.ds = DrugSupplier.objects.create(
			drug = self.drug,
			name = supplier_name,
			related_info = related_info,
			reason = reason,
			reverified = reverified_datetime
		)
		print self.ds

	def parse_dosage(self, row):
		if len(row.find_all('td')) == 2:
			availability = row.find_all('td')[1].text
			name = row.find_all('td')[0].text
		else:
			availability = row.find_all('td')[0].text
			name = row.find_all('td')[1].text

		product = Product.objects.create(
			supplier = self.ds,
			name = name,
			availability = availability
		)

	def get_drug_name(self, table):
		drug_el = table.find_previous()
		if drug_el.name == 'a':
			drug_el = drug_el.find_parent()
		elif drug_el.name == 'p':
			drug_el = drug_el.find('b')
		text = drug_el.text[:255]
		return text

	def fetch(self, url):
		cache_key = url
		replace_map = {
			'/': '', ':': '', '.': ''
		}
		for search, replace in replace_map.items():
			cache_key = cache_key.replace(search, replace)
		cache_path = os.path.join(CACHE_PATH, cache_key)
		if not os.path.exists(cache_path):
			logging.info('Downloading file at %s to %s' % (url, cache_path))
			page = urllib.urlopen(url)
			cache = open(cache_path, 'w')
			cache.write(page.read())
			cache.close()
		return open(cache_path, 'r')