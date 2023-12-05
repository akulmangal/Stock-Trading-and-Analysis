import sqlite3
from django.shortcuts import render
from datetime import date
import yahoo_fin.stock_info as si
from django.shortcuts import HttpResponse
import yfinance as yf
global dematAccNo,Email,Password


#dematAccNo = 12345678

def addToPortfolio(cDematAccNo, Tickr, quantity):
    connectiona = sqlite3.connect('PROJECT.db')
    cursor = connectiona.cursor()
    cursor.execute("insert into aCustomer_SharesOwned values (?,?,?)",(cDematAccNo, Tickr, quantity))
    connectiona.commit()
    cursor.close()
    connectiona.close()
    return
def updatePortfolio(cDematAccNo, Tickr, quantity):
    connectionu = sqlite3.connect('PROJECT.db')
    cursor = connectionu.cursor()
    cursor.execute("select pUnits from aCustomer_SharesOwned where cDematAccNo = ? and pTicker =?", (cDematAccNo, Tickr))
    data = cursor.fetchall()

    currentquantity = data[0][0]
    currentquantity = currentquantity + quantity

    cursor.execute("update aCustomer_SharesOwned set pUnits = ? where cDematAccNo=? and pTicker = ?",
                   (currentquantity, cDematAccNo, Tickr))
    connectionu.commit()
    return

def watchlist(request):
    return render(request, 'addwatchlist.html')
def addToWatchlist(request):
    global connection
    connection = sqlite3.connect('PROJECT.db')
    cursor = connection.cursor()
    TickerWatched = request.GET['TickerWatched']
    cursor.execute("INSERT INTO aCustomer_SharesWatched values (?,?)", (dematAccNo, TickerWatched))
    connection.commit()
    s = TickerWatched+" has been added to Watchlist"
    cursor.close()
    connection.close()
    return render(request, 'addwatchlist.html',{'str':s})
def deleteWatchlist(request):
    connection2 = sqlite3.connect('PROJECT.db')
    cursor = connection2.cursor()
    TickerWatched = request.GET['TickerWatched']
    TickerWatched = TickerWatched.upper()
    ans=""
    cursor.execute("SELECT cTickerWatched FROM aCustomer_SharesWatched WHERE cTickerWatched = ?", (TickerWatched,))
    data = cursor.fetchall()
    if len(data) == 0:
        ans=ans+"There is no such stock in the watchlist"
    else:
        cursor.execute("DELETE FROM aCustomer_SharesWatched WHERE cDematAccNo = ? and cTickerWatched= ?",
                   (dematAccNo, TickerWatched))
        connection2.commit()
        ans = TickerWatched + " has been deleted to Watchlist"
    cursor.close()
    connection2.close()
    return render(request, 'addwatchlist.html', {'str2': ans})


def buy(request):
    return render(request,'buy.html')
def sell(request):
    return render(request, 'sell.html')
def buytranaction(request):
    connection7 = sqlite3.connect('PROJECT.db')
    cursor = connection7.cursor()
    stock = request.GET['stock']
    units = request.GET['units']
    name =  request.GET['name']
    cardno = request.GET['cardno']
    em = request.GET['em']
    ey = request.GET['ey']
    provider = request.GET['provider']
    today = date.today()
    value = abs(si.get_live_price(stock) * units)
    cursor.execute("insert into eTransactions values (NULL,?,?, ?,?,?,'buy',?)",
                       (dematAccNo, stock,units, today, value, cardno))
    connection7.commit()
    cursor.execute("select pTicker from aCustomer_SharesOwned where cDematAccNo = ? and pTicker = ?", (dematAccNo, stock))
    a = cursor.fetchall()
    if (len(a) == 0):
        addToPortfolio(dematAccNo, stock, units)
    else:
        updatePortfolio(dematAccNo, stock, units)
    #Expiry = em + "-" + em + "-01"
    #cursor.execute("INSERT INTO eCreditCard values (?,?,date(?),?)",
    #               (cardno, name, Expiry, provider))
    #connection7.commit()
    #cursor.execute('INSERT INTO rCustomerCCNo values (?,?)',(dematAccNo,cardno))
    #connection7.commit()

    addCard(dematAccNo, cardno, name, em, ey, provider)
    cursor.close()
    connection7.close()
    s="Transaction Successful"
    return render(request,'Buy.html',{'Confirm':s})

