from BeautifulSoup import BeautifulSoup
import re
import mechanize
import urllib
import cookielib
import numpy as np

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

def max_loc(ar):
	maxval=max(ar)
	for idx in range(np.shape(ar)[0]):
		if (ar[idx]==maxval):
			return idx
def getShipping(country, value, number, insurance):
	insured=False
	if (value > 25 or (insurance ==False and value > 10)):
		insured = True

	if (country=="D"):
		if (insured):
			if (number<=16):
				return 3.6
			elif (number <=186):
				return 5.9
			elif (number<=399):
				return 8.55
			else:
				die("How many freaking cards are you buying!?!")
		else:
			if (number<=4):
				return 1
			elif (number<=16):
				return 1.55
			elif (number<=186):
				return 3.80
			else:
				die("How many cards!?")
	else:
		print "Warning: Unknown country " + country
		if (insured):
			if (number<=16):
				return 3.6
			elif (number <=186):
				return 5.9
			elif (number<=399):
				return 8.55
			else:
				die("How many freaking cards are you buying!?!")
		else:
			if (number<=4):
				return 1
			elif (number<=16):
				return 1.55
			elif (number<=186):
				return 3.80
			else:
				die("How many cards!?")
		if (insured):
			if (number<=16):
				return 3.6
			elif (number <=186):
				return 5.9
			elif (number<=399):
				return 8.55
			else:
				die("How many freaking cards are you buying!?!")
		else:
			if (number<=4):
				return 1
			elif (number<=16):
				return 1.55
			elif (number<=186):
				return 3.80
			else:
				die("How many cards!?")


def getCardInfo(url):
	br.open(url)
	#br.select_form(nr=2)

	#br.form["productFilter[idLanguage][]"]=["1"]
	#br.form["productFilter[condition][]"]=["MT", "NM", "EX"]

	#br.submit()
	#html = br.response().read()
	html = br.response()
	soup = BeautifulSoup(html)
	records=[]
	rows = soup.findAll("tr", {"class" : re.compile(".* thick hoverator")})
	for tr in rows:
		userurl= tr.span.span.a.attrs[0][1]
		username =  tr.span.span.a.contents[0]
		price = tr.find("td", {"class" : re.compile("alignRight nowrap.*")}).contents[0].replace(' &#x20AC;','').replace(',','.')
		countryName=re.search('.*/(.*)\.png', tr.span.span.nextSibling.nextSibling.img.attrs[1][1]).group(1)
		record = [username, userurl, countryName, float(price), 1, url]
		records.append(record)

	return records

def Cost(order):
	sellers=[]
	cost=0
	for card in order:
		added=False
		for idx,seller in enumerate(sellers):
			if (seller[0] == card[0]):

				#Just increase the number of cards from this seller
				sellers[idx][2] += card[4]
				sellers[idx][3] += card[4]*card[3]
				added=True
				break
		if(added!=True):
			#Then we've not had anything yet from this seller
			sellers.append([card[0], card[2], card[4],card[3]*card[4]])

		cost+=card[4] * card[3]
	for seller in sellers:
		cost+=getShipping(seller[1],seller[3],seller[2],True)

	return cost

def reverse_lookup_seller(d, v):
	for k in d:
        	if d[k][0] == v:
			return k
	raise ValueError

cards =[]
order =[]
#cards.append(getCardInfo('http://www.magiccardmarket.eu/Senseis_Divining_Top_(Champions_of_Kamigawa).c1p12179.prod'))
#cards.append(getCardInfo('http://www.magiccardmarket.eu/Lightning_Greaves_(Friday_Night_Magic_Promos).c1p21792.prod'))
#cards.append(getCardInfo('http://www.magiccardmarket.eu/Teneb_the_Harvester_(Planar_Chaos).c1p14342.prod'))

cards.append(getCardInfo('http://127.0.0.1/mkmtest/1.html'))
cards.append(getCardInfo('http://127.0.0.1/mkmtest/2.html'))
cards.append(getCardInfo('http://127.0.0.1/mkmtest/3.html'))
cards.append(getCardInfo('http://127.0.0.1/mkmtest/4.html'))
cards.append(getCardInfo('http://127.0.0.1/mkmtest/5.html'))
cards.append(getCardInfo('http://127.0.0.1/mkmtest/6.html'))


#Start with the cheapest of each card.
order.append(cards[0][0])
order.append(cards[1][0])
order.append(cards[2][0])

#Work out the cost


MP=np.array([[]])

sellerdict = {}


