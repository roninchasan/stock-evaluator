from flask import *

import numpy as np
import pandas as pd
import json
import math

from matplotlib import pyplot
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import Perceptron
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score

from bs4 import BeautifulSoup
import re
import requests
import io
import time
import datetime
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
        fcfsRaw = soup.find_all("span")[-26:-22]
        freeCashFlows = []
        # print(fcfsRaw)

        for fcf in fcfsRaw:
            fcfstring = re.search(betweenTagsRegEx, str(fcf)).group(0)
            choppedString = fcfstring.replace(",", "")
            # print(choppedString)
            if (choppedString!="Free Cash Flow"):
                freeCashFlows.append(int(choppedString))
        freeCashFlows.reverse()

        
    except:
        freeCashFlows = "FCFs unavailable."


    return freeCashFlows

def evalCashFlows(freeCashFlows):
    global longScore
    global shortScore

    # print(freeCashFlows)
    xtrain = np.array([range(1,len(freeCashFlows)+1)], dtype=float).reshape(-1,1)
    ytrain = np.array(freeCashFlows,dtype=float)
    model = LinearRegression().fit(xtrain, ytrain)
    score = model.score(xtrain, ytrain)
    # print("FCF r:" + str(score))
    slope = model.coef_[0]
    # print("FCF slope: " + str(slope))

    rateOfChange = 0.0
    curr = 0.0

    for i in range(1, len(freeCashFlows)):
        curr = freeCashFlows[i]/freeCashFlows[i-1]
        rateOfChange += curr

    rateOfChange = rateOfChange/(len(freeCashFlows)-1)

    # print((rateOfChange * score))

    longScore += 5*(rateOfChange * score)
    shortScore += 2*(rateOfChange * score)

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

    
    if ((finData['priceBookRatio'] !='')):   # and (finData['priceBookRatio'] < 1)):
        #stock price below book value - undervalued - good long term investment
        # longScore += 8/finData['priceBookRatio'] 
        longScore += -5 * math.log(finData['priceBookRatio'], 2) 
        # shortScore += 6/finData['priceBookRatio']
        shortScore += -3 * math.log(finData['priceBookRatio'], 2) 

        # if (finData['priceBookRatio'] < .6):
        #     #stock price far below book value - very undervalued - great long term investment
        #     true = True

        # elif (finData['priceBookRatio'] < .75):
        #     #stock price below book value - undervalued - good long term investment
        #     true = True

        # elif (finData['priceBookRatio'] < .9):
        #     #stock price slightly below book value - slightly undervalued - ok long term investment
        #     true = True

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
    global shortScore

    dfSelect = df.iloc[0:12]
    xtrain = np.array([range(12,0,-1)], dtype=float).reshape(-1,1)
    ytrain = np.array(dfSelect['close'],dtype=float)

    linModel = LinearRegression().fit(xtrain, ytrain)
    # print("Linear regression slope for time vs. price over last 3 months:", (linModel.coef_[0]))
    # print("Linear regression intercept for time vs. price over last 3 months:", linModel.intercept_)
    # print("Linear regression score for time vs. price over last 3 months:", linModel.score(xtrain, ytrain))

    polyX = PolynomialFeatures(interaction_only=True).fit_transform(xtrain).astype(int)
    polyY = ytrain.astype(int)
    polyModel = Perceptron(fit_intercept=False, max_iter=1000, tol=None,shuffle=False).fit(polyX, polyY)
    # print("Polynomial regression slope for time vs. price over last 3 months:", polyModel.coef_)
    # print("Polynomial regression score for time vs. price over last 3 months:", polyModel.score(polyX, polyY))

    logModel = LogisticRegression(solver='lbfgs', multi_class='auto', max_iter=10000).fit(polyX, polyY)
    # print("Logistic regression slope for time vs. price over last 3 months:", logModel.coef_[0][0])
    # print("Logistic regression score for time vs. price over last 3 months:", logModel.score(polyX, polyY))

    scores = {'lin':linModel.score(xtrain, ytrain),'poly':polyModel.score(polyX, polyY),'log':logModel.score(polyX, polyY)}
    maxScore = max(scores, key=scores.get)

    if maxScore == 'lin':
        shortScore += scores['lin']*(max(linModel.coef_[0],10))
    elif maxScore == 'poly':
        shortScore += scores['poly']*8
    elif maxScore == 'log':
        shortScore += scores['log']*2

