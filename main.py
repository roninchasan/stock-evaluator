import numpy as np
import pandas as pd
import json
from matplotlib import pyplot
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score

from bs4 import BeautifulSoup
import re
import requests
import io
import time
# from yahoo_finance import Share

betweenTagsRegEx = '(?<=>)(.*\n?)(?=<)'
shortScore = 50
longScore = 50
comments = []
sector_data_link = "https://eresearch.fidelity.com/eresearch/markets_sectors/sectors/sectors_in_market.jhtml?tab=learn&sector=10"

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

def buildFinDataLink(companyCode):
    return "https://finance.yahoo.com/quote/" + companyCode + "/key-statistics?p=" + companyCode

def buildCashFlowsLink(companyCode):
    return "https://finance.yahoo.com/quote/"+ companyCode + "/cash-flow?p="+ companyCode

def buildGetSectorLinkMiddleman(companyCode):
    return "https://eresearch.fidelity.com/eresearch/evaluate/snapshot.jhtml?symbols=" + companyCode

def buildIndustryLink(companyCode):
    url = buildGetSectorLinkMiddleman(companyCode)
    response = requests.get(url)    
    soup = BeautifulSoup(response.text, "lxml")
    comparison_div = soup.find("div", {"class": "comparison"})

    if comparison_div != None:
        industry = str(comparison_div.find("a"))
    else:
        return "no comparable industry at this point"

    industry_url_raw = industry.split('"')[1]
    industry_url_final = industry_url_raw.split('amp;')[0] + industry_url_raw.split('amp;')[1]

    return industry_url_final

def getIndustryData(companyCode):
    url = buildIndustryLink(companyCode)

    if url == "no comparable industry at this point":
        return "no comparable sector or industry at this point"

    response = requests.get(url)    
    soup = BeautifulSoup(response.text, "lxml")

    categories_raw = soup.find('div', {'class' : 'sec-fundamentals'}).find_all('th')
    data_points_raw = soup.find('div', {'class' : 'sec-fundamentals'}).find_all('td')

    categories_raw.pop(0)
    categories_raw.pop(0)

    categories = []
    data_points = []

    industry_data = {}

    for item in categories_raw:
        categories.append(item.text)

    for item in data_points_raw:
        item = str(item).replace('<td>', '').replace('</td>', '')
        item = str(item).strip()
        data_points.append(item)

    for i in range(0, 10):
        industry_data[categories[i]] = data_points[i]

    return industry_data

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
        elif "N/A" in data:
            data = ''
        else:
            try:
                data = float(data)
            except:
                data = ''

        finalFinData.append(data)

    finDataDict = dict(zip(finDataNames, finalFinData)) 

    return finDataDict

def getCashFlows(companyCode):

    url = buildCashFlowsLink(companyCode)
    response = requests.get(url)    
    soup = BeautifulSoup(response.text, "lxml")

    try:
        # price = soup.find("div",{"class": "My(6px) Pos(r) smartphone_Mt(6px)"}).find("span").text
        fcfsRaw = soup.find_all("span")[-21:-16]
        freeCashFlows = []

        for fcf in fcfsRaw:
            fcfstring = re.search(betweenTagsRegEx, str(fcf)).group(0)
            choppedString = fcfstring.replace(",", "")
            if (choppedString!="Free Cash Flow"):
                freeCashFlows.append(choppedString)
        
    except:
        freeCashFlows = "FCFs unavailable."

    return freeCashFlows

def evalCashFlows(freeCashFlows):
    # print(freeCashFlows)
    xtrain = np.array([range(1,len(freeCashFlows)+1)], dtype=float).reshape(-1,1)
    ytrain = np.array(freeCashFlows,dtype=float)
    model = LinearRegression().fit(xtrain, ytrain)
    score = model.score(xtrain, ytrain)
    print("FCF r:" + str(score))
    slope = -1 * model.coef_[0]
    print("FCF slope: " + str(slope))

def evalFinData(finData):
    global longScore
    global shortScore

    if ((finData['trailingPE'] !='' and finData['forwardPE'] !='') and (finData['trailingPE'] < finData['forwardPE'])):
        #company is expected to grow
        longScore += 10
        shortScore +=5
    else:
        #company's earnings are expected to decrease
        longScore -= 10
        shortScore -=5


    if ((finData['PEGratio'] !='') and (finData['PEGratio'] < 1)):
        #company's future is undervalued - good long term investment
        longScore += 12
        shortScore +=8
    elif ((finData['PEGratio'] !='') and (finData['PEGratio'] > 1)):
        #company's future may be overvalued - potential sell 
        longScore -= 7
        shortScore -= 2

    
    if ((finData['priceBookRatio'] !='') and (finData['priceBookRatio'] < 1)):
        #stock price below book value - undervalued - good long term investment
        longScore += 8/finData['priceBookRatio']
        shortScore += 6/finData['priceBookRatio']

        if (finData['priceBookRatio'] < .6):
            #stock price far below book value - very undervalued - great long term investment
            true = True

        if (finData['priceBookRatio'] < .75):
            #stock price below book value - undervalued - good long term investment
            true = True

        if (finData['priceBookRatio'] < .9):
            #stock price slightly below book value - slightly undervalued - ok long term investment
            true = True

    elif (finData['priceBookRatio'] !=''):
        #stock price is inflated/overvalued - not great long term investment 
        longScore -= .5*finData['priceBookRatio']
        shortScore -= .3*finData['priceBookRatio']    