for idx,card in enumerate(cards):
	#Add a column for this card.
	MP = np.append(MP, np.zeros( (np.shape(MP)[0], 1) ), 1 )
	for seller in card:
		if seller[0] not in sellerdict:
			sellerdict[seller[0]]=[len(sellerdict),seller]
			#Add a new row to the matrix for this seller
			MP = np.append(MP, np.zeros( (1, np.shape(MP)[1]) ), 0 )
		#Insert the price - if we don't already have one... some sellers sell multiple copies at different prices; the cheapest one is good enough for us, as we've already done some selection above.
		if (MP[sellerdict[seller[0]][0]][idx] == 0):
			MP[sellerdict[seller[0]][0]][idx] = seller[3] + getShipping(seller[2], seller[3], 1, seller[4])

print MP

#Last row won't have any content, as inserting the first colum into the matrix also inserts a first row, so we're one ahead of ourselves the whole time.
#Delete it.

MP = np.delete(MP,[np.shape(MP)[0]-1],0)

#Find the minimal prices
P_min = []
SV_min = []
for col in range(0,np.shape(MP)[1]):
	#Get the minimum price for this column
	pricemin=999999
	for row in range(0,np.shape(MP)[0]):
		if ( (MP[row][col] < pricemin) and (MP[row][col]>0)):
			sellerRow=row
			pricemin= MP[row][col]
	P_min.append(pricemin)
	SV_min.append(sellerRow)

#print np.take(MP, [0],1)

print P_min
print SV_min
PV=np.zeros_like(P_min)
cost=0
#If we simply buy from the cheapest seller for each item, what's the cost?

order=[]

for idx,sellerID in enumerate(SV_min):
	for seller in cards[idx]:
		if (seller[0] == reverse_lookup_seller(sellerdict, sellerID)):
			order.append(seller)

print "Find a better cost than " +  str(Cost(order))

while(True):
	#Find the sum of the maximal bundle for each seller
	
	MaxDiscount = []
	BundleCost = []

	for row in range(0,np.shape(MP)[0]):
		order=[]
		for col in range(0,np.shape(MP)[1]):
			if (MP[row][col]!=0):
				#Then this seller sells this good - add to our 'order' to calculate the bundle cost.
				for seller in cards[col]:
					if (seller[0] == reverse_lookup_seller(sellerdict, row)):
						order.append(seller)
						#This break is here because sometimes the same seller appears on the same page. If this is the case, skip the remaining instances.
						break
		BundleCost.append(Cost(order))
		MaxDiscount.append(sum(sum(np.take(MP,[row],0))) - BundleCost[row])
	
	#Calculate MaxSubCost for each seller.
	MaxSubCost = []


	for row in range(0,np.shape(MP)[0]):
		order=[]
		for col in range(0,np.shape(MP)[1]):
			if (MP[row][col]!=0):
				#Then this seller sells this good.
				#Add the minimum cost for a product...
				for seller in cards[col]:
					if (seller[0] == reverse_lookup_seller(sellerdict, SV_min[col])):
						order.append(seller)
						break
		MaxSubCost.append(Cost(order))
	
	
	complete = True
	for jdx, SingleBundleCost2 in enumerate(BundleCost):
		if ((SingleBundleCost2 - MaxSubCost[jdx]) <= 0):
			complete=False
			break

	if (complete):
		break

	#Unless we're very unlucky, buying as many cards as possible from a single seller is probably good enough. Strictly, should implement FindMinBundle etc.

	gain=[]
	for row in range(0,np.shape(MP)[0]):
		if (MaxSubCost[row]!=0):
			gain.append((MaxSubCost[row]-BundleCost[row])/MaxSubCost[row])
		else:
			gain.append(-999)

	bestSeller= max_loc(gain)
	bestBundle= np.take(MP, [bestSeller],0)
	for idx in range(np.shape(bestBundle)[1]):
		if (bestBundle[0][idx] > 0):
			PV[idx] = bestSeller
			#Now set the column containing this item to 0 for all serllers - as we have now decided who to buy it from.a
			for jdx in range(np.shape(MP)[0]):
				MP[jdx][idx] = 0

	cost += BundleCost[bestSeller]
	#Have we now bought all of our items?
	if (np.argmax(MP)==0):
		break

	


print "Best cost found: " + str(cost)
for idx,card in enumerate(cards):
	for jdx, seller in enumerate(card):
		if (seller[0]==reverse_lookup_seller(sellerdict,PV[idx])):
			print str(seller[5]) + " from " + seller[0]