def signin(request):
    return render(request, 'sign_in.html')
def SignUp(request):
    connectionsign = sqlite3.connect('PROJECT.db')
    cursor = connectionsign.cursor()
    name=request.GET['Name']
    Email=request.GET['Email']
    Password=request.GET['Password']
    address=request.GET['Address']
    demataccNo=request.GET['DematAccNo']
    if len(demataccNo) != 16:
        return HttpResponse("Demat Account Number incorrect. Enter Again")
    dematAccType=request.GET['dematAccType']
    dob=request.GET['DoB']
    year = int(dob[:4])
    month = int(dob[5:7])
    day = int(dob[8:])
    d1 = date(year, month, day)
    d0 = date.today()
    delta = d1 - d0
    year = delta.days
    if year >= 18*365:
        return HttpResponse("Entry Restricted, You need to be 18 or above to have a account on this site")
    PAN=request.GET['PAN']
    if len(PAN) != 10:
        return HttpResponse("PAN Card Number incorrect. Enter Again")
    aadhar=request.GET['Aadhar']
    if len(aadhar) != 12:
        return HttpResponse("Aadhar Card Number incorrect. Enter Again")
    cursor.execute("INSERT INTO eCustomer values (?,?,?,?,?,?,?,?,date(?))",(demataccNo,name,Email,Password,address,PAN,aadhar,dematAccType,dob))
    connectionsign.commit()
    phNo = request.GET['phone']
    phoneno=[]
    for i in range(len(phNo)):
        if phNo[i] == ',':
            if len(phNo[:i]) == 10:
                phoneno.append(phNo[:i])
    if phNo[len(phNo)-10:len(phNo)] not in phoneno and len(phNo[len(phNo)-10:len(phNo)]) ==10:
        phoneno.append(phNo[len(phNo)-10:len(phNo)])
    for no in phoneno:
        cursor.execute("INSERT INTO aCustomer_PhoneNo values (?,?)",(demataccNo,no))
        connectionsign.commit()
    cursor.execute("SELECT * FROM eCustomer")
    connectionsign.commit()
    d = cursor.fetchall()
    return render(request, 'sign_in.html')

def login(request):
    global dematAccNo
    connectionslog = sqlite3.connect('PROJECT.db')
    cursor = connectionslog.cursor()
    emailid = request.GET['emailid']
    passwd = request.GET['passwd']
    cursor.execute("SELECT * FROM eCustomer")
    connectionslog.commit()
    d = cursor.fetchall()
    s=""
    for i in range(len(d)):
        if emailid == d[i][2] and passwd == d[i][3]:
            dematAccNo = d[i][0]
            return render(request,'dbmshome.html')
    s="Invalid Email/Password"
    return render(request,'sign_in.html', {'invalid': s})

def viewCards(dematAccNo):
    connectionvc = sqlite3.connect('PROJECT.db')
    cursor = connectionvc.cursor()
    cursor.execute("SELECT ccNo FROM rCustomerCCNo WHERE cDematAccNo = ?",(dematAccNo,))
    data = cursor.fetchall()
    if len(data)==0:
        return "No Cards Found"
    else:
        l = []
        for i in data:
            cursor.execute("SELECT ccNo from eCreditCard where ccNo = ", (i[0],))
            j = cursor.fetchall()
            l.append(j[0])
    return l[-1]

def addCard(dematAccNo,CardNo,NameOnCard,ExpiryMonth,ExpiryYear,Provider):
    connectioncard = sqlite3.connect('PROJECT.db')
    cursor = connectioncard.cursor()
    cursor.execute("SELECT * FROM rCustomerCCNo WHERE ccNo = ? and cDematAccNo = ?", (CardNo,dematAccNo))
    data = cursor.fetchall()
    if len(data) == 0:
        cursor.execute("select * from eCreditCard where ccNo = ?", (CardNo,))
        data = cursor.fetchall()
        if len(data) == 0:
            Expiry = ExpiryMonth +"-"+ExpiryYear+"-01"
            cursor.execute("INSERT INTO eCreditCard values (?,?,?,?)",(CardNo,NameOnCard,Expiry,Provider))
            connectioncard.commit()
        cursor.execute("Insert into rCustomerCCNo values (?,?)",(dematAccNo,CardNo))
        connectioncard.commit()
    return
