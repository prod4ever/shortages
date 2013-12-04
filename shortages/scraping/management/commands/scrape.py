import urllib, traceback, os, logging, pdb
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import mail_admins
from bs4 import BeautifulSoup
from scraping.models import *

CACHE_PATH = '/tmp'
#These are the A-D, E-K, etc list pages
URLS = (
    'http://www.fda.gov/Drugs/DrugSafety/DrugShortages/ucm314743.htm',
    'http://www.fda.gov/Drugs/DrugSafety/DrugShortages/ucm314739.htm'
    #'http://www.fda.gov/Drugs/DrugSafety/DrugShortages/ucm314740.htm',
    #'http://www.fda.gov/Drugs/DrugSafety/DrugShortages/ucm314741.htm',
    #'http://www.fda.gov/Drugs/DrugSafety/DrugShortages/ucm314742.htm',
)

class Command(BaseCommand):

    def handle(self, **options):
        drugs_initial_count = Drug.objects.count()
        Drug.objects.all().delete()
        for url in URLS:
            self.url = url
            self.scrape_url(url)
        drugs_final_count = Drug.objects.count()

        message = """
        Drugs before: %d
        Drugs after: %d
        """ % (drugs_initial_count, drugs_final_count)
        #mail_admins('Jobson Health Shortages Scraper Ran', message)

    def scrape_url(self, url):
        print "scraping %s" % url
        page = self.fetch(url)
        self.soup = BeautifulSoup(page, 'html5lib')
        print self.soup
        drug_tables = self.soup.find_all("a")#('.middle-column table')
        #drug_tables = self.soup.select('table[summary="drug shortage details"]');
        print drug_tables

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
        print drug_name

        if not drug_name:
            raise Exception('Drug Name not found')
        self.drug = Drug.objects.create(
            name=drug_name,
            url=self.url
        )
        #Ignore <thead> row
        rows = table.find_all('tr')[1:]
        for row in rows:
            if len(row.find_all('td')) > 2:
                self.parse_supplier(row)
            self.parse_product(row)

    def parse_supplier(self, row):
        print row.find_all('td')
        supplier_name = row.find('td').text.replace(':', '\n')

        try:
            related_info = row.find_all('td')[3].text
        except:
            related_info = None
        reason = row.find_all('td')[4].text

        try:
            date_updated = row.find_all('td')[5].text.replace('Reverified', '').replace('Revised', '').strip()
            m, d, y = date_updated.split('/')
            reverified_datetime = datetime(int(y), int(m), int(d))
        except:
            reverified_datetime = None

        self.ds = DrugSupplier.objects.create(
            drug=self.drug,
            name=supplier_name,
            related_info=related_info,
            reason=reason,
            reverified=reverified_datetime
        )
        print self.ds

    def parse_product(self, row):
        """
        We can have 1-2 rows in the case that this row is only a prouct (no supplier name) or 5.  
        
        -For Product Row
        We always have a name in [0] and sometimes an availability in [1]

        -For Supplier Row
        We generally have a Supplier row in [0] (so its ignored here for a Product context)
        """
        if len(row.find_all('td')) <= 2:
            try:
                availability = row.find_all('td')[1].text
            except:
                availability = None
            name = row.find_all('td')[0].text
        else:
            try:
                availability = row.find_all('td')[2].text
            except:
                availability = None
            name = row.find_all('td')[1].text

        product = Product.objects.create(
            supplier=self.ds,
            name=name,
            availability=availability
        )

    def get_drug_name(self, table):
        """
        Extract a drug name from wierd markup above a table
        """
        drug_el = table.find_previous()
        if drug_el.name == 'a':
            drug_el = drug_el.find_parent()
        elif drug_el.name == 'p':
            drug_el = drug_el.find('b')
        text = drug_el.text[:255].strip()
        if text.startswith('*'): raise Exception('Invalid drug name, cannot deal with table.')
        return text

    def fetch(self, url):
        """
        Cache html in /tmp - TODO expiration
        """
        #cache_key = url
        #replace_map = {
        #    '/': '', ':': '', '.': ''
        #}
        #for search, replace in replace_map.items():
        #    cache_key = cache_key.replace(search, replace)
        #cache_path = os.path.join(CACHE_PATH, cache_key)
        print url
        #if not os.path.exists(cache_path):
        #logging.info('Downloading file at %s to %s' % (url, cache_path))
        print "getting new copy"
        page = urllib.urlopen(url)
        return page.read()
        #cache = open(cache_path, 'w')
        #cache.write(page.read())
        #cache.close()
        #else:
        #    print "cached"
         #   print open(cache_path, "r")
        

        #return open(cache_path, 'r')