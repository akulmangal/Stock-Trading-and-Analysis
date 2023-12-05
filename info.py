import numpy as np
import pandas as pd
import yfinance as yf
from django.shortcuts import render
import yahoo_fin.stock_info as si
from django.shortcuts import HttpResponse
import plotly.graph_objects as go
from datetime import datetime
import plotly.express as px
from sklearn import metrics
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
import datetime
from datetime import date
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor

df = pd.read_csv('training_model.csv')
dff = df.head(20)
X = dff[["P/S", "P/BV", "P/E", "PEG"]].values
Y = dff['Confidence Score'].values
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=1)
regressor = RandomForestRegressor(n_estimators=89, random_state=1)
regressor.fit(X_train, Y_train)
y_pred = regressor.predict(X_test)
R_square = r2_score(Y_test, y_pred)
print('Mean Absolute Error:', metrics.mean_absolute_error(Y_test, y_pred))
print('Mean Squared Error:', metrics.mean_squared_error(Y_test, y_pred))
print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(Y_test, y_pred)))
print("R^2 = %.2f" % (R_square))

def getinfo(request):
    global user_input
    user_input = request.GET['user_input']
    user_input = user_input.upper()
    user_input = user_input + '.NS'
    temp = yf.Ticker(user_input).info
    sector = temp['sector']
    info = temp['longBusinessSummary']
    if 'trailingPE' in temp:
        pe = temp['trailingPE']
    else:
        pe = 0

    ps = temp['priceToSalesTrailing12Months']
    if ps is None:
        ps = 0
    pbv = temp['priceToBook']
    if pbv is None:
        pbv = 0
    growth = temp['earningsQuarterlyGrowth']
    if growth is None:
        growth = 0
    if growth == 0:
        peg = 0
    else:
        peg = (pe / growth) / 100

    liveprice = si.get_live_price(user_input)
    liveprice = round(liveprice, 2)
    previousclose = temp['previousClose']
    growth = liveprice - previousclose
    growth = round(growth, 2)
    percentagegrowth = (growth / previousclose) * 100
    percentagegrowth = round(percentagegrowth, 2)
    imageurl = temp['logo_url']
    if growth > 0:
        arrow = "↑"
        growth2 = "+" + str(growth)
        percentagegrowth2 = "(+" + str(percentagegrowth) +"%)"
    elif growth < 0:
        arrow = "↓"
        percentagegrowth2 = "("+ str(percentagegrowth) + "%)"
        growth2 = str(growth)
    else:
        arrow = ""
        percentagegrowth2 = "unch"
        growth2 = ""
    marketstatus = si.get_market_status()
    prediction = regressor.predict([[ps, pbv, pe, peg]])
    return render(request, 'result.html',
                  {'Company': user_input, 'company_info': info, 'Sector': sector, 'PE': round(pe,2),
                   'PS': round(ps, 2), 'PBV': round(pbv, 2), 'PEG': round(peg, 2),
                   'Prediction': round(prediction[0], 3), 'lp': liveprice, 'ms': marketstatus, 'growth': growth2,
                   'percentage': percentagegrowth2, 'arrow': arrow, 'image': imageurl})
def predict(request):
    temp = yf.Ticker(user_input).info
    liveprice = si.get_live_price(user_input)
    liveprice = round(liveprice, 2)
    previousclose = temp['previousClose']
    growth = liveprice - previousclose
    growth = round(growth, 2)
    percentagegrowth = (growth / previousclose) * 100
    percentagegrowth = round(percentagegrowth, 2)
    imageurl = temp['logo_url']
    if growth > 0:
        arrow = "↑"
        growth2 = "+" + str(growth)
        percentagegrowth2 = "(+" + str(percentagegrowth) + "%)"
    elif growth < 0:
        arrow = "↓"
        percentagegrowth2 = "(" + str(percentagegrowth) + "%)"
        growth2 = str(growth)
    else:
        arrow = ""
        percentagegrowth2 = "unch"
        growth2 = ""

    marketstatus = si.get_market_status()
    return render(request, 'pricepredictions.html',{'lp': liveprice, 'ms': marketstatus, 'growth': growth2,
                   'percentage': percentagegrowth2, 'arrow': arrow, 'image': imageurl,'Company':user_input})
