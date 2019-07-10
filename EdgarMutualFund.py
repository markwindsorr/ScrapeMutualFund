# Dependencies

try:
    from urllib.parse import urljoin
except ImportError:
     from urlparse import urljoin

from bs4 import BeautifulSoup, SoupStrainer
import requests
import csv
import re
import xml.etree.ElementTree as ET

class EdgarMutualFund:

    #Constants
    BASE_URL = "https://www.sec.gov"
    URL_TEMPLATE = "/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=13F"
    company_name = ""


    def __init__(self):
        self.session = requests.Session()

    # Here we search for most recent 13-F xml and pass it to scrape_xml
    def search_by_cik(self, cik):

        self.company_name = self.cik_to_name(cik) # get company name to use for .tsv file name

        #1. Company search url with cik 
        url_search = urljoin(self.BASE_URL, self.URL_TEMPLATE.format(cik=cik))

        """
        2. We need to get to filing detail page of the mutual fund
        by selecting the first documents button which will be most recent
        We will use soup strainer to parse only the button
        """
        parse_button = SoupStrainer('a', {"id": "documentsbutton"})
        soup = BeautifulSoup(self.session.get(url_search).content, 'lxml', parse_only=parse_button)
        button_url = soup.find('a', {"id": "documentsbutton"})['href']
        button_url = urljoin(self.BASE_URL, button_url)

        """
        3.  Now we need to get the url of the XML information table file 
        within the document format file table
        """
        parse_infotable = SoupStrainer('tr', {"class": "blueRow"})
        soup = BeautifulSoup(self.session.get(button_url).content, 'lxml', parse_only=parse_infotable)
        #Here we have 2 blue row classes as rows in the table, we want the second one
        infotable_url = soup.find_all('tr', {"class": 'blueRow'})[-1].find('a')['href'] 
        infotable_url = urljoin(self.BASE_URL, infotable_url)

        return self.scrape_xml(infotable_url)


    """
    Here we must extract the tags as headers for our tsv file and extract the data
    from the attributes. We will pass headers and data to write_to_file to create
    the .tsv
    """
    def scrape_xml(self, infotable_url):

        """
        1. Get Response from the info table url and create an element tree
        from the xml string
        """
        xml_response = self.session.get(infotable_url)
        root = ET.fromstring(xml_response.text)


        """
        2. From the first element in root we can get the headers.
        We also need to remove the url thats attached to the tag 
        """
        header_tags = [element.tag for element in root[0].iter()]
        headers = [h.replace('{http://www.sec.gov/edgar/document/thirteenf/informationtable}', '') for h in header_tags]
        headers.pop(0) #We do not want 'infoTable' tag as a header

        """
        3. Now to scrape the data. We will loop through root and the sub elements
        We want to be careful of elements with children because we have these elements
        as headers but they will not have a singular value so I will assign an empty
        string to those fields
        """
        data = [] 
        for element in root:
            row = []
            for attribute in element:
                if "\n" not in attribute.text: #next line means element with children
                    row.append(attribute.text)
                else:
                    row.append("")
                for sub_attribute in attribute:
                    if "\n" not in sub_attribute.text:
                        row.append(sub_attribute.text)
            data.append(row)

        return self.write_to_file(headers, data)



    # Write data to .tsv file
    def write_to_file(self, headers, data):

        #1. Open save file
        file_name = self.company_name.replace(" ", "") + "_13F.tsv"
        save_file = open(file_name, 'w')

        #2. Write headers to file
        writer = csv.writer(save_file, dialect='excel-tab')
        writer.writerow(headers)

        #3. Write data to file
        for row in data:
            writer.writerow(row)

        print("A tsv file of holdings from " + self.company_name + "has been generated" )

    
    def ticker_to_cik(self, ticker):

        #1. URL to search by ticker
        url_search = urljoin(self.BASE_URL, self.URL_TEMPLATE.format(cik=ticker))
        cik_re_pattern = re.compile(r'.*CIK=(\d{10}).*')
        
        #2. Compile a regular expression pattern into a regular expression object 
        # to find CIK
        response = self.session.get(url_search.format(ticker), stream = True)
        cik = cik_re_pattern.findall(response.text)[0]
        
        return cik
 

    def cik_to_name(self, cik):

        #1. URL search
        url_search = urljoin(self.BASE_URL, self.URL_TEMPLATE.format(cik=cik))

        #2. Parse Company Name
        parse_name = SoupStrainer('span', {"class": "companyName"}) 
        soup = BeautifulSoup(self.session.get(url_search).content, 'lxml', parse_only=parse_name)
        name_tag = soup.find('span', {"class": "companyName"})
        name = name_tag.contents[0]

        return name











