def AddTransactions(cDematAccNo, Ticker, quantity,tDate):
    connectiont = sqlite3.connect('PROJECT.db')
    cursor = connectiont.cursor()
    value = abs(float(si.get_live_price(Ticker))*float(quantity))
    if float(quantity)>0:
        cursor.execute("insert into eTransactions values (NULL,?,?,?,?,'buy')",(cDematAccNo, Ticker, quantity,tDate))
    else:
        cursor.execute("insert into eTransactions values (NULL,?,?,?,?,'sell')",(cDematAccNo, Ticker, abs(quantity),tDate))
    connectiont.commit()
    ID = cursor.lastrowid
    cursor.execute("insert into aTransaction_Value values (?,?)",(ID,value))
    connectiont.commit()
    return ID


def addToPortfolio(cDematAccNo, Tickr, quantity):
    connectiona = sqlite3.connect('PROJECT.db')
    cursor = connectiona.cursor()
    cursor.execute("insert into aCustomer_SharesOwned values (?,?,?)", (cDematAccNo, Tickr, quantity))
    connectiona.commit()
    cursor.close()
    connectiona.close()
    return
def updatePortfolio(cDematAccNo, Tickr, quantity):
    connectionu = sqlite3.connect('PROJECT.db')
    cursor = connectionu.cursor()
    cursor.execute("select pUnits from aCustomer_SharesOwned where cDematAccNo = ? and pTicker =?", (cDematAccNo, Tickr))
    data = cursor.fetchall()

    currentquantity = data[0][0]
    currentquantity = float(currentquantity)
    currentquantity = currentquantity + float(quantity)

    cursor.execute("update aCustomer_SharesOwned set pUnits = ? where cDematAccNo=? and pTicker = ?",
                   (currentquantity, cDematAccNo, Tickr))
    connectionu.commit()
    return
def addToRecurringOrder(cDematAccNo, roDate, roTicker, roType, roUnits):
    # dd-mm-yyyy
    connectionrr = sqlite3.connect('PROJECT.db')
    cursor = connectionrr.cursor()
    year = int(roDate[:4])
    month = int(roDate[5:7])
    day = int(roDate[8:])
    d1 = date(year, month, day)
    d0 = date.today()
    delta = d1 - d0
    noOfDays = delta.days
    roDate2 = str(year) + "-" + str(month).zfill(2) + "-" + str(day).zfill(2)
    ID = cursor.lastrowid
    if noOfDays > 0:
        cursor.execute("INSERT INTO eReccuringOrder values(?,?,date(?),?,?,?)",
                       (ID,cDematAccNo, roDate2, roTicker, roType, roUnits))
        connectionrr.commit()
        return
    else:
        print("invalid date pls select future date")

def watchlist(request):
    return render(request, 'addwatchlist.html')
def addToWatchlist(request):
    global connection
    connection = sqlite3.connect('PROJECT.db')
    cursor = connection.cursor()
    TickerWatched = request.GET['TickerWatched']
    cursor.execute("SELECT cTickerWatched FROM aCustomer_SharesWatched WHERE cTickerWatched = ? and cDematAccNo = ?", (TickerWatched,dematAccNo))
    data = cursor.fetchall()
    if len(data) == 0:
        cursor.execute("INSERT INTO aCustomer_SharesWatched values (?,?)", (dematAccNo, TickerWatched))

    else:
        return HttpResponse("This Stock has already been added to your watchlist")
    connection.commit()
    s = TickerWatched+" has been added to your Watchlist"
    cursor.close()
    connection.close()
    return render(request, 'addwatchlist.html',{'str':s})
def deleteWatchlist(request):
    connection2 = sqlite3.connect('PROJECT.db')
    cursor = connection2.cursor()
    TickerWatched = request.GET['TickerWatched']
    TickerWatched = TickerWatched.upper()
    ans=""
    cursor.execute("SELECT cTickerWatched FROM aCustomer_SharesWatched WHERE cTickerWatched = ? and cDematAccNo = ?", (TickerWatched,dematAccNo))
    data = cursor.fetchall()
    if len(data) == 0:
        ans=ans+"There is no such stock in the watchlist"

    else:
        cursor.execute("DELETE FROM aCustomer_SharesWatched WHERE cDematAccNo = ? and cTickerWatched= ?",
                   (dematAccNo, TickerWatched))
        connection2.commit()
        ans = TickerWatched + " has been deleted from your Watchlist"
    cursor.close()
    connection2.close()
    return render(request, 'addwatchlist.html', {'str2': ans})
