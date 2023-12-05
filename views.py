from django.shortcuts import render
import yfinance as yf
import joblib
import yfinance as yf
import sqlite3
from django.shortcuts import render
import yahoo_fin.stock_info as si
def home(request):
    return render(request, 'index.html')
def signin(request):
    return render(request, 'sign_in.html')
def signingin(request):
    """
    connection1= sqlite3.connect('abcd.db')
    cursor=connection1.cursor()
    """
    global username,passwd
    username=request.GET['emailid']
    passwd=request.GET['pass']
    """
    cursor.execute("CREATE TABLE IF NOT EXISTS testing (username TEXT, passwd TEXT)")
    cursor.commit()
    cursor.execute("INSERT INTO testing VALUES (?,?)", username,passwd)
    cursor.commit()
    cursor.close()
    connection1.close()
    """
    if username == 'user@123.com' and passwd == 'web':
        return render(request, 'index.html')
def tradinghome(request):
    return render(request, 'dbmshome.html')