def summary(request):
    quote_table =si.get_stats_valuation(user_input)
    df = pd.DataFrame.from_dict(quote_table)
    df = df.rename(columns={0:'Topics'})
    df = df.rename(columns={1:'Value'})
    df = df.set_index("Topics")
    df.index.name = None
    table = df.to_html()
    temp = yf.Ticker(user_input).info
    liveprice = si.get_live_price(user_input)
    liveprice = round(liveprice, 2)
    previousclose = temp['previousClose']
    growth = liveprice - previousclose
    growth = round(growth, 2)
    percentagegrowth = (growth / previousclose) * 100
    percentagegrowth = round(percentagegrowth, 2)
    imageurl = temp['logo_url']
    if growth > 0:
        arrow = "↑"
        growth2 = "+" + str(growth)
        percentagegrowth2 = "(+" + str(percentagegrowth) + "%)"
    elif growth < 0:
        arrow = "↓"
        percentagegrowth2 = "(" + str(percentagegrowth) + "%)"
        growth2 = str(growth)
    else:
        arrow = ""
        percentagegrowth2 = "unch"
        growth2 = ""

    marketstatus = si.get_market_status()
    return render(request,'homepage.html',{'answer':table,'ticker':user_input,'lp':liveprice,'ms':marketstatus,'growth':growth2,'percentage':percentagegrowth2,'arrow':arrow,'image':imageurl})

def historical(request):
    temp = yf.Ticker(user_input).history(period="max")
    temp.drop(['Dividends','Stock Splits'],inplace=True,axis=1)
    columns = temp.shape[0]
    df = temp.head(columns)
    df = df.iloc[::-1]
    df = df.round(decimals = 2)
    df.index.name = None
    table2 = df.to_html()
    temp = yf.Ticker(user_input).info
    liveprice = si.get_live_price(user_input)
    liveprice = round(liveprice, 2)
    previousclose = temp['previousClose']
    growth = liveprice - previousclose
    growth = round(growth, 2)
    percentagegrowth = (growth / previousclose) * 100
    percentagegrowth = round(percentagegrowth, 2)
    imageurl = temp['logo_url']
    if growth > 0:
        arrow = "↑"
        growth2 = "+" + str(growth)
        percentagegrowth2 = "(+" + str(percentagegrowth) + "%)"
    elif growth < 0:
        arrow = "↓"
        percentagegrowth2 = "(" + str(percentagegrowth) + "%)"
        growth2 = str(growth)
    else:
        arrow = ""
        percentagegrowth2 = "unch"
        growth2 = ""

    marketstatus = si.get_market_status()
    return render(request, 'Historical_Data.html', {'answer2': table2,'ticker':user_input,'lp':liveprice,'ms':marketstatus,'growth':growth2,'percentage':percentagegrowth2,'arrow':arrow,'image':imageurl})

def incomesheet(request):
    temp = si.get_financials(user_input, yearly = True, quarterly = False)
    df = temp['yearly_income_statement']
    df.columns = df.columns.astype(str)
    df = df.divide(10000000, axis=0)
    df.index.name = None
    df.rename(columns = {"endDate" : "Particulars"}, inplace = True)
    table3 = df.to_html()
    temp = yf.Ticker(user_input).info
    liveprice = si.get_live_price(user_input)
    liveprice = round(liveprice, 2)
    previousclose = temp['previousClose']
    growth = liveprice - previousclose
    growth = round(growth, 2)
    percentagegrowth = (growth / previousclose) * 100
    percentagegrowth = round(percentagegrowth, 2)
    imageurl = temp['logo_url']
    if growth > 0:
        arrow = "↑"
        growth2 = "+" + str(growth)
        percentagegrowth2 = "(+" + str(percentagegrowth) + "%)"
    elif growth < 0:
        arrow = "↓"
        percentagegrowth2 = "(" + str(percentagegrowth) + "%)"
        growth2 = str(growth)
    else:
        arrow = ""
        percentagegrowth2 = "unch"
        growth2 = ""

    marketstatus = si.get_market_status()
    return render(request, 'Income_Statement.html', {'answer3': table3,'ticker':user_input,'lp':liveprice,'ms':marketstatus,'growth':growth2,'percentage':percentagegrowth2,'arrow':arrow,'image':imageurl})

