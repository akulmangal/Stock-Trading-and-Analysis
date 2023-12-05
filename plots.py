from django.shortcuts import render
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf
import plotly.express as px
import yahoo_fin.stock_info as si


def candlesticks(request):
    user_input = request.GET['user_input']
    user_input = user_input.upper()
    user_input = user_input + '.NS'
    df = yf.Ticker(user_input).history(period='1y')
    df.drop(columns=['Volume', 'Dividends', 'Stock Splits'], inplace=True)

    df.reset_index(inplace=True)
    fig = go.Figure(
        data=[go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    df.set_index('Date', inplace=True)
    ans = fig.to_html()
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
    elif growth < 0:
        arrow = "↓"
    else:
        arrow = "-"

    marketstatus = si.get_market_status()
    return render(request,"candlesticks.html",{'graph1':ans,'ticker':user_input, 'lp': liveprice,
                   'ms': marketstatus, 'growth': growth,
                   'percentage': percentagegrowth, 'arrow': arrow, 'image': imageurl})

def fivedaymovingdayaverage(request):
    user_input = request.GET['user_input']
    user_input = user_input.upper()
    user_input = user_input + '.NS'
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
    elif growth < 0:
        arrow = "↓"
    else:
        arrow = "-"

    marketstatus = si.get_market_status()
    return render(request, "movingdayaverage.html", {'graph3': anseight,'ticker':user_input,'graph2':ansfive,'graph4':ansthirteen, 'lp': liveprice, 'ms': marketstatus, 'growth': growth,
                   'percentage': percentagegrowth, 'arrow': arrow, 'image': imageurl})