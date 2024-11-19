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
    #data example: [{"id":836,"locale":"zh-TW","gameServerId":15,"gameServerName":"沙哈03","gameServerShortName":"沙03"},, ...]
    servers = []
    if response.status_code == 200:
        """
        #request success
        for server in data["data"]:
            servers.append({"serverID": str(server["gameServerId"]), "serverName": server["gameServerName"]})
        return servers
        """
        return data["data"]
    else:
        #error
        print("Error: Cannot get server list")
        print(f"Error code: {response.status_code} : {data['message']}")
        return None



def getLinwItems():
    url = 'https://trade.ssatem.com/api/v1/nc/linwItem?locale=zh-TW'
    response = requests.get(url)
    data = response.json()
    #data example: [{"id":4582,"locale":"zh-TW","gameItemKey":911167,"gameItemName":"[稜鏡] 拉普 多魯嘉變身卡片",
    # "itemGradeId":6,"itemImage":"https://assets.playnccdn.com/gamedata/powerbook/linw/Item/BM_Shop_Prism_Polymorph_Mythic_inven.png",
    # "itemOptions":"[]"},
    #{"id":4578,"locale":"zh-TW","gameItemKey":911784,"gameItemName":"杰弗雷庫的尖牙",
    # "itemGradeId":6,"itemImage":"https://assets.playnccdn.com/gamedata/powerbook/linw/Item/item_Neck_Zebrequi_01.png",
    # "itemOptions":"[{\"displayValue\":\"MP恢復 +30\"},{\"displayValue\":\"最大HP +300\"},
    # {\"displayValue\":\"物理防禦力 +10\"},{\"displayValue\":\"魔法防禦力 +15\"},{\"displayValue\":\"傷害減免 +10\"},
    # {\"displayValue\":\"減少被擊延遲 10%\"},{\"displayValue\":\"沉默 抗性 +20%\"},{\"displayValue\":\"昏迷 抗性 +15%\"},
    # {\"displayValue\":\"移動 抗性 +50%\"}]"},
    # {"id":4595,"locale":"zh-TW","gameItemKey":340,"gameItemName":"死亡騎士烈炎之劍",
    # "itemGradeId":5,"itemImage":"https://assets.playnccdn.com/gamedata/powerbook/linw/Item/sword_of_death_knight.png",
    # "itemOptions":"[{\"displayValue\":\"大型目標傷害 1~25\"},{\"displayValue\":\"小型目標傷害 1~29\"},{\"displayValue\":\"命中 +6\"},
    # {\"displayValue\":\"追加傷害 +5\"},{\"displayValue\":\"STR +3\"},{\"displayValue\":\"防止武器損壞\"},{\"displayValue\":\"無視傷害減免 +4\"},
    # {\"displayValue\":\"PVP追加傷害 +8\"},{\"displayValue\":\"不死族追加傷害 1~40\"}]"}, ...]
    items = []
    if response.status_code == 200:
        #request success
        """
        for item in data["data"]:
            items.append({"itemID": str(item["id"]), "itemName": item["gameItemName"]})
        return items
        """
        return data["data"]
    else:
        #error
        print("Error: Cannot get item list")
        print(f"Error code: {response.status_code} : {data['message']}")
        return None

def linwGoodsSearch(gameItemID, gameItemName, serverName):
    """
    if serverName != "":
        servers = getLinwServers()
        if any([i["gameServerId"] for i in servers if serverName == i["serverName"]]):
            print(f"Sever name {serverName} valid")
            server_valid = True
        else:
            print(f"Sever name {serverName} invalid")
            return { "status_code": 303, "status_text": f"錯誤: 找不到伺服器名稱 {serverName}" }
    else:
        #gameServerId is empty
        print("Sever name is empty")
        server_valid = False
    
    gameServerId = "99999"
    """
    """
    items = getLinwItems()
    match_list = [i["itemID"] for i in items if gameItemName in i["itemName"]]
    if items and match_list:
        #if gameItemID is in the itemIds.itemID
        gameItemID = match_list[0]
    elif items and len(match_list)==0:
        #gameItemID is not in the itemIds.itemID
        return { "status_code": 303, "status_text": f"錯誤: 找不到物品名稱 {gameItemName}" }
    else:
        #no response from getLinwItems()
        return { "status_code": 404, "status_text": "錯誤: 物價網站無法連線" }
    """
    enchantValues = "0,+5,+7,+9"
    serverID="99999"
    url = f'https://trade.ssatem.com/api/v1/nc/linwGoods?linwGoodsSearchId=&locale=zh-TW&linwServerId={serverID}&linwItemId={gameItemID}&enchantValues={enchantValues}&sort=lowPrice&page=1'
    response = requests.get(url)
    data = response.json()
    #data example: [{"id":66738139,"linwGoodsSearchId":186982,"gameServerId":10000,"gameServerName":"潘朵拉","gameItemKey":913376,"gameItemName":"冰之女王之淚","gameItemQuantity":1,"salePrice":260,"unitPrice":260.0000,"effectiveTo":"2일 15시간","displayData":"{\"sellerWorldNo\":115}","gameItemConditions":[{"key":"EnchantLevel","type":"1","value":"0"},...]
                
    if response.status_code == 200:
        #request success
        print("Success: Data is successfully scraped")
        if data["data"]["empty"]:
            #search success, but no item on the shelf
            return { "status_code": 500, "status_text": "查詢成功: 架上暫無此物品" }
        else:
            #search success, and there are items on the shelf
            #replace the data["data"]["content"] with the items that match the serverName
            if serverName == "":
                return { "status_code": response.status_code, "status_text": "查詢成功", "data_count": len(data["data"]["content"]), "data": data["data"]["content"] }
            else:
                if any([items for items in data["data"]["content"] if items["gameServerName"] == serverName]):
                    data["data"]["content"] = [items for items in data["data"]["content"] if items["gameServerName"] == serverName]
                    return { "status_code": response.status_code, "status_text": "查詢成功", "data_count": len(data["data"]["content"]), "data": data["data"]["content"] }
                else:
                    return { "status_code": 500, "status_text": f"{serverName} 交易所無此物品 - {gameItemName}", "data_count": len(data["data"]["content"]), "data": data["data"]["content"] }
                
    elif response.status_code == 429:
        #too many requests
        print("Error: Authentication session is not available. Too many requests")
        return { "status_code": response.status_code, "status_text": "錯誤: 物價網站連線數過多，30秒自動重試，若仍無法連線請稍後再試" }
    else:
        #unknown error
        print("Error: Unknown error")
        return { "status_code": response.status_code, "status_text": data["message"] if data["message"] else str(data) }