def printWatchlist(request):
    connection3 = sqlite3.connect('PROJECT.db')
    cursor = connection3.cursor()
    s="Your Shares Watched"
    cursor.execute("SELECT * FROM aCustomer_SharesWatched WHERE cDematAccNo = ?", (dematAccNo,))
    d = cursor.fetchall()
    data = []

    for i in d:
        j = list(i)
        imgurl = str(yf.Ticker(j[1]).info['logo_url'])
        j.append(imgurl)
        data.append(j)
    connection3.close()
    return render(request, 'dbmshome.html', {'str3': s,'table':data})

def buy(request):
    return render(request,'buy.html')
def buytranaction(request):
    connection7 = sqlite3.connect("PROJECT.db")
    cursor = connection7.cursor()
    stock = request.GET['stock']
    units = request.GET['units']
    name = request.GET['name']
    cardno = request.GET['cardno']
    if len(cardno) != 16:
        return HttpResponse('Card No entered is wrong')
    em = request.GET['em']
    ey = request.GET['ey']
    provider = request.GET['provider']
    year = "20"+ey
    year = int(year)
    month = int(em)
    day = int('01')
    expiry = date(year,month,day)
    datetoday = date.today()
    d = expiry - datetoday
    dd = d.days
    if dd <= 0:
        return HttpResponse("The Card Has Passed its Expiry Date.Enter Another Card")
    ID = AddTransactions(dematAccNo, stock, units,datetoday)
    cursor.execute("SELECT * FROM rCustomerCCNo WHERE ccNo = ? and cDematAccNo = ?", (cardno,dematAccNo))
    data = cursor.fetchall()
    if len(data) == 0:
        addCard(dematAccNo, cardno, name, em, ey, provider)
    cursor.execute("insert into rTransactionCCNo values(?,?)", (ID, cardno))
    connection7.commit()
    cursor.execute("select pTicker from aCustomer_SharesOwned where cDematAccNo = ? and pTicker = ?", (dematAccNo, stock))
    a = cursor.fetchall()
    if len(a) == 0:
        addToPortfolio(dematAccNo, stock, units)
    else:
        updatePortfolio(dematAccNo, stock, units)
    cursor.close()

    connection7.close()
    s = "Transaction Successful"
    return render(request,'PaymentSuccessful.html',{'Confirm':s})

def sell(request):
    return render (request,'sell.html')
def selltransacion(request):
    connection8 = sqlite3.connect('PROJECT.db')
    cursor = connection8.cursor()
    Ticker = request.GET['stock1']
    quantity = request.GET['units1']
    account = request.GET['accountno']
    cursor.execute("select pUnits from aCustomer_SharesOwned where cDematAccNo = ? and pTicker = ?", (dematAccNo, Ticker))
    a = cursor.fetchall()
    if (len(a) == 0):
        return HttpResponse("you dont own any quantity of these shares")
    elif (int(a[0][0]) < int(quantity)):
        return HttpResponse("quantity exceeded. Retry")
    else:
        datetoday = date.today()
        AddTransactions(dematAccNo, Ticker, float(quantity) * -1,datetoday)
        updatePortfolio(dematAccNo, Ticker, float(quantity) * -1)
    cursor.close()
    connection8.close()
    s = "Transaction Successfull"
    t = f"The Money will be deposited in  account no {account} within two working days"
    return render(request, 'PaymentSuccessful.html', {'Confirm2': s,'Confirm3':t})

def ViewTransactions(request):
    connection9 = sqlite3.connect('PROJECT.db')
    cursor = connection9.cursor()
    s = "Your Transaction History"
    cursor.execute("SELECT * FROM eTransactions WHERE cDematAccNo = ?", (dematAccNo,))
    d = cursor.fetchall()
    data = []
    for elem in d:
        temp = list(elem)
        cursor.execute("SELECT * from aTransaction_Value where tID = ?", (temp[0],))
        imgurl = yf.Ticker(elem[2]).info['logo_url']
        d2 = cursor.fetchall()
        val = round(d2[0][1],2)
        temp.append(val)
        temp.append(imgurl)
        data.append(temp)

    cursor.close()
    connection9.close()
    return render(request,'dbmshome.html',{"Title":s,"ans":data})
