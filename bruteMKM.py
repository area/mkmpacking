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

    if (country=="German"):
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
    elif (country=="Spain"):
        if (insured):
            if (number<=4):
                return 3.6
            elif (number<=16):
                return 3.90
            elif (number<=36):
                return 4.8
            elif (number<=85):
                return 6.75
            else:
                die("Too many cards!?")
        else:
            if (number<=4):
                return 1
            elif (number<=16):
                return 1.6
            elif (number<=36):
                return 2.5
            elif (number<=85):
                return 4.15
            else:
                die("Too many cards!?")
            
    elif (country=="Italy"):
        if (insured):
            if (number<=4):
                return 8.1
            elif (number<=16):
                return 9.75
            elif (number<=40):
                return 10.50
            elif (number<=100):
                return 12.00
            else:
                die("Too many cards!?")
        else:
            if (number<=4):
                return 1
            elif (number<=16):
                return 1.8
            elif (number<=40):
                return 2.5
            elif (number<=200):
                return 5
    
    elif (country=="Portugal"):
        if (insured):
            if (number<=4):
                return 3.4
            elif (number<=16):
                return 3.8
            elif (number<=40):
                return 4.05
            elif (number<=899):
                return 30
            else:
                die("Too many cards!?")
        else:
            if (number<=4):
                return 1
            elif (number<=16):
                return 1.55
            elif (number<=40):
                return 2.5
            elif (number<=100):
                return 5
    elif (country=="France"):
        if (insured):
            if (number<=87.5):
                return 7.5
            else:
                die("Too many cards!?")
        else:
            if (number<=4):
                return 1
            elif (number<=16):
                return 1.3
            elif (number<=87.5):
                return 3.8
            else:
                exit("Too many cards!?!")


    


    else:
    #   print "Warning: Unknown country " + country
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
        countryName= re.search('Item location: (.*?)\'', str(tr.span.span.nextSibling.nextSibling.span)).group(1)
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

f = open('./cardURLS.txt', 'r')

for line in f:
    cards.append(getCardInfo(line))

f.close()
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

PV = np.zeros(np.shape(MP)[1],dtype=np.int)
print PV
#Increment by one.
mincost=99999
while(True):
    for idx in range(np.shape(MP)[1]-1,-1,-1):
        if (idx==len(PV)-1):
            PV[idx]+=1
        else:
            if (PV[idx+1] == np.shape(cards[idx+1])[0]):
                PV[idx+1]=0
                PV[idx]+=1
    if (PV[0]==np.shape(cards[0])[0]): break
    order=[]
    for col in range(len(PV)-1,-1,-1):
        order.append(cards[col][PV[col]])
    if (Cost(order) < mincost):
        mincost=Cost(order)
        PVB=PV
        bestorder=order
        print "New Best: " + str(mincost)


print PVB
print mincost
print bestorder
    