def longTermMomentum(df):
    global longScore

    dfSelect = df.iloc[0:52]
    xtrain = np.array([range(52,0,-1)], dtype=float).reshape(-1,1)
    ytrain = np.array(dfSelect['close'],dtype=float)

    linModel = LinearRegression().fit(xtrain, ytrain)
    # print("Linear regression slope for time vs. price over last 12 months:", (linModel.coef_[0]))
    # print("Linear regression intercept for time vs. price over last 12 months:", linModel.intercept_)
    # print("Linear regression score for time vs. price over last 12 months:", linModel.score(xtrain, ytrain))

    polyX = PolynomialFeatures(interaction_only=True).fit_transform(xtrain).astype(int)
    polyY = ytrain.astype(int)
    polyModel = Perceptron(fit_intercept=False, max_iter=1000, tol=None,shuffle=False).fit(polyX, polyY)
    # print("Polynomial regression slope for time vs. price over last 12 months:", polyModel.coef_)
    # print("Polynomial regression score for time vs. price over last 12 months:", polyModel.score(polyX, polyY))

    logModel = LogisticRegression(solver='lbfgs', multi_class='auto', max_iter=10000).fit(polyX, polyY)
    # print("Logistic regression slope for time vs. price last 12 months:", model.coef_[0][0])
    # print("Logistic regression score for time vs. price last 12 months:", logModel.score(polyX, polyY))

    scores = {'lin':linModel.score(xtrain, ytrain),'poly':polyModel.score(polyX, polyY),'log':logModel.score(polyX, polyY)}
    maxScore = max(scores, key=scores.get)

    if maxScore == 'lin':
        longScore += scores['lin']*(max(linModel.coef_[0],10))
    elif maxScore == 'poly':
        longScore += scores['poly']*7
    elif maxScore == 'log':
        longScore += scores['log']*3

def getNewsSentiment(companyCode):
    response = requests.get('https://finnhub.io/api/v1/news-sentiment?symbol=' + companyCode + '&token=c08rrp748v6oofbnp750')
    # print(response.json())
    data = response.json()

    return data

    # json data formatted as tuple as follows:
    # {'buzz': {'articlesInLastWeek': 40, 'buzz': 0.7843, 'weeklyAverage': 51}, 
    # 'companyNewsScore': 0.9166, 'sectorAverageBullishPercent': 0.6558, 'sectorAverageNewsScore': 0.5427, 
    # 'sentiment': {'bearishPercent': 0, 'bullishPercent': 1}, 'symbol': 'NIO'}
    # access by data['buzz']['weeklyAverage']

def evalNewsSentiment(newsData):
    global longScore
    global shortScore
    
    val = 0

    shortScore += 5*newsData['buzz']['buzz']
    val += newsData['sentiment']['bullishPercent'] - newsData['sentiment']['bearishPercent']
    val += newsData['companyNewsScore'] + newsData['sectorAverageNewsScore']

    shortScore += 4*val
    longScore += 2*val

def getWallStreetRecs(companyCode):
    response = requests.get('https://finnhub.io/api/v1/stock/recommendation?symbol=' + companyCode + '&token=c08rrp748v6oofbnp750')
    rawData = response.json()
    data = pd.DataFrame(rawData)

    return data

    #data returned in DF object with buy, hold, sell, strong buy and strong sell columns. rows are dates on the first of each month.

def evalWallStreetRecs(data):
    global longScore
    global shortScore
    
    val = 0
    numRaters = data.at[0, 'strongSell']+data.at[0, 'sell']+data.at[0, 'buy']+data.at[0, 'strongBuy']

    val += (data.at[0, 'strongBuy']/numRaters)
    val += (data.at[0, 'buy']/numRaters)
    val -= (data.at[0, 'sell']/numRaters)
    val -= (data.at[0, 'strongSell'] /numRaters)

    # print(val)

    longScore += 10 * val
    shortScore += 13 * val