def ViewPortfolio(request):
    connection10 = sqlite3.connect('PROJECT.db')
    cursor = connection10.cursor()
    s = "Your Portfolio"
    cursor.execute("SELECT * FROM aCustomer_SharesOwned WHERE cDematAccNo = ?", (dematAccNo,))
    d = cursor.fetchall()
    data = []
    for elem in d:
        a = list(elem)
        imgurl = yf.Ticker(elem[1]).info['logo_url']
        a.append(imgurl)
        data.append(a)

    cursor.close()
    connection10.close()
    return render(request, 'dbmshome.html', {"Title2": s, "ans2": data})
def ViewCards(request):
    connection11 = sqlite3.connect('PROJECT.db')
    cursor = connection11.cursor()
    s = "Your Cards Used"
    cursor.execute("SELECT * FROM rCustomerCCNo WHERE cDematAccNo = ?", (dematAccNo,))
    d = cursor.fetchall()
    data = []
    for elem in d:
        cursor.execute("SELECT * FROM eCreditCard WHERE ccNo = ?", (elem[1],))
        d2 = cursor.fetchall()
        data.append(list(d2[0]))
    cursor.close()
    connection11.close()
    return render(request, 'dbmshome.html', {"Title3": s, "ans3": data})

def reccuring(request):
    return render(request,'recurringoder.html')
def recurringorder(request):
    connection12 = sqlite3.connect('PROJECT.db')
    cursor = connection12.cursor()
    global ticker
    ticker = request.GET['stock2']
    global quan
    quan = request.GET['units2']
    global tpyee
    typee = request.GET['Buy/Sell']
    global datee
    datee = request.GET['Date']
    year = int(datee[:4])
    month = int(datee[5:7])
    day = int(datee[8:])
    d1 = date(year, month, day)
    d0 = date.today()
    delta = d1 - d0
    d = delta.days
    if d <= 0:
        return HttpResponse("Invalid Date, Please Enter a future date")
    if typee == 'sell':
        cursor.execute("select pUnits from aCustomer_SharesOwned where cDematAccNo = ? and pTicker = ?",
                   (dematAccNo, ticker))
        a = cursor.fetchall()
        if (len(a) == 0):
            return HttpResponse("you dont own any quantity of these shares")
        elif (int(a[0][0])< int(quan)):
            return HttpResponse("quantity exceeded. Retry")

        else:
            addToRecurringOrder(dematAccNo,datee,ticker,typee,quan)
    else:
        addToRecurringOrder(dematAccNo, datee, ticker, typee, quan)
    s = f"The Stock will be bought/sold on {datee}"
    return render(request,'PaymentSuccessful.html',{'Confirm4':s})