def balancesheet(request):
    temp = si.get_financials(user_input, yearly=True, quarterly=False)
    df = temp['yearly_balance_sheet']
    df.columns = df.columns.astype(str)
    df = df.divide(10000000, axis=0)
    df.index.name = None
    table4 = df.to_html()
    temp = yf.Ticker(user_input).info
    liveprice = si.get_live_price(user_input)
    liveprice = round(liveprice, 2)
    previousclose = temp['previousClose']
    growth = liveprice - previousclose
    growth = round(growth, 2)
    percentagegrowth = (growth / previousclose) * 100
    percentagegrowth = round(percentagegrowth, 2)
    imageurl = temp['logo_url']
    if growth > 0:
        arrow = "↑"
        growth2 = "+" + str(growth)
        percentagegrowth2 = "(+" + str(percentagegrowth) + "%)"
    elif growth < 0:
        arrow = "↓"
        percentagegrowth2 = "(" + str(percentagegrowth) + "%)"
        growth2 = str(growth)
    else:
        arrow = ""
        percentagegrowth2 = "unch"
        growth2 = ""

    marketstatus = si.get_market_status()
    return render(request, 'balancesheet.html', {'answer4': table4,'ticker':user_input,'lp':liveprice,'ms':marketstatus,'growth':growth2,'percentage':percentagegrowth2,'arrow':arrow,'image':imageurl})

def cashflow(request):
    temp = si.get_financials(user_input, yearly=True, quarterly=False)
    df= temp['yearly_cash_flow']
    df.columns = df.columns.astype(str)
    df = df.divide(10000000, axis=0)
    df.index.name = None
    table4 = df.to_html()
    temp = yf.Ticker(user_input).info
    liveprice = si.get_live_price(user_input)
    liveprice = round(liveprice, 2)
    previousclose = temp['previousClose']
    growth = liveprice - previousclose
    growth = round(growth, 2)
    percentagegrowth = (growth / previousclose) * 100
    percentagegrowth = round(percentagegrowth, 2)
    imageurl = temp['logo_url']
    if growth > 0:
        arrow = "↑"
        growth2 = "+" + str(growth)
        percentagegrowth2 = "(+" + str(percentagegrowth) + "%)"
    elif growth < 0:
        arrow = "↓"
        percentagegrowth2 = "(" + str(percentagegrowth) + "%)"
        growth2 = str(growth)
    else:
        arrow = ""
        percentagegrowth2 = "unch"
        growth2 = ""

    marketstatus = si.get_market_status()
    return render(request, 'cashflow.html', {'answer5': table4,'ticker':user_input,'lp':liveprice,'ms':marketstatus,'growth':growth2,'percentage':percentagegrowth2,'arrow':arrow,'image':imageurl})


