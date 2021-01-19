import numpy as np
import pandas as pd
from matplotlib import pyplot
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score

from bs4 import BeautifulSoup
import re
import requests
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
    return "https://www.barchart.com/stocks/sectors/rankings?symbol=" + companyCode

def getSectorDataLink():

    url = "https://www.barchart.com/proxies/core-api/v1/quotes/get?fields=symbol%2CsymbolName%2Csectors%2ClastPrice%2CpriceChange%2CpercentChange%2ClowPrice1y%2CpriceChange%2CpercentChange%2CopenPrice%2ClastPrice1yAgo%2CopenPrice1y%2ChighPrice1y%2CmarketCap%2CpeRatioTrailing%2CearningsPerShare%2CannualNetIncome.format(millions%3B0)%2Cbeta%2CdividendRateTrailing%2CdividendYieldTrailing&method=%2Fquotes%2Fget&raw=1&symbols=NIO"

    payload={}
    headers = {
        'authority': 'www.barchart.com',
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36',
        'x-xsrf-token': 'eyJpdiI6IitUZGpVT3FLd3ZNSjNBbDB1dUppYWc9PSIsInZhbHVlIjoiQThnWnhrRkNxZ21sRjRTQXBQNDJmbHpqa1plUzhVWkVwRlh6RVRuNUFJTm56a3dyYXFkVDQxZ09oK2o1ajMzTiIsIm1hYyI6IjdlZjZmZWVjNTA1YWZhNmU5NzVmM2RkY2Y0Y2JmMGQ3OGZhY2VmZGI1NTEwZjEwNDQwYTYyNzFmOThkODI1NDUifQ==',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.barchart.com/stocks/sectors/rankings?symbol=NIO',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': 'cheat-01202021WebinarClosed=true; _gcl_au=1.1.1480181004.1610999181; _ga=GA1.2.2111207041.1610999181; _gid=GA1.2.1656464231.1610999181; usprivacy=1---; __qca=P0-1677819782-1610999185069; _admrla=2.0-a304f9ab-a6ab-6eae-1404-0f39ecdf7bb2; _pbjs_userid_consent_data=3524755945110770; _pubcid=2d01dcac-61e6-4fc9-9c1b-98812baddf01; cto_bidid=2KxbZl95NzBnNHlBWDNjMkJ0T3Y0ck9yWVdvbkQ2b3lJakJjZG9EV0QwUGVYemtCQ0tLbXV4SlVCWExkYVJ4MXlsRnMxZGwyVnp6cnRrS0htRGpRbU0lMkZaMk4wbjVSaUI5dmIlMkJ0WHNWT1FjQm1JJTJCVSUzRA; cto_bundle=FY2OWl9TSWE1cU5BYzUyOERRcXByWkxxOVl5UEV0WFg0Y1BNRzFPS21BdmdjaUpobmJTdmtrdFpTUnhyeUpWJTJGWHNhJTJCYjBrMU84WUlRQ2pFamF2bnY5YTc5JTJCMU4yQ3ExQ1lBcUs2OUh5QjVmSFQlMkJRbTE5akZHWGV0bDEybllPZiUyRlR4JTJGclh3JTJCbWFLUWVkb2cxY05jMDNtc1VjQSUzRCUzRA; pbjs-unifiedid=%7B%22TDID%22%3A%22eca9fe6c-cc0b-42d8-b13f-6fd4eeb9aea1%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222020-12-18T20%3A15%3A47%22%7D; idl_env=AvQSGFJO8RUPzSS0fgIFuNuCuG0zmCB_JhZoctwVTeYMb-ub1IFqvTEupYdR8IYycoFlRMNr4cMApaX2iGlFXdQlMQT3tDdwx0aTf7V_OrFPrNZE1Qu1BUtpi3_6Y2D4Qsz8juhlzMtyK5OUbefSW6QhG9xYYcbFcLwt5FOSeUzWZzUuurzvF7f0746AnqL8SmEzIBd2QZilVDkElLahVav4O1UTN8NpFx5Ilizm9zBBFjUoz6-Sn3kXASDImqzduX2WCxnMBEQnRu-etw-4X2VYYp_LTPpnFwDyDEaylymReWTIcw; fc=%7B%22MjY0fm51bGxfbnVsbH4xMDM0LU9BVEgxMDEzNzgwMDAtMjk2NjY4Ng%22%3A%221%3A1611000947202%22%2C%22NjI4fm51bGxfbnVsbH4yOTc0OjMwMDY2MzQ%22%3A%221%3A1611000965977%22%2C%22NjI4fm51bGxfbnVsbH4yOTc0OjMwNTYxOTA%22%3A%221%3A1611000996016%22%7D; pv=%7B%22d%22%3A%223%3A1611000947202%22%7D; GED_PLAYLIST_ACTIVITY=W3sidSI6IitVV20iLCJ0c2wiOjE2MTEwMDIxNDUsIm52IjowLCJ1cHQiOjE2MTEwMDA5NDEsImx0IjoxNjExMDAwOTQxfV0.; market=eyJpdiI6Ik1tMkQxRHpZeXJYeFpxSkpvQWd6Vmc9PSIsInZhbHVlIjoiazdvTTZ6STdjNDdMZHVyeXdOOGFPdz09IiwibWFjIjoiZTE1ODFiMDExMWFiNjIwM2M4MjFmMzk1NTUwY2YxZDUxNzgzYjIwMTkxYjE3MDMyM2QzZWQ5OGU5NjRiMjJlMiJ9; __gads=ID=0bd151c279f68900:T=1611080926:S=ALNI_MaxMC7inGxyVT3i5K4F2qX86--eSg; cto_bundle=AFXBV19TSWE1cU5BYzUyOERRcXByWkxxOVkyQlU1WGpwaE5iNm94RnJQTWgwUmdxU3hpeGxackNYanlwYjklMkZXMThXZk9HSTd2dHF3T0psSWZGaHJxS2o1V203cXBEbmtLbVFLRkxHYWZCUjRvd1poVzFHaXc1aEMzVFdhMG5pWU9lMUxSNmtxV2NoZXhYdGNQYkMlMkJoMkRWSFRnJTNEJTNE; cto_bundle=AFXBV19TSWE1cU5BYzUyOERRcXByWkxxOVkyQlU1WGpwaE5iNm94RnJQTWgwUmdxU3hpeGxackNYanlwYjklMkZXMThXZk9HSTd2dHF3T0psSWZGaHJxS2o1V203cXBEbmtLbVFLRkxHYWZCUjRvd1poVzFHaXc1aEMzVFdhMG5pWU9lMUxSNmtxV2NoZXhYdGNQYkMlMkJoMkRWSFRnJTNEJTNE; _awl=2.1611081161.0.4-881a78f4-a304f9aba6ab6eae14040f39ecdf7bb2-6763652d75732d6561737431-600725c9-0; laravel_token=eyJpdiI6Ijd1ZnA5KzFOZUQxeHFEY1NPQnhocFE9PSIsInZhbHVlIjoibzdQZUpBTDZqMEtkOWZCNEZvK0VoMnNpYzFSSitvVHAxb0lRWjFxb0ZybW40a05kcHo0UHN4c09uVFptK3pHQlplWGtxVjJsRTlaS0RVZWtIdXVjYkpKSHNTZlJNdVNPMWoyVE1scW15a1owTWlSODhxd1l6bCsrMkU3VVlzR3hDb1FTcDQrSFdUallmTTcwZXgybWNMc0NpbC9WcjdaU01BMkVvejA2UUhMYWxjRktML2pnaWJHUnl1SjNtS1Azc3B6c1FucUVWc09jL1UzZDBqSTEzK1dqZ21mbTVJdjVGc1VVT0VoaTc5VWcxMjliMVF4LzRwcjJVSnFKZzV5dSIsIm1hYyI6ImE3NjAyY2JkZDVmNzg2NWJkYjhmNzQ0N2UzMjIwMDlhYWZiOWViODRmMzc2MzYyZWQzZmVmYjFlMzViYjE2MTEifQ%3D%3D; XSRF-TOKEN=eyJpdiI6IitUZGpVT3FLd3ZNSjNBbDB1dUppYWc9PSIsInZhbHVlIjoiQThnWnhrRkNxZ21sRjRTQXBQNDJmbHpqa1plUzhVWkVwRlh6RVRuNUFJTm56a3dyYXFkVDQxZ09oK2o1ajMzTiIsIm1hYyI6IjdlZjZmZWVjNTA1YWZhNmU5NzVmM2RkY2Y0Y2JmMGQ3OGZhY2VmZGI1NTEwZjEwNDQwYTYyNzFmOThkODI1NDUifQ%3D%3D; laravel_session=eyJpdiI6ImdHYUliN3hVRDB5RytHdDZLdWdyN2c9PSIsInZhbHVlIjoiUEttQUxyZGgzNC85MmJIYlNQSVZHWFpoaDRoalRRc0EyNWo5Vi9RdHR6bkxRUnJlUVcvdFc3NksvYVhRNCs5SyIsIm1hYyI6ImNiMmIxMjVjNGU0MDk2ZmRkM2Y4YTIyNGI2MWQ1MmM5ZjcyN2YwZDRjM2E0OWYyM2Q2YTJkYTkxNTZlZWYwZTEifQ%3D%3D; _gat_UA-2009749-51=1; IC_ViewCounter_www.barchart.com=8'
        }

    response = requests.request("GET", url, headers=headers, data=payload)

    # print(response.text)

    # middleman = buildGetSectorLinkMiddleman(companyCode)
    # headers = requests.utils.default_headers()
    # headers.update({
    #     'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    #     })

    # response = requests.get(middleman, headers=headers)
    # soup = BeautifulSoup(response.text, "lxml")

    # daddy_div = soup.find("div",{"class": "sectors-list"}).find('ul')

    # try:
        
    # except:
    #     sector_data_link = "unavailable. Please enter a valid stock market code."

    return response.text

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
            data = float(data)

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
    print(freeCashFlows)
    xtrain = np.array([range(1,len(freeCashFlows)+1)], dtype=float).reshape(-1,1)
    ytrain = np.array(freeCashFlows,dtype=float)
    model = LinearRegression().fit(xtrain, ytrain)
    score = model.score(xtrain, ytrain)
    print("r:" + str(score))
    slope = -1 * model.coef_[0]
    print("slope: " + str(slope))

