from BeautifulSoup import BeautifulSoup
import re

import urllib




f = urllib.urlopen("http://www.magiccardmarket.eu/Senseis_Divining_Top_(Champions_of_Kamigawa).c1p12179.prod")
# Read from the object, storing the page's contents in 's'.
s = f.read()
f.close()

soup = BeautifulSoup(s)
records=[]
rows = soup.findAll("tr", {"class" : re.compile(".* thick hoverator")})
for tr in rows:
    userurl= tr.span.span.a.attrs[0][1]
    username =  tr.span.span.a.contents[0]
    price = tr.find("td", {"class" : re.compile("alignRight nowrap.*")}).contents[0]
    record = (username, userurl, price)
    records.append(record)

print records
