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
        'x-xsrf-token': 'eyJpdiI6IlNSU1prbld3Y1dFa0Z3SHJaU1FZd3c9PSIsInZhbHVlIjoiVUpUajVZdnNDYmgzaFJ5Y0dHeFBHR2ZTT2JqM2ttZlozU3ZSajRRY1lxQ0srUDFpcHBZbmF6QmJWVGtZdmVUNCIsIm1hYyI6IjhmMjc0YzBmNDk5NmI1NGFjMWExNDA0MmYwOWEyYTkxZTkwYzU0ZDEzNTJmY2RlOWY2ZDZhZjQxMmZiNDEyYjgifQ==',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.barchart.com/stocks/sectors/rankings?symbol=' + companyCode,
        'accept-language': 'en-US,en;q=0.9',
        'cookie': '_gcl_au=1.1.1480181004.1610999181; _ga=GA1.2.2111207041.1610999181; usprivacy=1---; __qca=P0-1677819782-1610999185069; _admrla=2.0-a304f9ab-a6ab-6eae-1404-0f39ecdf7bb2; _pbjs_userid_consent_data=3524755945110770; _pubcid=2d01dcac-61e6-4fc9-9c1b-98812baddf01; pbjs-unifiedid=%7B%22TDID%22%3A%22eca9fe6c-cc0b-42d8-b13f-6fd4eeb9aea1%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222020-12-18T20%3A15%3A47%22%7D; idl_env=AvQSGFJO8RUPzSS0fgIFuNuCuG0zmCB_JhZoctwVTeYMb-ub1IFqvTEupYdR8IYycoFlRMNr4cMApaX2iGlFXdQlMQT3tDdwx0aTf7V_OrFPrNZE1Qu1BUtpi3_6Y2D4Qsz8juhlzMtyK5OUbefSW6QhG9xYYcbFcLwt5FOSeUzWZzUuurzvF7f0746AnqL8SmEzIBd2QZilVDkElLahVav4O1UTN8NpFx5Ilizm9zBBFjUoz6-Sn3kXASDImqzduX2WCxnMBEQnRu-etw-4X2VYYp_LTPpnFwDyDEaylymReWTIcw; cto_bundle=85drx19TSWE1cU5BYzUyOERRcXByWkxxOVkwTUdNdGVuNnJCNHhoUU5CcWIzQzFSTFVhVDFlRjE5NUlBQjd4N0FxSDRjeVdic2tWSmdmcVpFc0I0OHo3NnY3aktFb1BjclB0elRva3VjWDBTR2V6a1BxRmw3SWVDRFclMkZIU01wQkc5Z0l6Zmlyb0NjY0FCdCUyRjBwZWsyNkliYndRJTNEJTNE; cto_bidid=7Gtu5F95NzBnNHlBWDNjMkJ0T3Y0ck9yWVdvbkQ2b3lJakJjZG9EV0QwUGVYemtCQ0tLbXV4SlVCWExkYVJ4MXlsRnMxZGwyVnp6cnRrS0htRGpRbU0lMkZaMk4lMkZoNnQzNm5HdVFhJTJGVktDMlFWWHQ1byUzRA; fc=%7B%22NjI4fm51bGxfbnVsbH4yOTc0OjMwMjk3NzU%22%3A%221%3A1611092692165%22%7D; pv=%7B%22d%22%3A%224%3A1611000947202%22%7D; __gads=ID=0bd151c279f68900:T=1611099398:S=ALNI_Masyn3wMvj4at7muwWT4jotsCPNXw; _ccm_inf=1; CRISPSUBNO=; cto_bundle=iJY7Jl9TSWE1cU5BYzUyOERRcXByWkxxOVl6MlZZS1ZnZlR0aUFBJTJGTms4JTJCVVJvdFRaYlJhM3F1TGxzcGx0RHNScmxQRWNmMDJuSkxRWWt1b2VTWlE4MzlOUk5landHQjg0bGdJNlhZd2F0UlVSVFhqbHZoNldyZWRDMDVlVjElMkZBQlU1OHNIemQ5bWdTeThaekduRkZ6c3RDQVElM0QlM0Q; cto_bundle=iJY7Jl9TSWE1cU5BYzUyOERRcXByWkxxOVl6MlZZS1ZnZlR0aUFBJTJGTms4JTJCVVJvdFRaYlJhM3F1TGxzcGx0RHNScmxQRWNmMDJuSkxRWWt1b2VTWlE4MzlOUk5landHQjg0bGdJNlhZd2F0UlVSVFhqbHZoNldyZWRDMDVlVjElMkZBQlU1OHNIemQ5bWdTeThaekduRkZ6c3RDQVElM0QlM0Q; market=eyJpdiI6IlM0eXltZlNjNENhaGEwbU1uWUM1c1E9PSIsInZhbHVlIjoiRHViWHV1cHZkdjdMMUNPRE1VZ0c0dz09IiwibWFjIjoiNTY1MzkyN2EzYzBiNGMxODRjZjFiNWY1MDgzYjkxNjE2OTNlYWQ2OTMwOTQ0MGEwZWYyODQxN2ExMTUzYTdjMiJ9; bull-puts-01272021PageView=1; bull-puts-01272021WebinarClosed=true; _gid=GA1.2.759695256.1611356924; IC_ViewCounter_www.barchart.com=2; _awl=2.1611356955.0.4-6dfa3ca-a304f9aba6ab6eae14040f39ecdf7bb2-6763652d75732d6561737431-600b5b15-0; laravel_token=eyJpdiI6InZZMXZ4T2d2MUNQd01aMEx0N2N0b2c9PSIsInZhbHVlIjoiQ0pDeFFnL1YxS3lDbmJ3TDg0QkJMZm9UU1RCMS9IMEMxT1FSSVFWNEtaajBCS2JOdC92Z3dod0lmN2VPSlJRa3ZXTlIzMVZ6WFBXY0kwcG10NThqQ2F2M2NjVXUyNFg4Tm5mSHlLTzMxR0ZaR29QRVdSWWpGNnZQcldjbjAxTFlBcFVDWjNtd1oxcHNpTFVyblRxUVU1bWdJeC82ckNTV3FUSEd5bkNRV0VkSmdaV1grVmJUdVI0c0lxb0FaTG5jWXE1Q2Q4dzZ1UUxMOWh1eG91YVF6VURFYlRqcVBGZW40N09melg0cXBpNm55VWNDbXhqQlN5SFE4b2JvM1IyZSIsIm1hYyI6IjgzNWRhNmUwYWZlZGIwYWU2N2U2OTAzMzQ0MTY0MWJmY2RmZmY2ZjgyMmI5OWNmMzQzNjQ2OTUwNzZkNDIxNTgifQ%3D%3D; XSRF-TOKEN=eyJpdiI6IlNSU1prbld3Y1dFa0Z3SHJaU1FZd3c9PSIsInZhbHVlIjoiVUpUajVZdnNDYmgzaFJ5Y0dHeFBHR2ZTT2JqM2ttZlozU3ZSajRRY1lxQ0srUDFpcHBZbmF6QmJWVGtZdmVUNCIsIm1hYyI6IjhmMjc0YzBmNDk5NmI1NGFjMWExNDA0MmYwOWEyYTkxZTkwYzU0ZDEzNTJmY2RlOWY2ZDZhZjQxMmZiNDEyYjgifQ%3D%3D; laravel_session=eyJpdiI6IkVjbldydXk4N1BQR1RsK1FMQW9xOEE9PSIsInZhbHVlIjoibjdXZlRWaHQvUDg3U0pmM1RCSllibWNuS3JWOTJXUHlRTE5pMFQ1Z3lUSGtQcjZ1RTRZWStBVkFnTTlqR2hMSSIsIm1hYyI6IjM2YWUxZjVjOTM0ODEzZGQ4ZTQ2NDAwNjdiY2E0OWVlODMyYWIyNjVmNGMzZTc1YjgwOGI0MDc1NWNjZjY1YmMifQ%3D%3D; _gat_UA-2009749-51=1'
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
        'x-xsrf-token': 'eyJpdiI6IlNSU1prbld3Y1dFa0Z3SHJaU1FZd3c9PSIsInZhbHVlIjoiVUpUajVZdnNDYmgzaFJ5Y0dHeFBHR2ZTT2JqM2ttZlozU3ZSajRRY1lxQ0srUDFpcHBZbmF6QmJWVGtZdmVUNCIsIm1hYyI6IjhmMjc0YzBmNDk5NmI1NGFjMWExNDA0MmYwOWEyYTkxZTkwYzU0ZDEzNTJmY2RlOWY2ZDZhZjQxMmZiNDEyYjgifQ==',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.barchart.com/stocks/quotes/' + company_sector_symbol + '/components/' + companyCode,
        'accept-language': 'en-US,en;q=0.9',
        'cookie': '_gcl_au=1.1.1480181004.1610999181; _ga=GA1.2.2111207041.1610999181; usprivacy=1---; __qca=P0-1677819782-1610999185069; _admrla=2.0-a304f9ab-a6ab-6eae-1404-0f39ecdf7bb2; _pbjs_userid_consent_data=3524755945110770; _pubcid=2d01dcac-61e6-4fc9-9c1b-98812baddf01; pbjs-unifiedid=%7B%22TDID%22%3A%22eca9fe6c-cc0b-42d8-b13f-6fd4eeb9aea1%22%2C%22TDID_LOOKUP%22%3A%22TRUE%22%2C%22TDID_CREATED_AT%22%3A%222020-12-18T20%3A15%3A47%22%7D; idl_env=AvQSGFJO8RUPzSS0fgIFuNuCuG0zmCB_JhZoctwVTeYMb-ub1IFqvTEupYdR8IYycoFlRMNr4cMApaX2iGlFXdQlMQT3tDdwx0aTf7V_OrFPrNZE1Qu1BUtpi3_6Y2D4Qsz8juhlzMtyK5OUbefSW6QhG9xYYcbFcLwt5FOSeUzWZzUuurzvF7f0746AnqL8SmEzIBd2QZilVDkElLahVav4O1UTN8NpFx5Ilizm9zBBFjUoz6-Sn3kXASDImqzduX2WCxnMBEQnRu-etw-4X2VYYp_LTPpnFwDyDEaylymReWTIcw; cto_bundle=85drx19TSWE1cU5BYzUyOERRcXByWkxxOVkwTUdNdGVuNnJCNHhoUU5CcWIzQzFSTFVhVDFlRjE5NUlBQjd4N0FxSDRjeVdic2tWSmdmcVpFc0I0OHo3NnY3aktFb1BjclB0elRva3VjWDBTR2V6a1BxRmw3SWVDRFclMkZIU01wQkc5Z0l6Zmlyb0NjY0FCdCUyRjBwZWsyNkliYndRJTNEJTNE; cto_bidid=7Gtu5F95NzBnNHlBWDNjMkJ0T3Y0ck9yWVdvbkQ2b3lJakJjZG9EV0QwUGVYemtCQ0tLbXV4SlVCWExkYVJ4MXlsRnMxZGwyVnp6cnRrS0htRGpRbU0lMkZaMk4lMkZoNnQzNm5HdVFhJTJGVktDMlFWWHQ1byUzRA; fc=%7B%22NjI4fm51bGxfbnVsbH4yOTc0OjMwMjk3NzU%22%3A%221%3A1611092692165%22%7D; pv=%7B%22d%22%3A%224%3A1611000947202%22%7D; __gads=ID=0bd151c279f68900:T=1611099398:S=ALNI_Masyn3wMvj4at7muwWT4jotsCPNXw; _ccm_inf=1; CRISPSUBNO=; cto_bundle=iJY7Jl9TSWE1cU5BYzUyOERRcXByWkxxOVl6MlZZS1ZnZlR0aUFBJTJGTms4JTJCVVJvdFRaYlJhM3F1TGxzcGx0RHNScmxQRWNmMDJuSkxRWWt1b2VTWlE4MzlOUk5landHQjg0bGdJNlhZd2F0UlVSVFhqbHZoNldyZWRDMDVlVjElMkZBQlU1OHNIemQ5bWdTeThaekduRkZ6c3RDQVElM0QlM0Q; cto_bundle=iJY7Jl9TSWE1cU5BYzUyOERRcXByWkxxOVl6MlZZS1ZnZlR0aUFBJTJGTms4JTJCVVJvdFRaYlJhM3F1TGxzcGx0RHNScmxQRWNmMDJuSkxRWWt1b2VTWlE4MzlOUk5landHQjg0bGdJNlhZd2F0UlVSVFhqbHZoNldyZWRDMDVlVjElMkZBQlU1OHNIemQ5bWdTeThaekduRkZ6c3RDQVElM0QlM0Q; market=eyJpdiI6IlM0eXltZlNjNENhaGEwbU1uWUM1c1E9PSIsInZhbHVlIjoiRHViWHV1cHZkdjdMMUNPRE1VZ0c0dz09IiwibWFjIjoiNTY1MzkyN2EzYzBiNGMxODRjZjFiNWY1MDgzYjkxNjE2OTNlYWQ2OTMwOTQ0MGEwZWYyODQxN2ExMTUzYTdjMiJ9; bull-puts-01272021PageView=1; bull-puts-01272021WebinarClosed=true; _gid=GA1.2.759695256.1611356924; IC_ViewCounter_www.barchart.com=2; _awl=2.1611356955.0.4-6dfa3ca-a304f9aba6ab6eae14040f39ecdf7bb2-6763652d75732d6561737431-600b5b15-0; laravel_token=eyJpdiI6InZZMXZ4T2d2MUNQd01aMEx0N2N0b2c9PSIsInZhbHVlIjoiQ0pDeFFnL1YxS3lDbmJ3TDg0QkJMZm9UU1RCMS9IMEMxT1FSSVFWNEtaajBCS2JOdC92Z3dod0lmN2VPSlJRa3ZXTlIzMVZ6WFBXY0kwcG10NThqQ2F2M2NjVXUyNFg4Tm5mSHlLTzMxR0ZaR29QRVdSWWpGNnZQcldjbjAxTFlBcFVDWjNtd1oxcHNpTFVyblRxUVU1bWdJeC82ckNTV3FUSEd5bkNRV0VkSmdaV1grVmJUdVI0c0lxb0FaTG5jWXE1Q2Q4dzZ1UUxMOWh1eG91YVF6VURFYlRqcVBGZW40N09melg0cXBpNm55VWNDbXhqQlN5SFE4b2JvM1IyZSIsIm1hYyI6IjgzNWRhNmUwYWZlZGIwYWU2N2U2OTAzMzQ0MTY0MWJmY2RmZmY2ZjgyMmI5OWNmMzQzNjQ2OTUwNzZkNDIxNTgifQ%3D%3D; XSRF-TOKEN=eyJpdiI6IlNSU1prbld3Y1dFa0Z3SHJaU1FZd3c9PSIsInZhbHVlIjoiVUpUajVZdnNDYmgzaFJ5Y0dHeFBHR2ZTT2JqM2ttZlozU3ZSajRRY1lxQ0srUDFpcHBZbmF6QmJWVGtZdmVUNCIsIm1hYyI6IjhmMjc0YzBmNDk5NmI1NGFjMWExNDA0MmYwOWEyYTkxZTkwYzU0ZDEzNTJmY2RlOWY2ZDZhZjQxMmZiNDEyYjgifQ%3D%3D; laravel_session=eyJpdiI6IkVjbldydXk4N1BQR1RsK1FMQW9xOEE9PSIsInZhbHVlIjoibjdXZlRWaHQvUDg3U0pmM1RCSllibWNuS3JWOTJXUHlRTE5pMFQ1Z3lUSGtQcjZ1RTRZWStBVkFnTTlqR2hMSSIsIm1hYyI6IjM2YWUxZjVjOTM0ODEzZGQ4ZTQ2NDAwNjdiY2E0OWVlODMyYWIyNjVmNGMzZTc1YjgwOGI0MDc1NWNjZjY1YmMifQ%3D%3D; _gat_UA-2009749-51=1'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = json.loads(response.content)
    data_count = data['count']
    total_alpha = 0.0
    
    for obj in data['data']:
        # print(obj)
        # print('----------')
        alpha = obj['weightedAlpha'].split("+")[1]
        total_alpha = total_alpha + float(alpha)

    sector_alpha = total_alpha / data_count

    sector_data = {"data" : {"sector-alpha" : sector_alpha, "sector-name" : company_sector_description}}

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