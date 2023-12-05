import numpy as np
import pandas as pd
import yfinance as yf
from django.shortcuts import render
import yahoo_fin.stock_info as si
from sklearn import metrics
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

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

def result(request):
    user_input = request.GET['user_input']
    user_input=user_input.upper()
    user_input=user_input+'.NS'
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

    liveprice=si.get_live_price(user_input)
    liveprice= round(liveprice, 2)
    previousclose = temp['previousClose']
    growth =liveprice - previousclose
    growth =round(growth,2)
    percentagegrowth = (growth/previousclose)*100
    percentagegrowth = round(percentagegrowth, 2)
    imageurl= temp['logo_url']
    growth2 = ""
    percentagegrowth2 = ""
    if growth > 0:
        arrow= "↑"
        growth2 = "+"+str(growth)
        percentagegrowth2 = "+"+str(percentagegrowth)
    elif growth < 0:
        arrow= "↓"
        growth2 = "-" + str(growth)
        percentagegrowth2 = "-" + str(percentagegrowth)
    else:
        arrow = "-"
        growth2 = "unch"
        percentagegrowth2 = ""

    marketstatus=si.get_market_status()
    prediction = regressor.predict([[ps, pbv, pe, peg]])
    return render(request, 'result.html',
                  {'Company':user_input,'company_info': info, 'Sector': sector, 'PE': pe, 'PS': ps, 'PBV': pbv, 'PEG': peg,
                   'Prediction': prediction[0],'lp':liveprice,'ms':marketstatus,'growth':growth2,'percentage':percentagegrowth2,'arrow':arrow,'image':imageurl})


