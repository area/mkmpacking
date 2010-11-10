from BeautifulSoup import BeautifulSoup
import re
import mechanize
import urllib
import cookielib

br=mechanize.Browser()

# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

# The site we will navigate into, handling it's session
def getCardInfo(url):
	br.open(url)
	br.select_form(nr=2)

	br.form["productFilter[idLanguage][]"]=["1"]
	br.form["productFilter[condition][]"]=["MT", "NM", "EX"]

	br.submit()
	html = br.response().read()

	soup = BeautifulSoup(html)
	records=[]
	rows = soup.findAll("tr", {"class" : re.compile(".* thick hoverator")})
	for tr in rows:
		userurl= tr.span.span.a.attrs[0][1]
		username =  tr.span.span.a.contents[0]
		price = tr.find("td", {"class" : re.compile("alignRight nowrap.*")}).contents[0].replace(' &#x20AC;','').replace(',','.')
		record = (username, userurl, price)
		records.append(record)

	print records


getCardInfo('http://www.magiccardmarket.eu/Senseis_Divining_Top_(Champions_of_Kamigawa).c1p12179.prod')

