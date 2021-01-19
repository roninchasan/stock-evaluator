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

def getSectorData(companyCode):

    #get company sector

    url = "https://www.barchart.com/proxies/core-api/v1/quotes/get?fields=symbol%2CsymbolName%2Csectors%2ClastPrice%2CpriceChange%2CpercentChange%2ClowPrice1y%2CpriceChange%2CpercentChange%2CopenPrice%2ClastPrice1yAgo%2CopenPrice1y%2ChighPrice1y%2CmarketCap%2CpeRatioTrailing%2CearningsPerShare%2CannualNetIncome.format(millions%3B0)%2Cbeta%2CdividendRateTrailing%2CdividendYieldTrailing&method=%2Fquotes%2Fget&raw=1&symbols=" + companyCode

    payload={}
    headers = {
        'authority': 'www.barchart.com',
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36',
        'x-xsrf-token': 'eyJpdiI6InlEcHFnRzNTZiszM1lCY1hRdTBlQlE9PSIsInZhbHVlIjoicW9CZTBnSDJTNm1lOGNsZ0FDSlk2Z0o1dm8wN1J0akRnR1lZQ0dTRjMwQlBmYVVKNWVrZnFWMVNNRWdGVTBzNiIsIm1hYyI6ImI3Yjk3MDI3OTEzMGQ0MmE0N2U4ZGYxYjY0ZDlmNmZlNmRmNWU2ODg3NDNmZWNkYWE3N2Y0MzMyZmIyZjQ5OTcifQ==',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.barchart.com/stocks/sectors/rankings?symbol=' + companyCode,
        'accept-language': 'en-US,en;q=0.9',
        'cookie': '_gcl_au=1.1.1480181004.1610999181; _ga=GA1.2.2111207041.1610999181; _gid=GA1.2.1656464231.1610999181; usprivacy=1---; __qca=P0-1677819782-1610999185069; _admrla=2.0-a304f9ab-a6ab-6eae-1404-0f39ecdf7bb2; _pbjs_userid_consent_data=3524755945110770; _pubcid=2d01dcac-61e6-4fc9-9c1b-98812baddf01; cto_bidid=2KxbZl95NzBnNHlBWDNjMkJ0T3Y0ck9yWVdvbkQ2b3lJakJjZG9EV0QwUGVYemtCQ0tLbXV4SlVCWExkYVJ4MXlsRnMxZGwyVnp6cnRrS0htRGpRbU0lMkZaMk4wbjVSaUI5dmIlMkJ0WHNWT1FjQm1JJTJCVSUzRA; cto_bundle=FY2OWl9TSWE1cU5BYzUyOERRcXByWkxxOVl5UEV0WFg0Y1BNRzFPS21BdmdjaUpobmJTdmtrdFpTUnhyeUpWJTJGWHNhJTJCYjBrMU84WUlRQ2pFamF2bnY5YTc5JTJCMU4yQ3ExQ1lBcUs2OUh5QjVmSFQlMkJRbTE5akZHWGV0bDEybllPZiUyRlR4JTJGclh3JTJCbWFLUWVkb2cxY05jMDNtc1VjQSUzRCUzRA; pbjs-unifiedid=%7B%22TDID%22%3A%22eca9fe6c-cc0b-42d8-b13f-6fd4eeb9aea1%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222020-12-18T20%3A15%3A47%22%7D; idl_env=AvQSGFJO8RUPzSS0fgIFuNuCuG0zmCB_JhZoctwVTeYMb-ub1IFqvTEupYdR8IYycoFlRMNr4cMApaX2iGlFXdQlMQT3tDdwx0aTf7V_OrFPrNZE1Qu1BUtpi3_6Y2D4Qsz8juhlzMtyK5OUbefSW6QhG9xYYcbFcLwt5FOSeUzWZzUuurzvF7f0746AnqL8SmEzIBd2QZilVDkElLahVav4O1UTN8NpFx5Ilizm9zBBFjUoz6-Sn3kXASDImqzduX2WCxnMBEQnRu-etw-4X2VYYp_LTPpnFwDyDEaylymReWTIcw; fc=%7B%22MjY0fm51bGxfbnVsbH4xMDM0LU9BVEgxMDEzNzgwMDAtMjk2NjY4Ng%22%3A%221%3A1611000947202%22%2C%22NjI4fm51bGxfbnVsbH4yOTc0OjMwMDY2MzQ%22%3A%221%3A1611000965977%22%2C%22NjI4fm51bGxfbnVsbH4yOTc0OjMwNTYxOTA%22%3A%221%3A1611000996016%22%7D; pv=%7B%22d%22%3A%223%3A1611000947202%22%7D; __gads=ID=0bd151c279f68900:T=1611080926:S=ALNI_MaxMC7inGxyVT3i5K4F2qX86--eSg; market=eyJpdiI6IjQ4bG1HRk5TRG5DT2ZjQzZwak9lRXc9PSIsInZhbHVlIjoiSWhmdUMwLzFHMlZqb0ZuTmhLTnNRQT09IiwibWFjIjoiNTJhNWQ2Y2FlNmRjOTljNjUyYmYwNTZhYjViNTU3MDFiN2FlNGI3MTVhYmY2YWY2OGY4NzEyNGJlZDJjZWY4ZSJ9; cheat-01202021PageView=1; cheat-01202021WebinarClosed=true; session_depth=www.barchart.com%3D1%7C743181235%3D1; _gat_UA-2009749-51=1; IC_ViewCounter_www.barchart.com=4; cto_bundle=HUhpNV9TSWE1cU5BYzUyOERRcXByWkxxOVl4bTBWOHMyeDdnM0JHOWxMb0s3TzVkcUVmWG03eDU0cnVrN1NaVkhkcktzYTU3VXoyYlgzRnBsS2R0SWNzVE01U2ZwNnZJJTJGODN4cXcwZUJ0NzVjZmczb21RS2ZabTE1UEVMSG9pZG1HbjV2RndwUGw2WDdXU29wMTFFUE9Mb3NPUSUzRCUzRA; cto_bundle=HUhpNV9TSWE1cU5BYzUyOERRcXByWkxxOVl4bTBWOHMyeDdnM0JHOWxMb0s3TzVkcUVmWG03eDU0cnVrN1NaVkhkcktzYTU3VXoyYlgzRnBsS2R0SWNzVE01U2ZwNnZJJTJGODN4cXcwZUJ0NzVjZmczb21RS2ZabTE1UEVMSG9pZG1HbjV2RndwUGw2WDdXU29wMTFFUE9Mb3NPUSUzRCUzRA; _awl=2.1611091447.0.4-60bb6241-a304f9aba6ab6eae14040f39ecdf7bb2-6763652d75732d6561737431-60074df2-0; laravel_token=eyJpdiI6IlV0dVAwNFArTW9lQ2M2RFhZY1ZkUVE9PSIsInZhbHVlIjoiWUNpazJFcEg3MnVYYU5rQnl2SXBUeUNub1RwMyttdUNqQmMrM1p3eE9nTFh5ZEViY09ZSUUvM0VnYTVQNmF5NkVkbjc4akZ4NW82NE9kTXdIZFExS1hYUW1mVkRCaFhzb0cyMkRjb041aW0yUHFNQVczMDNTMTdNdHlGMnUycWtBT3NmUTZMeFJEcTlUcEdyQjNRQlkxeVNmSlllbGxFRkViU1JhMjFWWkYvLzhZU1B0KzJGNXltTlc5bXJ0SWRFbFd5ZitrYW5FOXN6dVZrL0phZXZTbEVpRkxlUWUyMWZGeEhkWmVOTmJDVGhLNndrVENaa01TUFpvaDFpTFgxdyIsIm1hYyI6IjdhMmNjYWY2ZTdmMGU2NGQyNWVkYmJkODZhMjZhOWNhZTM0MmZkZTFmN2RjMTRiMTJlMjdiNDIwM2M4NzIxMTkifQ%3D%3D; XSRF-TOKEN=eyJpdiI6InlEcHFnRzNTZiszM1lCY1hRdTBlQlE9PSIsInZhbHVlIjoicW9CZTBnSDJTNm1lOGNsZ0FDSlk2Z0o1dm8wN1J0akRnR1lZQ0dTRjMwQlBmYVVKNWVrZnFWMVNNRWdGVTBzNiIsIm1hYyI6ImI3Yjk3MDI3OTEzMGQ0MmE0N2U4ZGYxYjY0ZDlmNmZlNmRmNWU2ODg3NDNmZWNkYWE3N2Y0MzMyZmIyZjQ5OTcifQ%3D%3D; laravel_session=eyJpdiI6Ik81TUE0VzZCRGtjR2MxbmJrdnUxSXc9PSIsInZhbHVlIjoiNHUwNytCL0FlM09VK1hSQWIrVFI3amcyTitFbm5md2RJbkxxdHI2T01XMWhqbmRXM2VVME92WEtlUkthUXZodiIsIm1hYyI6IjdhNjY5NTZjYjJiODFjYTczYTk4NTIzYTQ3NDM5YzAyMzQ3ZDA2Yzc2ZGI5ZTNjOWVlNWZhNWJjYjA2YTY0M2UifQ%3D%3D'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = json.loads(response.content)
    company_sector_symbol = data['data'][0]['sectors'][1]['symbol']
    company_sector_description = data['data'][0]['sectors'][1]['description']

    #get stock list from sector

    url = "https://www.barchart.com/proxies/core-api/v1/quotes/get?lists=stocks.inSector.all(" + company_sector_symbol + ")&fields=symbol%2CsymbolName%2CweightedAlpha%2ClastPrice%2CpriceChange%2CpercentChange%2ChighPrice1y%2ClowPrice1y%2CpercentChange1y%2CtradeTime%2CsymbolCode%2CsymbolType%2ChasOptions&orderBy=weightedAlpha&orderDir=desc&meta=field.shortName%2Cfield.type%2Cfield.description&hasOptions=true&page=1&limit=25&raw=1"

    payload={}
    headers = {
        'authority': 'www.barchart.com',
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36',
        'x-xsrf-token': 'eyJpdiI6IkRUN0lKZkxiTmRsUmNFWUJDZVVFaVE9PSIsInZhbHVlIjoiZk1CQkVPSEI0d3IyWHJ3SDVnT2llYkhsZEZIYkpKN01oYVI1VmFhK0NrQnBsMWMvWTl3UUo4aWtodDl5cnQxTyIsIm1hYyI6ImY4ZDVkMGE2OGFlZjllOTA5YWFhN2ZiY2Y3YTE0NzI1ZTFjYTA2OTQ0NWUyNDViODYxMjBhOGYwYzI0MDBhNGUifQ==',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.barchart.com/stocks/quotes/' + company_sector_symbol + '/components/' + companyCode,
        'accept-language': 'en-US,en;q=0.9',
        'cookie': '_gcl_au=1.1.1480181004.1610999181; _ga=GA1.2.2111207041.1610999181; _gid=GA1.2.1656464231.1610999181; usprivacy=1---; __qca=P0-1677819782-1610999185069; _admrla=2.0-a304f9ab-a6ab-6eae-1404-0f39ecdf7bb2; _pbjs_userid_consent_data=3524755945110770; _pubcid=2d01dcac-61e6-4fc9-9c1b-98812baddf01; pbjs-unifiedid=%7B%22TDID%22%3A%22eca9fe6c-cc0b-42d8-b13f-6fd4eeb9aea1%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222020-12-18T20%3A15%3A47%22%7D; idl_env=AvQSGFJO8RUPzSS0fgIFuNuCuG0zmCB_JhZoctwVTeYMb-ub1IFqvTEupYdR8IYycoFlRMNr4cMApaX2iGlFXdQlMQT3tDdwx0aTf7V_OrFPrNZE1Qu1BUtpi3_6Y2D4Qsz8juhlzMtyK5OUbefSW6QhG9xYYcbFcLwt5FOSeUzWZzUuurzvF7f0746AnqL8SmEzIBd2QZilVDkElLahVav4O1UTN8NpFx5Ilizm9zBBFjUoz6-Sn3kXASDImqzduX2WCxnMBEQnRu-etw-4X2VYYp_LTPpnFwDyDEaylymReWTIcw; __gads=ID=0bd151c279f68900:T=1611080926:S=ALNI_MaxMC7inGxyVT3i5K4F2qX86--eSg; market=eyJpdiI6IjQ4bG1HRk5TRG5DT2ZjQzZwak9lRXc9PSIsInZhbHVlIjoiSWhmdUMwLzFHMlZqb0ZuTmhLTnNRQT09IiwibWFjIjoiNTJhNWQ2Y2FlNmRjOTljNjUyYmYwNTZhYjViNTU3MDFiN2FlNGI3MTVhYmY2YWY2OGY4NzEyNGJlZDJjZWY4ZSJ9; cheat-01202021PageView=1; cheat-01202021WebinarClosed=true; _gat_UA-2009749-51=1; cto_bidid=7Gtu5F95NzBnNHlBWDNjMkJ0T3Y0ck9yWVdvbkQ2b3lJakJjZG9EV0QwUGVYemtCQ0tLbXV4SlVCWExkYVJ4MXlsRnMxZGwyVnp6cnRrS0htRGpRbU0lMkZaMk4lMkZoNnQzNm5HdVFhJTJGVktDMlFWWHQ1byUzRA; cto_bundle=85drx19TSWE1cU5BYzUyOERRcXByWkxxOVkwTUdNdGVuNnJCNHhoUU5CcWIzQzFSTFVhVDFlRjE5NUlBQjd4N0FxSDRjeVdic2tWSmdmcVpFc0I0OHo3NnY3aktFb1BjclB0elRva3VjWDBTR2V6a1BxRmw3SWVDRFclMkZIU01wQkc5Z0l6Zmlyb0NjY0FCdCUyRjBwZWsyNkliYndRJTNEJTNE; fc=%7B%22NjI4fm51bGxfbnVsbH4yOTc0OjMwMjk3NzU%22%3A%221%3A1611092692165%22%7D; pv=%7B%22d%22%3A%224%3A1611000947202%22%7D; GED_PLAYLIST_ACTIVITY=W3sidSI6IitVV20iLCJ0c2wiOjE2MTEwOTI3MDQsIm52IjoxLCJ1cHQiOjE2MTEwOTI2ODcsImx0IjoxNjExMDkyNzA0fV0.; cto_bundle=GGrWQ19TSWE1cU5BYzUyOERRcXByWkxxOVkyVFFIUTFvNmNiQWViSWNPZ1Fja0w4NnAzSklPaFlOZDhEbEJqNzlHUU9US3FmcnA4MkVEalRyUmYzazhraiUyQmtCd1dOaFFUNTBWa3NWJTJGSXJ4RFh1TTZNbkVucTRkbWxreWJXZlFnaVhqcTZZSEpCeUM4aFBrUFRFYkdEUk9zTjJnJTNEJTNE; cto_bundle=GGrWQ19TSWE1cU5BYzUyOERRcXByWkxxOVkyVFFIUTFvNmNiQWViSWNPZ1Fja0w4NnAzSklPaFlOZDhEbEJqNzlHUU9US3FmcnA4MkVEalRyUmYzazhraiUyQmtCd1dOaFFUNTBWa3NWJTJGSXJ4RFh1TTZNbkVucTRkbWxreWJXZlFnaVhqcTZZSEpCeUM4aFBrUFRFYkdEUk9zTjJnJTNEJTNE; _awl=2.1611092710.0.4-d85f00f-a304f9aba6ab6eae14040f39ecdf7bb2-6763652d75732d6561737431-600752e0-0; laravel_token=eyJpdiI6ImdjMmFQMVRMVm1XcENpM0p6amptWnc9PSIsInZhbHVlIjoiWU10VUw0TnMzdnNJRk9Qd096ZndBVXVSdDZVZ3pscUpqWmtmTHFQMWZMWlM3K0VEL09Lc0JHa2NLTlU2emhIU1haRTIwQjFwYThNbmR6bHlnekhiMmtBVjhkQVExVjhvRFR3QkFZTHpOWnd5RVlYYTFKNWhKVWdNaDJENGRYN2ltaFB5SXpMUm5lMk80c3F0WkNQSGtmNS9GOUQ1T0pUcnkvR1J5OGhUT3FZS1ZKbTJqbWVJbCsxM1ZyYS83cExpZVhXVnJ4YzRSQ29WUnhwanlrelhWWVZWSlA2UEM5ZUw2SExHbzg3SmNIT1cvNUc1aDFscjBiSjlXd0M4ZHlzWSIsIm1hYyI6ImUwMGE3MGUzNjdlYjJkNzYzOTNmODM3NDBiOTc4MWQ5MDExNDc3MzZmZjhkNmM2OTIyNDU0ZTk1ZjUyNzJhMWQifQ%3D%3D; XSRF-TOKEN=eyJpdiI6IkRUN0lKZkxiTmRsUmNFWUJDZVVFaVE9PSIsInZhbHVlIjoiZk1CQkVPSEI0d3IyWHJ3SDVnT2llYkhsZEZIYkpKN01oYVI1VmFhK0NrQnBsMWMvWTl3UUo4aWtodDl5cnQxTyIsIm1hYyI6ImY4ZDVkMGE2OGFlZjllOTA5YWFhN2ZiY2Y3YTE0NzI1ZTFjYTA2OTQ0NWUyNDViODYxMjBhOGYwYzI0MDBhNGUifQ%3D%3D; laravel_session=eyJpdiI6InBWdG9NQ0RJejVpanVpRWY3TThVdHc9PSIsInZhbHVlIjoiQXVaT2xQN3h5R0VqVkFhL3ZNWng0UThsaEhKbWpUckhTVWZqMGVZRGVmd3d0dW50UHErdytYUnp4MWJndlhEeiIsIm1hYyI6IjZlYTljYzM3ZDZiOWQ1MmE5YWVkM2RhOGI5MjZjNWEyYzZhYTAyMzM3NjMwNzE4YmIzMzhiZWQyNDk4NTlkNmEifQ%3D%3D; IC_ViewCounter_www.barchart.com=9'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = json.loads(response.content)
    data_count = data['count']
    total_alpha = 0.0
    
    for obj in data['data']:
        alpha = obj['weightedAlpha'].split("+")[1]
        total_alpha = total_alpha + float(alpha)

    sector_alpha = total_alpha / data_count

    sector_data = {"sector-alpha" : sector_alpha}

    return sector_data

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


def getHistoricalData(companyCode):
    url = "https://alpha-vantage.p.rapidapi.com/query"

    querystring = {"function":"TIME_SERIES_WEEKLY","symbol":companyCode,"datatype":"csv"}

    headers = {
        'x-rapidapi-key': "5a71a248c1mshec5ac249ab63653p1e7a54jsnf4f122a5edee",
        'x-rapidapi-host': "alpha-vantage.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response

companyCode = input("Enter company's stock market code: ")
print(getSectorData(companyCode))
print("The current price of " + str(getName(companyCode)) + " is: $"+str(livePrice(companyCode))+" per share.")
finData = getFinData(companyCode)
industry = str(input("Enter company's industry from http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/pedata.html : "))
evalPeRatios(finData, industry)
freeCashFlows = getCashFlows(companyCode)
evalCashFlows(freeCashFlows)
historicalData = getHistoricalData(companyCode)




print("Short term investment score: " + str(shortScore))
print("Long term investment score: " + str(longScore))