def candlesticks(request):
    df = yf.Ticker(user_input).history(period='1y')
    df.drop(columns=['Volume', 'Dividends', 'Stock Splits'], inplace=True)
    df.reset_index(inplace=True)
    fig = go.Figure(
        data=[go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    df.set_index('Date', inplace=True)
    fig.update_layout(
        title="Candlestick Chart:",
        xaxis_title="Date",
        yaxis_title="Price",
        font=dict(
            family="Montserrat, Sans-serif",
            size=14,
            color="black"
        )
    )
    ans = fig.to_html(default_height = '1000px',config=dict(displayModeBar=False))
    temp = yf.Ticker(user_input).info
    liveprice = si.get_live_price(user_input)
    liveprice = round(liveprice, 2)
    previousclose = temp['previousClose']
    growth = liveprice - previousclose
    growth = round(growth, 2)
    percentagegrowth = (growth / previousclose) * 100
    percentagegrowth = round(percentagegrowth, 2)
    imageurl = temp['logo_url']
    if growth > 0:
        arrow = "↑"
        growth2 = "+" + str(growth)
        percentagegrowth2 = "(+" + str(percentagegrowth) + "%)"
    elif growth < 0:
        arrow = "↓"
        percentagegrowth2 = "(" + str(percentagegrowth) + "%)"
        growth2 = str(growth)
    else:
        arrow = ""
        percentagegrowth2 = "unch"
        growth2 = ""

    marketstatus = si.get_market_status()
    return render(request,"candlesticks.html",{'graph1':ans,'ticker':user_input, 'lp': liveprice,
                   'ms': marketstatus, 'growth': growth2,
                   'percentage': percentagegrowth2, 'arrow': arrow, 'image': imageurl})

def fivedaymovingdayaverage(request):
    df = yf.Ticker(user_input).history(period='max')
    df.drop(columns=['Volume', 'Dividends', 'Stock Splits'], inplace=True)
    n = 5
    import datetime
    dt = datetime.datetime.today()
    date = datetime.datetime(year=dt.year - 1, month=dt.month, day=dt.day)

    ent = len(df.loc[df.index > date])
    ent += n
    ent -= (2 * ent)
    df = df.iloc[ent:]

    df.reset_index(inplace=True)

    nDayMovingAvg = []
    for i in range(n - 1):
        nDayMovingAvg.append(0)

    for i in range(n - 1, len(df), 1):
        temp = 0
        for j in range(n):
            temp += df.loc[(i - j), 'Close']
        temp /= n
        nDayMovingAvg.append(temp)

    df['5-Day Moving average'] = nDayMovingAvg

    df = df.iloc[n:]

    fig = px.line(df, x="Date", y="5-Day Moving average", title='5-Day Moving average')
    df.set_index('Date', inplace=True)
    ansfive = fig.to_html()



    n = 8

    import datetime
    dt = datetime.datetime.today()
    date = datetime.datetime(year=dt.year - 1, month=dt.month, day=dt.day)

    ent = len(df.loc[df.index > date])
    ent += n
    ent -= (2 * ent)
    df = df.iloc[ent:]

    df.reset_index(inplace=True)

    nDayMovingAvg = []
    for i in range(n - 1):
        nDayMovingAvg.append(0)

    for i in range(n - 1, len(df), 1):
        temp = 0
        for j in range(n):
            temp += df.loc[(i - j), 'Close']
        temp /= n
        nDayMovingAvg.append(temp)

    df['8-Day Moving average'] = nDayMovingAvg

    df = df.iloc[n:]

    fig = px.line(df, x="Date", y="8-Day Moving average", title='8-Day Moving average')
    df.set_index('Date', inplace=True)
    anseight = fig.to_html()

    n = 13

    import datetime
    dt = datetime.datetime.today()
    date = datetime.datetime(year=dt.year - 1, month=dt.month, day=dt.day)

    ent = len(df.loc[df.index > date])
    ent += n
    ent -= (2 * ent)
    df = df.iloc[ent:]

    df.reset_index(inplace=True)

    nDayMovingAvg = []
    for i in range(n - 1):
        nDayMovingAvg.append(0)

    for i in range(n - 1, len(df), 1):
        temp = 0
        for j in range(n):
            temp += df.loc[(i - j), 'Close']
        temp /= n
        nDayMovingAvg.append(temp)

    df['13-Day Moving average'] = nDayMovingAvg

    df = df.iloc[n:]

    fig = px.line(df, x="Date", y="13-Day Moving average", title='13-Day Moving average')
    df.set_index('Date', inplace=True)
    ansthirteen = fig.to_html()

    n = 30

    import datetime
    dt = datetime.datetime.today()
    date = datetime.datetime(year=dt.year - 1, month=dt.month, day=dt.day)

    ent = len(df.loc[df.index > date])
    ent += n
    ent -= (2 * ent)
    df = df.iloc[ent:]

    df.reset_index(inplace=True)

    nDayMovingAvg = []
    for i in range(n - 1):
        nDayMovingAvg.append(0)

    for i in range(n - 1, len(df), 1):
        temp = 0
        for j in range(n):
            temp += df.loc[(i - j), 'Close']
        temp /= n
        nDayMovingAvg.append(temp)

    df['30-Day Moving average'] = nDayMovingAvg

    df = df.iloc[n:]

    fig = px.line(df, x="Date", y="30-Day Moving average", title='30-Day Moving average')
    df.set_index('Date', inplace=True)
    ansth= fig.to_html()

    temp = yf.Ticker(user_input).info
    liveprice = si.get_live_price(user_input)
    liveprice = round(liveprice, 2)
    previousclose = temp['previousClose']
    growth = liveprice - previousclose
    growth = round(growth, 2)
    percentagegrowth = (growth / previousclose) * 100
    percentagegrowth = round(percentagegrowth, 2)
    imageurl = temp['logo_url']
    if growth > 0:
        arrow = "↑"
        growth2 = "+" + str(growth)
        percentagegrowth2 = "(+" + str(percentagegrowth) + "%)"
    elif growth < 0:
        arrow = "↓"
        percentagegrowth2 = "(" + str(percentagegrowth) + "%)"
        growth2 = str(growth)
    else:
        arrow = ""
        percentagegrowth2 = "unch"
        growth2 = ""

    marketstatus = si.get_market_status()
    return render(request, "movingdayaverage.html", {'g':ansth,'graph3': anseight,'ticker':user_input,'graph2':ansfive,'graph4':ansthirteen, 'lp': liveprice, 'ms': marketstatus, 'growth': growth2,
                   'percentage': percentagegrowth2, 'arrow': arrow, 'image': imageurl})

def pricepredictions(request):
    is_private = request.GET['is_private']
    years = is_private[:4]
    years = int(years)
    months = is_private[5:7]
    months = int(months)
    days = is_private[8:]
    days = int(days)
    x = datetime.datetime.now()
    yyear = int(x.year)
    mmonth = int(x.month)
    dday = int(x.day)
    d0 = date(yyear, mmonth, dday)
    d1 = date(years, months, days)
    delta = d1 - d0
    future_days = delta.days
    if future_days < 0:
        return HttpResponse("Invalid Date <br> Enter the correct date")
    temp = yf.Ticker(user_input).history(period="max")
    df = temp
    dff = df[['Close']]
    dfff = df[['High']]
    dffff = df[['Low']]
    dfffff = df[['Open']]
    dff['Prediction'] = dff[['Close']].shift(-future_days)
    dfff['Prediction'] = dfff[['High']].shift(-future_days)
    dffff['Prediction'] = dffff[['Low']].shift(-future_days)
    dfffff['Prediction'] = dfffff[['Open']].shift(-future_days)
    X = np.array(dff.drop(['Prediction'], 1))[:-future_days]
    XX = np.array(dfff.drop(['Prediction'], 1))[:-future_days]
    XXX = np.array(dffff.drop(['Prediction'], 1))[:-future_days]
    XXXX = np.array(dfffff.drop(['Prediction'], 1))[:-future_days]
    y = np.array(dff['Prediction'])[:-future_days]
    yy = np.array(dfff['Prediction'])[:-future_days]
    yyy = np.array(dffff['Prediction'])[:-future_days]
    yyyy = np.array(dfffff['Prediction'])[:-future_days]
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.25)
    xx_train, xx_test, yy_train, yy_test = train_test_split(XX, yy, test_size=0.25)
    xxx_train, xxx_test, yyy_train, yyy_test = train_test_split(XXX, yyy, test_size=0.25)
    xxxx_train, xxxx_test, yyyy_train, yyyy_test = train_test_split(XXXX, yyyy, test_size=0.25)
    tree = DecisionTreeRegressor()
    tree1 = DecisionTreeRegressor()
    tree2 = DecisionTreeRegressor()
    tree3 = DecisionTreeRegressor()
    tree.fit(x_train, y_train)
    tree1.fit(xx_train, yy_train)
    tree2.fit(xxx_train, yyy_train)
    tree3.fit(xxxx_train, yyyy_train)
    predictions = tree.predict(x_test)
    predictions1 = tree1.predict(xx_test)
    predictions2 = tree2.predict(xxx_test)
    predictions3 = tree3.predict(xxxx_test)
    R_square = r2_score(y_test, predictions)
    R_square1 = r2_score(yy_test, predictions1)
    R_square2 = r2_score(yyy_test, predictions2)
    R_square3 = r2_score(yyyy_test, predictions3)
    print("R^2 of closing price = %.2f" % (R_square))
    print("R^2 of High price= %.2f" % (R_square1))
    print("R^2 of Low price= %.2f" % (R_square2))
    print("R^2 of opening price= %.2f" % (R_square3))
    x_future = dff.drop(['Prediction'], 1)[:-future_days]
    x_future = x_future.tail(future_days)
    x_future = np.array(x_future)

    xx_future = dfff.drop(['Prediction'], 1)[:-future_days]
    xx_future = xx_future.tail(future_days)
    xx_future = np.array(xx_future)

    xxx_future = dffff.drop(['Prediction'], 1)[:-future_days]
    xxx_future = xxx_future.tail(future_days)
    xxx_future = np.array(xxx_future)

    xxxx_future = dfffff.drop(['Prediction'], 1)[:-future_days]
    xxxx_future = xxxx_future.tail(future_days)
    xxxx_future = np.array(xxxx_future)

    predict = tree.predict(x_future)
    predict1 = tree1.predict(xx_future)
    predict2 = tree2.predict(xxx_future)
    predict3 = tree3.predict(xxxx_future)
    for i in range(len(predict)):
        if predict[i] < predict2[i]:
            predict[i] = predict2[i]
        if predict2[i] > predict3[i]:
            predict2[i] = predict3[i]
        if predict3[i] > predict1[i]:
            predict1[i] = predict3[i]
        if predict[i] > predict1[i]:
            predict1[i] = predict[i]

    print("Predicted opening price= %.2f" % (predict3[0]))
    print("Predicted High price= %.2f" % (predict1[0]))
    print("Predicted Low price= %.2f" % (predict2[0]))
    print("Predicted closing price = %.2f" % (predict[0]))
    temp = yf.Ticker(user_input).info
    liveprice = si.get_live_price(user_input)
    liveprice = round(liveprice, 2)
    previousclose = temp['previousClose']
    growth = liveprice - previousclose
    growth = round(growth, 2)
    percentagegrowth = (growth / previousclose) * 100
    percentagegrowth = round(percentagegrowth, 2)
    imageurl = temp['logo_url']
    if growth > 0:
        arrow = "↑"
        growth2 = "+" + str(growth)
        percentagegrowth2 = "(+" + str(percentagegrowth) + "%)"
    elif growth < 0:
        arrow = "↓"
        percentagegrowth2 = "(" + str(percentagegrowth) + "%)"
        growth2 = str(growth)
    else:
        arrow = ""
        percentagegrowth2 = "unch"
        growth2 = ""
    dates=[]
    for i in range(1,future_days+1):
        dates.append(i)

    predict33 =predict3[::-1]
    predict22 = predict2[::-1]
    predict11 = predict1[::-1]
    predict00 = predict[::-1]
    fig = go.Figure(
        data=[go.Candlestick(x=dates, open=predict33, high=predict11, low=predict22, close=predict00)])
    fig.update_layout(
        title="Candlestick Chart:",
        xaxis_title="Days",
        yaxis_title="Price",
        font=dict(
            family="Montserrat, Sans-serif",
            size=14,
            color="black"
        )
    )

    ans = fig.to_html()
    marketstatus = si.get_market_status()
    return render(request, "answer.html", {"Open":round(predict3[0],2),"High":round(predict1[0],2),"Low":round(predict2[0],2),"Close":round(predict[0],2),"Date":is_private,'ticker':user_input, 'lp': liveprice,'ms': marketstatus, 'growth': growth2,'percentage': percentagegrowth2, 'arrow': arrow, 'image': imageurl,'Graph':ans})


