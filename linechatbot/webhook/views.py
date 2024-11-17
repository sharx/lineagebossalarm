from django.shortcuts import render
# Create your views here.
import re
import json
import base64
import hashlib
import hmac
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Boss, LineGroup, KillRecord
#submit on mac
channel_secret = '2f97d3e3a877f6d13a8407793fa1caf5' # Channel secret string
channel_id = '2006537537' # Channel ID string
access_token = 'QbASYEKbRgwRXr5PbEXyBw4L/J9UASMbFpYnTSj3q2e6PBo0HhULDq9ZbToYuRG79xuwcmXSmsDZCcNi1z0HB0nQ1UVV8jaaQnRO6SphCfvlWxZ5JyjFu22YMXiv4yobgX4fGqUqRkZyWe9Sq0qP5wdB04t89/1O/w1cDnyilFU='

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
    if request.method == 'POST':
        #request.headers['X-Line-Signature']

        # Request body string
        body = request.body.decode('utf-8')
        hash = hmac.new(channel_secret.encode('utf-8'), request.body, hashlib.sha256).digest()
        if signature_validation(request.headers, request.body):
            #signature is valid, process the message.
            #if the text in the body is in text format and as format 'k boss_name time(mmss)', then add the boss name and kill time to the database
            json_data = json.loads(body) #convert the body to json format
            text = json_data['events'][0]['message']['text']
            reply_token = json_data['events'][0]['replyToken'] 
            type = json_data['events'][0]['message']['type']
            if text != "":
                print('=============Log=============\nMessage received')
                print(json_data)
                #if the text is in the format 'k boss_name time(mmss)', then add the boss name and kill time to the database
                """if re.match(r'^k \s+ \d{4}$', text):
                    #get the boss name and kill time
                    boss_name = text.split(' ')[1]
                    kill_time = text.split(' ')[2]
                    #get the boss object. if boss_name in Boss.boss_name or in Boss.slug.split(';'), then get the boss object
                    boss = Boss.objects.get(boss_name=boss_name)
                    #get the line group object
                    line_group = LineGroup.objects.get(group_id=json_data['events'][0]['source']['groupId'])
                    #create a kill record object
                    kill_record = KillRecord(boss=boss, line_group=line_group)
                    kill_record.save()
                    #update the respond time of the boss
                    boss.respond_time += 1
                    boss.save()
                    #return a json response, status code 200
                    return JsonResponse({'status': 'true'}, status=200)"""
        

        #return a json response, status code 200
        return JsonResponse({'status': 'true'}, status=200)
    else:
        #return a json response, status code 405
        return JsonResponse({'status': 'false'}, status=405)