def evalPeRatios(finData, industry):
    df = pd.read_html("http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/pedata.html", header = 0, index_col="Industry Name")[0]

    industryGood = False

    while (industryGood == False):
        try: 
            indTrailPE = df.loc[industry, "Trailing  PE"]
            indForwardPE = df.loc[industry, 'Forward  PE']
            indPEG = df.loc[industry, 'PEG  Ratio']
            industryGood = True

        except:
            industry = input("The industry " + industry + " is not on this list. Please select one from the table:")

    global longScore
    global shortScore

    print(finData)

    if ((finData['trailingPE'] !='' and finData['forwardPE'] !='') and (finData['trailingPE'] < finData['forwardPE'])):
        #company is expected to grow
        longScore += 10
        shortScore +=5
    else:
        #company's earnings are expected to decrease
        longScore -= 10
        shortScore -=5


    if (finData['trailingPE'] !='')and ((finData['trailingPE'] < indTrailPE) ):
        #company is undervalued & has room to grow - good long term investment
        longScore += 10
        shortScore +=8
    else:
        #company may be overvalued - potential sell 
        longScore -= 5
        shortScore -= 6


    if ((finData['PEGratio'] !='') and (finData['PEGratio'] < 1)):
        #company's future is undervalued - good long term investment
        longScore += 12
        shortScore +=8

    elif ((finData['PEGratio'] !='') and (finData['PEGratio'] > 1)):
        #company's future may be overvalued - potential sell 
        longScore -= 7
        shortScore -= 2


    if ((finData['PEGratio'] !='')and (finData['PEGratio'] < indPEG) ):
        #company expected to fall behind competition - poor long term investment
        longScore -= 10
        shortScore -=12

    else:
        #company expected to keep pace with or exceed competition - good long term investment 
        longScore += 10
        shortScore += 11


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



companyCode = input("Enter company's stock market code: ")
print(getSectorDataLink())
print("The current price of " + str(getName(companyCode)) + " is: $"+str(livePrice(companyCode))+" per share.")
finData = getFinData(companyCode)
industry = str(input("Enter company's industry from http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/pedata.html : "))
evalPeRatios(finData, industry)
freeCashFlows = getCashFlows(companyCode)
evalCashFlows(freeCashFlows)
print("Short term investment score: " + str(shortScore))
print("Long term investment score: " + str(longScore))