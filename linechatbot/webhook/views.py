from django.shortcuts import render
# Create your views here.
import re
import json
import base64
import hashlib
import hmac
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, F
from .models import Boss, LineGroup, KillRecord
from .scraper import linwGoodsSearch, getLinwServers, getLinwItems
from pprint import pprint

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

channel_secret = '2f97d3e3a877f6d13a8407793fa1caf5' # Channel secret string
channel_id = '2006537537' # Channel ID string
access_token = 'QbASYEKbRgwRXr5PbEXyBw4L/J9UASMbFpYnTSj3q2e6PBo0HhULDq9ZbToYuRG79xuwcmXSmsDZCcNi1z0HB0nQ1UVV8jaaQnRO6SphCfvlWxZ5JyjFu22YMXiv4yobgX4fGqUqRkZyWe9Sq0qP5wdB04t89/1O/w1cDnyilFU='

configuration = Configuration(access_token=access_token)
handler = WebhookHandler(channel_secret)


def _post(self, path, endpoint=None, data=None, headers=None, timeout=None):
        url = (endpoint or self.endpoint) + path

        if headers is None:
            headers = {'Content-Type': 'application/json'}
        headers.update(self.headers)

        response = self.http_client.post(
            url, headers=headers, data=data, timeout=timeout
        )

        #self.__check_error(response)
        return response

def push_message(
            self, to, messages,
            retry_key=None, notification_disabled=False,
            custom_aggregation_units=None, timeout=None):
        """Call push message API.

        https://developers.line.biz/en/reference/messaging-api/#send-push-message

        Send messages to users, groups, and rooms at any time.

        :param str to: ID of the receiver
        :param messages: Messages.
            Max: 5
        :type messages: T <= :py:class:`linebot.models.send_messages.SendMessage` |
            list[T <= :py:class:`linebot.models.send_messages.SendMessage`]
        :param retry_key: (optional) Arbitrarily generated UUID in hexadecimal notation.
        :param bool notification_disabled: (optional) True to disable push notification
            when the message is sent. The default value is False.
        :param custom_aggregation_units: (optional) Name of aggregation unit. Case-sensitive.
            Max unit: 1
            Max aggregation unit name length: 30 characters
            Supported character types: Half-width alphanumeric characters and underscore
        :type custom_aggregation_units: str | list[str]
        :param timeout: (optional) How long to wait for the server
            to send data before giving up, as a float,
            or a (connect timeout, read timeout) float tuple.
            Default is self.http_client.timeout
        :type timeout: float | tuple(float, float)
        """
        url = "https://api.line.me/v2/bot/message/push"
        if not isinstance(messages, (list, tuple)):
            messages = [messages]

        if retry_key:
            self.headers['X-Line-Retry-Key'] = retry_key

        data = {
            'to': to,
            'messages': [message.as_json_dict() for message in messages],
            'notificationDisabled': notification_disabled,
        }

        if custom_aggregation_units is not None:
            if not isinstance(custom_aggregation_units, (list, tuple)):
                custom_aggregation_units = [custom_aggregation_units]
            data['customAggregationUnits'] = custom_aggregation_units

        self._post(
            '/v2/bot/message/push', data=json.dumps(data), timeout=timeout
        )

def signature_validation(headers, body):
    hash = hmac.new(channel_secret.encode('utf-8'), body, hashlib.sha256).digest()
    signature = base64.b64encode(hash).decode('utf-8')
    if signature == headers['X-Line-Signature']:
        print('=============Log=============\nSignature is valid')
        return True
    else:
        print('=============Log=============\nSignature is invalid')
        print('Signature: ', headers['X-Line-Signature'] )
        print('body: \n', body)
        return False

