# Parse Mutual Fund Holdings

Coding Challenge

Parse mutual fund holdings by scraping the latest 13F xml file
and generate a .tsv file.


### How to Run

First of all, make sure we are upgraded to python 3 and pip3 and
all dependencies are installed

Navigate to the ScrapeMutualFund directory and run `./main.py`. We will now be asked
to input a central index key (CIK) or ticker. If we enter a valid CIK/ticker that 
has 13F reports filed in edgar, the program will generate a .tsv file from the 
xml.

Will not work for funds without 13 F reports filed


### External Dependencies
- requests
- BeautifulSoup 
- re
- csv


### Testing

I included a list of 40000+ mutual fund tickers (MutualFundSymbols.txt) and a lot of 
them don't have 13F reports filed, so its useful to know which mutual funds do have 13F 
reports filed before hand.

### Goals

How we could get previous reports? When using the BeautifulSoup parser, we can use
the find_all method to return a list of tags, in this case it we would be looking for
the documents button. Once we have the list of tags, we can specify which one we want
to use by choosing an index of the tag list.

Thoughts on how to deal with different formats. When scraping the xml I choose not to
explicitly define the tags/headers when parsing because I knew there was a possibility of the format
being different. So first, I looped through the first element in the element tree 
to get the headers used for the .tsv file (issuer, titleOfClass, cusip etc.).

Since the format of the 13F xml can be different, I chose not create a set using a set 
comprehension which would take one line of code (and looks a lot cleaner):

issuer = {h.text for h in soup.find_all((lambda tag: 'issuer' in tag.name.lower()))} 

(notice how we need to know the tag here)

Instead, I looped through the tags and their nested tags (if the tag has children) and 
added the attributes to a list called data, which includes all relevant data of the 
xml. Data is then used to write the .tsv file

 
