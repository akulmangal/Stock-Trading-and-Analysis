"""djangoProject1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from . import ml_model
from . import info
from . import plots
from . import databases

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('info/', info.getinfo, name='information'),
    path('summary/', info.summary,name="summary"),
    path('historical/', info.historical,name="historical"),
    path('incomestatement/', info.incomesheet,name="incomestatement"),
    path('balancesheet/', info.balancesheet,name="balance_sheet"),
    path('cashflow/', info.cashflow,name="cash_flow"),
    path('candlesticks/', info.candlesticks,name="candlesticks"),
    path('pricepredict/', info.pricepredictions,name="pricepredict"),
    path('predict/', info.predict,name="predict"),
    path('fivedaymovingavg/', info.fivedaymovingdayaverage,name="fiveavg"),
    path('dbmshome/', views.tradinghome,name="dbmshome"),
    path('watchlist/', databases.watchlist,name="watchlist"),
    path('addwatchlist/', databases.addToWatchlist,name="addwatchlist"),
    path('deletewatchlist/', databases.deleteWatchlist,name="deletewatchlist"),
    path('printwatchlist/', databases.printWatchlist,name="printwatchlist"),
    path('buystocks/', databases.buy,name="buy"),
    path('buytransaction/', databases.buytranaction,name="buytransaction"),
    path('sellstocks/', databases.sell,name="sell"),
    path('selltransaction/', databases.selltransacion,name="selltransaction"),
    path('viewtransaction/', databases.ViewTransactions,name="viewtransaction"),
    path('viewportfolio/', databases.ViewPortfolio,name="viewportfolio"),
    path('viewcards/', databases.ViewCards,name="viewcards"),
    path('recurring/', databases.reccuring,name="recurring"),
    path('recurringoder/', databases.recurringorder,name="recurringorder"),
    path('viewrecurring/', databases.viewreccuring,name="viewrecurringorder"),
    path('customersupport/', databases.Custsupport,name="CustomerSupport"),
    path('customersupportdetails/', databases.Custsupportdetails,name="csdetails"),
    path('', databases.signin,name="signin"),
    path('signuppage/', databases.SignUp,name="signup"),
    path('login/', databases.login,name="login"),
]