@csrf_exempt
def webhook(request):
    """
    if request.method == 'POST':
        #request.headers['X-Line-Signature']
        
        # Request body string
        body = request.body.decode('utf-8')
        if signature_validation(request.headers, request.body):
            #signature is valid, process the message.
            #if the text in the body is in text format and as format 'k boss_name time(mmss)', then add the boss name and kill time to the database
            json_data = json.loads(body) #convert the body to json format
            #json example:  {'destination': 'U43fea91f310a64a21a17504c201eeecc', 'events': [{'type': 'message', 'message': {'type': 'text', 'id': '535190510172635573', 'quoteToken': 'fmG0rnTQu5hNdjNnoAgoFZ6csW9PMOdxMjLGf2HuBmH1gmlNnAMY0gBrHiLbcW3gg2outYa3xlDwaExHGItnkxVD16nqlNnGaCcuoNnNCWyipChB5DgPGyyR6iaTkSdLfm71bioPatwkEI-MH7hdug', 'text': 'T'}, 'webhookEventId': '01JCWHGBQSC3JB74KASEPNH20C', 'deliveryContext': {'isRedelivery': False}, 'timestamp': 1731829706477, 'source': {'type': 'group', 'groupId': 'Cdcd54d6760aea051210de8f9b253a1dd', 'userId': 'Ubad400ab80fd2a636e6a7cd511a0cdf0'}, 'replyToken': '1d48f923bb55416d9a2678387476a6c8', 'mode': 'active'}]}
            text = json_data['events'][0]['message']['text']
            replyToken = json_data['events'][0]['replyToken'] 
            msgType = json_data['events'][0]['message']['type']
            srcType = json_data['events'][0]['source']['type']
            groupId = json_data['events'][0]['source']['groupId']
            if text != "":
                print('=============Log=============\nMessage received')
                #if the text is in the format 'k boss_name time(mmss)', then add the boss name and kill time to the database
                if re.match(r'^k \s+ \d{4}$', text):
                    #get the boss name and kill time
                    boss_name = text.split(' ')[1]
                    kill_time = text.split(' ')[2]
                    #get the boss object. if boss_name in Boss.boss_name or in Boss.slug.split(';'), then get the boss object
                    #boss.slug example: 'boss1;boss2;boss3'
                    #query the boss object if boss_name exactly match the list elements in boss.slug.split(';')
                    boss_first_match = Boss.objects.filter(slug__contains=boss_name)
                    if boss_first_match.count() == 0:
                        #no boss name match, ignore the message
                        print('=============Log=============\nNo boss name match')
                        boss = None
                    elif boss_first_match.count() == 1:
                        #boss match only one, add the kill record
                        boss = boss_first_match[0]
                    else:
                        #boss match more than one, boss_name must match the slug.split(";") exactly
                        for ele in boss_first_match:
                            if boss_name in boss.slug.split(';'):
                                boss = ele

                    #if kill_time is in the format 'mmss', mm is minute, ss is second, 0 < mm < 24, 0 < ss < 60. if true, then add the kill record
                    mm = int(kill_time[0:2])
                    ss = int(kill_time[2:4])
                    if mm <24 and mm>=0 and ss < 60 and ss >= 0:
                        kill_time = datetime.now().replace(hour=mm, minute=ss, second=0, microsecond=0)
                        respond_time = kill_time + timedelta(hours=boss.respond_duration)
                        kill_record, created = KillRecord.objects.get_or_create(boss=boss, line_group=LineGroup.objects.get_or_create(group_id=groupId))
                        if created:
                            print('=============Log=============\nKill record created\nBoss: %s\nGroup: %s', boss.boss_name, groupId)
                        else:
                            kill_record.responds_time = respond_time
                            kill_record.save()
                            print('=============Log=============\nKill record updated\nBoss: %s\nGroup: %s\nRespond time: %s'(boss.boss_name, groupId, respond_time.strftime("%Y-%m-%d %H:%M")) )
                    else:
                        #kill time is not in the correct format, ignore the message
                        print('=============Log=============\nKill time is not in the correct format. Received: ', kill_time)

                    
                    #return a json response, status code 200
                    return JsonResponse({'status': 'true'}, status=200)

        #return a json response, status code 200
        return JsonResponse({'status': 'true'}, status=200)
        
    else:
        #return a json response, status code 405
        return JsonResponse({'status': 'false'}, status=405)
    """
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.body.decode('utf-8')

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return JsonResponse({'status': 'false'}, status=405)

    return JsonResponse({'status': 'true'}, status=200)

def getBoss(boss_name):
    #get the boss object. if boss_name in Boss.boss_name or in Boss.slug.split(';'), then get the boss object
    #boss.slug example: 'boss1;boss2;boss3'
    #query the boss object if boss_name exactly match the list elements in boss.slug.split(';')
    boss_first_match = Boss.objects.filter(slug__contains=boss_name)
    if boss_first_match.count() == 0:
        #no boss name match, ignore the message
        print('=============Log=============\nNo boss name match')
        boss = None
    elif boss_first_match.count() == 1:
        #boss match only one, add the kill record
        boss = boss_first_match[0]
    else:
        #boss match more than one, boss_name must match the slug.split(";") exactly
        for ele in boss_first_match:
            if boss_name in ele.slug.split(';'):
                boss = ele
    return boss

