import pandas as pd
import numpy as np
from matplotlib import pyplot

from bs4 import BeautifulSoup
import re
import requests

betweenTagsRegEx = '(?<=>)(.*\n?)(?=<)'

def livePrice(companyCode):

    url = buildLivePriceLink(companyCode)
    response = requests.get(url)    
    soup = BeautifulSoup(response.text, "lxml")

    try:
        price = soup.find("div",{"class": "My(6px) Pos(r) smartphone_Mt(6px)"}).find("span").text

    except:
        price = "unavailable. Please enter a valid stock market code."

    return price

def getName(companyCode):

    url = buildLivePriceLink(companyCode)
    response = requests.get(url)    
    soup = BeautifulSoup(response.text, "lxml")

    try:
        name = soup.find("h1").text
    except:
        name = companyCode

    return name

def buildLivePriceLink(companyCode):
    return "https://finance.yahoo.com/quote/"+ companyCode + "?p="+ companyCode + "&.tsrc=fin-srch"

def getFinData(companyCode):
    
    response = requests.get(buildFinDataLink(companyCode))
    soup = BeautifulSoup(response.text, "lxml")

    allData = soup.find_all('td')

    freeCashFlowHTML = allData[-1]
    freeCashFlow = re.search(betweenTagsRegEx, str(freeCashFlowHTML)).group(0)

    opCashFlowHTML = allData[-3]
    opCashFlow = re.search(betweenTagsRegEx, str(opCashFlowHTML)).group(0)

    bookValPerShareHTML = allData[-5]
    bookValPerShare = re.search(betweenTagsRegEx, str(bookValPerShareHTML)).group(0)

    currentRatioHTML = allData[-7]
    currentRatio = re.search(betweenTagsRegEx, str(currentRatioHTML)).group(0)

    debtEquityHTML = allData[-9]
    debtEquity = re.search(betweenTagsRegEx, str(debtEquityHTML)).group(0)

    totalDebtHTML = allData[-11]
    totalDebt = re.search(betweenTagsRegEx, str(totalDebtHTML)).group(0)

    totalCashHTML = allData[-15]
    totalCash = re.search(betweenTagsRegEx, str(totalCashHTML)).group(0)

    yoyEarningsGrowthHTML = allData[-17]
    yoyEarningsGrowth = re.search(betweenTagsRegEx, str(yoyEarningsGrowthHTML)).group(0)

    yoyRevenueGrowthHTML = allData[-27]
    yoyRevenueGrowth = re.search(betweenTagsRegEx, str(yoyRevenueGrowthHTML)).group(0)

    revenueHTML = allData[-31]
    revenue = re.search(betweenTagsRegEx, str(revenueHTML)).group(0)

    returnOnEquityHTML = allData[-33]
    returnOnEquity = re.search(betweenTagsRegEx, str(returnOnEquityHTML)).group(0)

    returnOnAssetsHTML = allData[-35]
    returnOnAssets = re.search(betweenTagsRegEx, str(returnOnAssetsHTML)).group(0)

    operatingMarginHTML = allData[-37]
    operatingMargin = re.search(betweenTagsRegEx, str(operatingMarginHTML)).group(0)

    profitMarginHTML = allData[-39]
    profitMargin = re.search(betweenTagsRegEx, str(profitMarginHTML)).group(0)

    trailingPEHTML = allData[13]
    trailingPE = re.search(betweenTagsRegEx, str(trailingPEHTML)).group(0)

    forwardPEHTML = allData[19]
    forwardPE = re.search(betweenTagsRegEx, str(forwardPEHTML)).group(0)

    PEGratioHTML = allData[25]
    PEGratio = re.search(betweenTagsRegEx, str(PEGratioHTML)).group(0)

    priceSalesRatioHTML = allData[31]
    priceSalesRatio = re.search(betweenTagsRegEx, str(priceSalesRatioHTML)).group(0)

    priceBookRatioHTML = allData[37]
    priceBookRatio = re.search(betweenTagsRegEx, str(priceBookRatioHTML)).group(0)

    finData = [freeCashFlow, opCashFlow, currentRatio, bookValPerShare, debtEquity, totalDebt, totalCash, 
    yoyEarningsGrowth, yoyRevenueGrowth, revenue, returnOnEquity, returnOnAssets, operatingMargin, 
    profitMargin, trailingPE, forwardPE, PEGratio, priceSalesRatio, priceBookRatio]

    finalFinData = []

    finDataNames = ['freeCashFlow', 'opCashFlow', 'currentRatio', 'bookValPerShare', 'debtEquity', 'totalDebt',
    'totalCash', 'yoyEarningsGrowth', 'yoyRevenueGrowth', 'revenue', 'returnOnEquity', 'returnOnAssets',
    'operatingMargin', 'profitMargin', 'trailingPE', 'forwardPE', 'PEGratio', 'priceSalesRatio', 'priceBookRatio']

    for data in finData:
        if data[-1] == 'M':
            data = float(data[0:-1]) * 1000000
        elif data[-1] == 'B':
            data = float(data[0:-1]) * 1000000000
        elif data[-1] == '%':
            data = float(data[0:-1]) / 100.0
        else:
            data = float(data)

        finalFinData.append(data)

    finDataDict = dict(zip(finDataNames, finalFinData)) 

    return finDataDict


def buildFinDataLink(companyCode):
    return "https://finance.yahoo.com/quote/" + companyCode + "/key-statistics?p=" + companyCode

def evalPeRatios(finData, industry):
    df = pd.DataFrame(pd.read_csv("pedata.csv", index_col="Industry  Name"))

    industryBad = False

    while (industryBad == False):
        try: 
            indTrailPE = df.loc[industry, "Trailing PE"]
            indForwardPE = df.loc[industry, 'Forward PE']
            indPEG = df.loc[industry, 'PEG Ratio']

            industryBad = True
        except:
            print("The industry " + industry + "is not on this list. Please select one from the table.")
            industry = input()

    if (finData['trailingPE'] < finData['forwardPE']):
        #company is expected to grow
        true = True
    else:
        #company's earnings are expected to decrease
        true = True


    if (finData['trailingPE'] < indTrailPE):
        #company is undervalued - good long term investment
        true = True

    else:
        #company may be overvalued - potential sell 
        true = True

    if (finData['PEGratio'] < 1):
        #company's future is undervalued - good long term investment
        true = True

    elif (finData['PEGratio'] > 1):
        #company's future may be overvalued - potential sell 
        true = True

    if (finData['PEGratio'] < indPEG):
        #company expected to fall behind competition - poor long term investment
        true = True

    else:
        #company expected to keep pace with or exceed competition - good long term investment 
        true = True

    if (finData['priceBookRatio'] < 1):
        #stock price below book value - undervalued - good long term investment
        true = True

        if (finData['priceBookRatio'] < .6):
            #stock price far below book value - very undervalued - great long term investment
            true = True

        if (finData['priceBookRatio'] < .75):
            #stock price below book value - undervalued - good long term investment
            true = True

        if (finData['priceBookRatio'] < .9):
            #stock price slightly below book value - slightly undervalued - ok long term investment
            true = True

    


print("Enter company's stock market code:")
companyCode = str(input())
print("The current price of " + str(getName(companyCode)) + " is: "+str(livePrice(companyCode)))
finData = getFinData(companyCode)
print("Enter company's industry from http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/pedata.html:")
industry = str(input())
evalPeRatios(finData, industry)