def getShortInterest(companyCode):
    import requests
    currentDate = str(datetime.datetime.now())[:10]
    lastYear = int(currentDate[:4]) - 1
    lastYearDate = str(lastYear) + currentDate[4:]
    response = requests.get('https://finnhub.io/api/v1/stock/short-interest?symbol=' + companyCode + '&from='+ lastYearDate +'&to=' + currentDate + '&token=c08rrp748v6oofbnp750')

    df = pd.DataFrame(response.json()['data'])

    #df with date (yyyy-mm-dd) and # of uncovered shorted shares columns

    return df

def evalShortInterest(shortData):

    dfSelect = shortData.iloc[0:12]
    xtrain = np.array([range(12,0,-1)], dtype=float).reshape(-1,1)
    ytrain = np.array(dfSelect['close'],dtype=float)

    linModel = LinearRegression().fit(xtrain, ytrain)
    print("Linear regression slope for time vs. short interest over last 3 months:", (linModel.coef_[0]))
    print("Linear regression intercept for time vs. short interest over last 3 months:", linModel.intercept_)
    print("Linear regression score for time vs. short interest over last 3 months:", linModel.score(xtrain, ytrain))

    polyX = PolynomialFeatures(interaction_only=True).fit_transform(xtrain).astype(int)
    polyY = ytrain.astype(int)
    polyModel = Perceptron(fit_intercept=False, max_iter=1000, tol=None,shuffle=False).fit(polyX, polyY)
    # print("Polynomial regression slope for time vs. price over last 3 months:", polyModel.coef_)
    print("Polynomial regression score for time vs. short interest over last 3 months:", polyModel.score(polyX, polyY))

    logModel = LogisticRegression(solver='lbfgs', multi_class='auto', max_iter=10000).fit(polyX, polyY)
    # print("Logistic regression slope for time vs. price over last 3 months:", logModel.coef_[0][0])
    print("Logistic regression score for time vs. short interest over last 3 months:", logModel.score(polyX, polyY))

def evaluate(companyCode):
    global shortScore
    shortScore = 50
    global longScore
    longScore = 50
    # companyCode = input("Enter company's stock market code: ")
    companyCode = companyCode.upper()
    print("The current price of " + str(getName(companyCode)) + " is: $"+str(livePrice(companyCode))+" per share.")
    # finData = getFinData(companyCode)
    industryData = getIndustryData(companyCode)

    # industry = str(input("Enter company's industry from http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/pedata.html : "))
    # evalFinData(finData)
    # compareIndustryData(finData, industryData)
    freeCashFlows = getCashFlows(companyCode)
    if (freeCashFlows != "FCFs unavailable."):
        evalCashFlows(freeCashFlows)

    historicalData = getHistoricalData(companyCode)
    # print()
    shortTermMomentum(historicalData)
    # print()
    longTermMomentum(historicalData)
    # print()

    newsData = getNewsSentiment(companyCode)
    evalNewsSentiment(newsData)
    wallStreetRecs = getWallStreetRecs(companyCode)
    evalWallStreetRecs(wallStreetRecs)
    # shorts = getShortInterest(companyCode)
    # evalShortInterest(shorts)
    return {"short": shortScore, "long":longScore, "data":historicalData}

# print()
# print("Short term investment score: " + str(shortScore))
# print("Long term investment score: " + str(longScore))

scores = {}

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')    

@app.route('/evaluated.html')
def evaluated():
    global scores
    # ticker = request.form['ticker']
    ticker = request.args.get('ticker')
    scores = evaluate(ticker)
    ticker = ticker.upper()
    print(scores)
    return render_template('evaluated.html', ticker = ticker, company = getName(ticker), shortScore = scores['short'], longScore = scores['long'], price = livePrice(ticker))


@app.route('/stockdata')
def getStockData():
    global scores
    df = scores['data']
    return df.to_csv()

# @app.route('/css/<path:path>')
# def send_css(path):
#     return send_from_directory('css', path)

# @app.route('/css/styles.css')
# def send_css():
#     return app.send_static_file('/css/styles.css')

if __name__ == "__main__":
    app.run(debug=True)