def compareIndustryData(finData, industry):
    # df = pd.read_html("http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/pedata.html", header = 0, index_col="Industry Name")[0]

    # industryGood = False

    # while (industryGood == False):
    #     try: 
    #         indTrailPE = df.loc[industry, "Trailing  PE"]
    #         indForwardPE = df.loc[industry, 'Forward  PE']
    #         indPEG = df.loc[industry, 'PEG  Ratio']
    #         industryGood = True

    #     except:
    #         industry = input("The industry " + industry + " is not on this list. Please select one from the table:")

    global longScore
    global shortScore

    indTrailPE = industry["P/E (Last Year GAAP Actual)"]
    indForwardPE = industry["P/E (This Year's Estimate)"]
    indPEG = industry["P/E (This Year's Estimate)"]/industry["EPS Growth (TTM vs. Prior TTM)"]
    
    if (finData['trailingPE'] !='')and ((finData['trailingPE'] < indTrailPE) ):
        #company is undervalued & has room to grow - good long term investment
        longScore += 10
        shortScore +=8
    else:
        #company may be overvalued - potential sell 
        longScore -= 5
        shortScore -= 6


    if ((finData['PEGratio'] !='')and (finData['PEGratio'] < indPEG) ):
        #company expected to fall behind competition - poor long term investment
        longScore -= 10
        shortScore -=12

    else:
        #company expected to keep pace with or exceed competition - good long term investment 
        longScore += 10
        shortScore += 11



def getHistoricalData(companyCode):
    url = "https://alpha-vantage.p.rapidapi.com/query"

    querystring = {"function":"TIME_SERIES_WEEKLY","symbol":companyCode,"datatype":"csv"}

    headers = {
        'x-rapidapi-key': "5a71a248c1mshec5ac249ab63653p1e7a54jsnf4f122a5edee",
        'x-rapidapi-host': "alpha-vantage.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    rawData = io.StringIO(response.text)
    data = pd.read_csv(rawData)

    marketCap = data['close'] * data['volume']

    data.insert(6,'MarketCap', marketCap)


    return data

def shortTermMomentum(df):

    dfSelect = df.iloc[0:12]
    xtrain = np.array([range(12,0,-1)], dtype=float).reshape(-1,1)
    ytrain = np.array(dfSelect['close'],dtype=float)

    linModel = LinearRegression().fit(xtrain, ytrain)
    print("Linear regression slope for time vs. price over last 3 months:", (linModel.coef_[0]))
    print("Linear regression intercept for time vs. price over last 3 months:", linModel.intercept_)
    print("Linear regression score for time vs. price over last 3 months:", linModel.score(xtrain, ytrain))

    # logModel = LogisticRegression(solver='lbfgs', multi_class='auto', max_iter=2000).fit(xtrain, dfSelect[['close']])
    # print("Logistic regression slope for time vs. price over last 3 months:", logModel.coef_[0][0])
    # print("Logistic regression score for time vs. price over last 3 months:", logModel.score(dfSelect[['close']], dfSelect.index))
    

def longTermMomentum(df):

    dfSelect = df.iloc[0:52]
    xtrain = np.array([range(52,0,-1)], dtype=float).reshape(-1,1)
    ytrain = np.array(dfSelect['close'],dtype=float)

    linModel = LinearRegression().fit(xtrain, ytrain)
    print("Linear regression slope for time vs. price over last 12 months:", (linModel.coef_[0]))
    print("Linear regression intercept for time vs. price over last 12 months:", linModel.intercept_)
    print("Linear regression score for time vs. price over last 12 months:", linModel.score(xtrain, ytrain))

    # model = LogisticRegression(solver='lbfgs', multi_class='auto', max_iter=2500).fit(dfSelect[['close']], dfSelect.index)
    # print("Logistic regression slope for time vs. price last 12 months:", model.coef_[0][0])
    # print("Logistic regression score for time vs. price last 12 months:", model.score(dfSelect[['close']], dfSelect.index))


companyCode = input("Enter company's stock market code: ")
companyCode = companyCode.upper()
print("The current price of " + str(getName(companyCode)) + " is: $"+str(livePrice(companyCode))+" per share.")
finData = getFinData(companyCode)
industryData = getIndustryData(companyCode)

# industry = str(input("Enter company's industry from http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/pedata.html : "))
# evalFinData(finData)
# compareIndustryData(finData, industryData)
# freeCashFlows = getCashFlows(companyCode)
# evalCashFlows(freeCashFlows)

historicalData = getHistoricalData(companyCode)
print()
shortTermMomentum(historicalData)
print()
longTermMomentum(historicalData)
print()


print("Short term investment score: " + str(shortScore))
print("Long term investment score: " + str(longScore))