def processRegisterKillTime(request_kill_time):
    #if the text in the body is in text format and as format 'k boss_name time(mmss)', then add the boss name and kill time to the database
    if request_kill_time and request_kill_time != "":
        mm = int(request_kill_time[0:2])
        ss = int(request_kill_time[2:4])
        #if kill_time is in the format 'mmss', mm is minute, ss is second, 0 < mm < 24, 0 < ss < 60. if true, then add the kill record
        if mm <24 and mm>=0 and ss < 60 and ss >= 0:
            kill_time = datetime.now().replace(hour=mm, minute=ss, second=0, microsecond=0)
            if kill_time > datetime.now():
                #kill time is in the future, should be a late register in midnight. subtract 1 day from the kill time
                kill_time = kill_time - timedelta(days=1)
        else:
            #kill time is not in the correct format, ignore the message
            print('=============Log=============\nKill time is not in the correct format. Received: ', request_kill_time)
            print(f"MM SS: {mm} {ss}")
            kill_time = None
    else:
        #reqeust_kill_time is none, kill_time is now and replace second and microsecond to 0
        kill_time = datetime.now().replace(second=0, microsecond=0)
    return kill_time

def processSearchResultAndReplyMsg(text, searchResult, event, api_client):
    #find the lowest "unitPrice" and return the "gameServerName" and "unitPrice"
    if searchResult["status_text"] == "查詢成功":
        data = searchResult["data"]
        lowest_price_item = data[0]
        for item in data:
            if item["unitPrice"] < lowest_price_item["unitPrice"]:
                lowest_price_item = item
        enchantStr = "+"+str(lowest_price_item["gameItemConditions"][0]["value"]) if int(lowest_price_item["gameItemConditions"][0]["value"])>0 else ""
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=f'查詢成功 - 最低價位物品：\n{enchantStr}{lowest_price_item["gameItemName"]}\n最低單位價格：{lowest_price_item["unitPrice"]}\n伺服器：{lowest_price_item["gameServerName"]}')]
            )
        )
    elif searchResult["status_text"].startswith("錯誤: 找不到物品名稱"):
        enteredItemName = searchResult["status_text"][:searchResult["status_text"].rfind(" ")]
        gameItems = searchResult["gameItems"]
        gameItemNames = [item["gameItemName"] for item in gameItems]
        targetItemName = searchResult["status_text"].replace("錯誤: 找不到物品名稱 ", "")
        possibleItemNames = [item for item in gameItemNames if targetItemName in item]
        replyText = f'錯誤: 找不到物品名稱\n{enteredItemName}'
        replyText += f'\n可能的物品名稱：'
        for item in possibleItemNames:
            replyText += f'\n{item}'
        
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=replyText)]
            )
        )
    else:
        err_msg = searchResult["status_text"]
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=err_msg)]
            )
        )
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        text = event.message.text
        groupId = event.source.group_id
        if re.match(r'^k', text):
            print('=============Log=============\nK Message received')
            #if the text is in the format 'k boss_name time(mmss)', then add the boss name and kill time to the database
            if re.match(r'^k [\u4e00-\u9fa5]+ \d{4}$', text) or re.match(r'^k \S+ \d{4}$', text):
                #get the boss name and kill time
                request_kill_time = text.split(' ')[2]
                boss = getBoss(text.split(' ')[1])
                kill_time = processRegisterKillTime(text.split(' ')[2])
            elif re.match(r'^k [\u4e00-\u9fa5]+$', text) or re.match(r'^k \S+$', text):
                boss = getBoss(text.split(' ')[1])
                kill_time = processRegisterKillTime(None)
            else:
                print('=============Log=============\nMessage text is not in the correct format')
                print('Message text: ', text)
                return JsonResponse({'status': 'false'}, status=405)

            if kill_time:
                respond_time = kill_time + timedelta(hours=boss.respond_duration)
            else:
                return JsonResponse({'status': 'false'}, status=405)
            
            line_group, created =LineGroup.objects.get_or_create(group_id=groupId)
            kill_record, created = KillRecord.objects.get_or_create(boss=boss, line_group = line_group)
            
            if created:
                print(f'=============Log=============\nKill record created\nBoss: {boss.boss_name}\nGroup: {groupId}')
            else:
                kill_record.responds_time = respond_time
                kill_record.save()
                print(f'=============Log=============\nKill record updated\nBoss: {boss.boss_name}\nGroup: {groupId}\nRespond time: {respond_time}' )
            
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='擊殺%s，將在%s重生，重生3分鐘前通知' % (boss.boss_name, respond_time.strftime("%H:%M")))]
                )
            )
        elif re.match(r'^新增首領', text):
            print('=============Log=============\nAdd Message received')
            #if the text is in the format 'add boss_name', then add the boss name and respond_duration to the database
            if len(text.split(' ')) == 3:
                boss_str = text.split(' ')[1]
                respond_duration = int(text.split(' ')[2])

            else:
                print('=============Log=============\nMessage text is not in the correct format')
                print('Message text: ', text)
                return JsonResponse({'status': 'false'}, status=405)
        elif text == '時刻表':
            print('=============Log=============\nMenu request received')
            #if the text is '時刻表', then return the help message
            help_message = '時刻表指令\n-登記擊殺時間：k 首領名稱(可簡稱) xxyy(小時分鐘) - 註冊擊殺時間\n範例：k 麥肯 2138\n\n-註冊首領屬性：\n新增首領 首領名稱,簡稱(可多個) 重生時間 - 新增首領名稱及重生時間\n範例：\n新增首領 飛龍3,龍3,3 4\n\n時刻表 - 顯示此訊息'
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=help_message)]
                )
            )
            pass
        elif re.match(r'^查詢物價', text):
            print(f'=============Log=============\nSearch item message received: {text}')
            servers = getLinwServers()
            gameItems = getLinwItems()
            #阿修傳說咒語書選擇箱Ⅲ
            text_suffix = text.replace('查詢物價 ', '')
            if len(text_suffix.split(' ')) > 1:
                # if the text is in the format '查詢物價 物品名稱 ???'
                # examine if ??? is a valid server name. 
                # if valid, then search the item with the serverId
                # if invalid, then search the item with serverId "99999"
                
                for server in servers:
                    if text_suffix.split(' ')[-1] == server["gameServerName"] or text_suffix.split(' ')[-1] == server["gameServerShortName"]:
                        serverName_valid = True
                        gameServerName = text_suffix.split(' ')[-1]
                        gameServerId = server["gameServerId"]
                        break
                    else:
                        serverName_valid = False
                for gameItem in gameItems:
                    if text_suffix[:text_suffix.rfind(' ')] == gameItem["gameItemName"]:
                        gameItemName_valid = True
                        gameItemID = gameItem["id"]
                        gameItemName = gameItem["gameItemName"]
                        break
                    else:
                        gameItemName_valid = False

                if serverName_valid and gameItemName_valid:
                    print('=============Log=============\nServer name and gameItemName_valid is valid')
                    gameItemName = text_suffix[:text_suffix.rfind(' ')]
                    searchResult = linwGoodsSearch(gameItemID, gameItemName, gameServerName)
                    processSearchResultAndReplyMsg(text, searchResult, event, api_client)
                elif not serverName_valid:
                    print('=============Log=============\nServer name is invalid')
                    searchResult = { "status_code": 404, "status_text": f"錯誤: 找不到伺服器 {gameServerName}" }
                    processSearchResultAndReplyMsg(text, searchResult, event, api_client)
                elif not gameItemName_valid:
                    print('=============Log=============\nGameItemName is invalid')
                    searchResult = { "status_code": 404, "status_text": f"錯誤: 找不到物品名稱 {gameItemName}" }
                    processSearchResultAndReplyMsg(text, searchResult, event, api_client)
                else:
                    print('=============Log=============\nMessage text is not in the correct goods search format. pinpoint 1')
                    print('Message text: ', text)
                    return JsonResponse({'status': 'false'}, status=405)
            elif len(text_suffix.split(' ')) == 1:
                # if the text is in the format '查詢物價 物品名稱'
                # search the item with serverId "99999"
                for gameItem in gameItems:
                    if text_suffix == gameItem["gameItemName"]:
                        gameItemName_valid = True
                        gameItemID = gameItem["id"]
                        gameItemName = gameItem["gameItemName"]
                        break
                    else:
                        gameItemName_valid = False
                if gameItemName_valid:
                    print('=============Log=============\nServer name and gameItemName_valid is valid')
                    searchResult = linwGoodsSearch(gameItemID, gameItemName, "")
                    processSearchResultAndReplyMsg(text, searchResult, event, api_client)
                else:
                    print('=============Log=============\nGameItemName is invalid')
                    searchResult = { "status_code": 404, "status_text": f"錯誤: 找不到物品名稱 {text_suffix}", "gameItems": gameItems }
                    processSearchResultAndReplyMsg(text, searchResult, event, api_client)
                
            else:
                print('=============Log=============\nMessage text is not in the correct goods search format. pinpoint 2')
                print('Message text: ', text)
                return JsonResponse({'status': 'false'}, status=405)
        else:
            print('=============Log=============\nMessage text is empty')
            #return a json response, status code 200
            return JsonResponse({'status': 'true'}, status=200)
        