def viewReccuringOrder():
    connectionvr = sqlite3.connect('PROJECT.db')
    cursor = connectionvr.cursor()
    cursor.execute('Select * from eReccuringOrder where cDematAccNo = ?',(dematAccNo,))
    data = cursor.fetchall()
    for i in range(len(data)):
        datecurrent = data[i][2]
        year = int(datecurrent[:4])
        month = int(datecurrent[5:7])
        day = int(datecurrent[8:])
        d1 = date(year, month, day)
        d0 = date.today()
        delta = d1 - d0
        noOfDays = delta.days
        if noOfDays <= 0:
            cursor.execute('Select tID from eTransactions where cDematAccNo = ? and tType = "buy"', (data[i][1],))
            data2 = cursor.fetchall()

            cursor.execute('Select ccNo from rTransactionCCNo where tID = ?', data2[-1])
            data2 = cursor.fetchall()

            if data[i][4].lower() == "buy":

                value = abs(si.get_live_price(data[i][3]) * data[i][5])
                cursor.execute("insert into eTransactions values (NULL,?,?,?,?,'buy')",
                               (data[i][1], data[i][3], data[i][5], data[i][2]))
                connectionvr.commit()
                ID = cursor.lastrowid
                cursor.execute("insert into aTransaction_Value values (?,?)", (ID, value))
                cursor.execute("insert into rTransactionCCNo values(?,?)", (ID, data2[0][0]))
                connectionvr.commit()

                cursor.execute("select pUnits from aCustomer_SharesOwned where cDematAccNo = ? and pTicker = ?",
                               (data[i][1], data[i][3]))
                a = cursor.fetchall()
                if (len(a) == 0):
                    cursor.execute("insert into aCustomer_SharesOwned values (?,?,?)", (data[i][1], data[i][3], data[i][5]))
                    connectionvr.commit()
                else:

                    currentquantity = int(a[0][0])
                    currentquantity = currentquantity + data[i][5]

                    cursor.execute("update aCustomer_SharesOwned set pUnits = ? where cDematAccNo=? and pTicker = ?",
                                   (currentquantity, data[i][1], data[i][3]))
                    connectionvr.commit()

                    cursor.execute('delete from eReccuringOrder where roID = ? and cDematAccNo = ?', (data[i][0],dematAccNo))
                    connectionvr.commit()


            else:
                cursor.execute("select pUnits from aCustomer_SharesOwned where cDematAccNo = ? and pTicker = ?",
                               (data[i][1], data[i][3]))
                a = cursor.fetchall()

                if (len(a) == 0):
                    return HttpResponse("you dont own any quantity of these shares")
                elif (int(a[0][0]) < int(quan)):
                    return HttpResponse("quantity exceeded. Retry")

                else:

                    value = abs(si.get_live_price(data[i][3]) * data[i][5])
                    cursor.execute("insert into eTransactions values (NULL,?,?,?,?,'sell')",
                                   (data[i][1], data[i][3], data[i][5], data[i][2]))
                    connection.commit()
                    ID = cursor.lastrowid
                    cursor.execute("insert into aTransaction_Value values (?,?)", (ID, value))

                    currentquantity = int(a[0][0])
                    currentquantity = currentquantity - data[i][5]

                    cursor.execute("update aCustomer_SharesOwned set pUnits = ? where cDematAccNo=? and pTicker = ?",
                                   (currentquantity, data[i][1], data[i][3]))
                    connectionvr.commit()

                    cursor.execute('delete from eReccuringOrder where roID = ? and cDematAccNo = ?', (data[i][0],dematAccNo))
                    connectionvr.commit()
def viewreccuring(request):
    viewReccuringOrder()
    connection13 = sqlite3.connect('PROJECT.db')
    cursor = connection13.cursor()
    cursor.execute('Select * from eReccuringOrder where cDematAccNo=?',(dematAccNo,))
    d = cursor.fetchall()
    data = []
    for elem in d:
        a = list(elem)
        imgurl = yf.Ticker(elem[3   ]).info['logo_url']
        a.append(imgurl)
        data.append(a)
    cursor.close()
    connection13.close()
    s = "Pending recurring orders"
    return render(request, 'dbmshome.html',{'aans':data,'Title4':s})

def Custsupport(request):
    return render(request,'CustomerSupport.html')
def Custsupportdetails(request):
    connection12 = sqlite3.connect('PROJECT.db')
    cursor = connection12.cursor()
    city = request.GET['City']
    cursor.execute("select * from eCustSupport where csRegion = ?", (city,))
    d1 = cursor.fetchall()
    cursor.execute("select * from aCustSupport_Address where csRegion = ?", (city,))
    d2 = cursor.fetchall()
    cursor.execute('SELECT * from aCustSupport_Phone where csRegion = ?', (city,))
    d3 = cursor.fetchall()
    s = "City"
    ss = "E-Mail:"
    sss = "Addresses"
    ssss = "Phone numbers"
    if (len(d1) == 0 or len(d2) == 0 or len(d3) == 0):
        a = str(len(d1))
        b = str(len(d2))
        c = str(len(d3))
        return HttpResponse("Support not available")
    else:
        l = list(d1[0])
        l2 = []
        l3 = []
        for i in range(len(d2)):
            a = d2[i]
            l2.append(a[1])
        for i in range(len(d3)):
            a = d3[i]
            l3.append(a[1])
        l.append(l2)
        l.append(l3)
        return render(request, 'CustomerSupport.html',
                      {'City': l[0], 'Gmail': l[1], 'Address': l[2], 'Phone': l[3], 'city': s, 'mail': ss,
                       'address': sss, 'phone': ssss})

