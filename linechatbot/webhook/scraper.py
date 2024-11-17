#scrape the data from the website 
import requests
from bs4 import BeautifulSoup as bs
import re
import json
import os

def getLinwServers():
    url = 'https://trade.ssatem.com/api/v1/nc/linwServer?locale=zh-TW'
    response = requests.get(url)
    data = response.json()
    servers = []
    if response.status_code == 200:
        #request success
        for server in data["data"]:
            servers.append({"serverID": str(server["gameServerId"]), "serverName": server["gameServerName"]})
        return servers
    else:
        #error
        print("Error: Cannot get server list")
        print(f"Error code: {response.status_code} : {data['message']}")
        return None

def getLinwItems():
    url = 'https://trade.ssatem.com/api/v1/nc/linwItem?locale=zh-TW'
    response = requests.get(url)
    data = response.json()
    items = []
    if response.status_code == 200:
        #request success
        for item in data["data"]:
            items.append({"itemID": str(item["gameItemId"]), "itemName": item["gameItemName"]})
        return items
    else:
        #error
        print("Error: Cannot get item list")
        print(f"Error code: {response.status_code} : {data['message']}")
        return None

def linwGoodsSearch(gameItemName, serverId, enchantValues):
    serverIds = getLinwServers()
    if serverIds and any(serverId in s["serverID"] for s in serverIds):
        #if serverId is in the serverIds.serverID
        serverId = serverId
    elif serverIds and not any(serverId in s["serverID"] for s in serverIds):
        #serverId is not in the serverIds.serverID
        return { "status_code": 500, "status_text": "錯誤: 物價網站無法連線" }
    else:
        #serverIds is empty
        serverId = "99999"

    itemIds = getLinwItems()
    if itemIds and any(gameItemID in i["itemID"] for i in itemIds):
        #if gameItemID is in the itemIds.itemID
        gameItemID = gameItemID
    elif itemIds and not any(gameItemID in i["itemID"] for i in itemIds):
        #gameItemID is not in the itemIds.itemID
        return { "status_code": 500, "status_text": f"錯誤: 找不到物品名稱 {gameItemName}" }
    else:
        #no response from getLinwItems()
        return { "status_code": 500, "status_text": "錯誤: 物價網站無法連線" }

    
    url = f'https://trade.ssatem.com/api/v1/nc/linwGoods?linwGoodsSearchId=&locale=zh-TW&linwServerId={serverId}&linwItemId={gameItemID}&enchantValues={enchantValues}&sort=lowPrice&page=1'
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        #request success
        print("Success: Data is successfully scraped")
        return { "status_code": response.status_code, "status_text": "查詢成功", "data_count": len(data["data"]["content"]), "data": data["data"]["content"] }
        
    elif response.status_code == 429:
        #too many requests
        print("Error: Authentication session is not available. Too many requests")
        return { "status_code": response.status_code, "status_text": "錯誤: 物價網站連線數過多，30秒自動重試，若仍無法連線請稍後再試" }
    else:
        #unknown error
        print("Error: Unknown error")
        return { "status_code": response.status_code, "status_text": data["message"] }