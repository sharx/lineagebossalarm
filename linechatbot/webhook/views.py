from django.shortcuts import render

# Create your views here.
import base64
import hashlib
import hmac
from django.http import JsonResponse

channel_secret = '2f97d3e3a877f6d13a8407793fa1caf5' # Channel secret string
channel_id = '2006537537' # Channel ID string

def webhook(request):
    if request.method == 'POST':
        request.headers['X-Line-Signature']
        # Request body string
        body = request.body
        hash = hmac.new(channel_secret.encode('utf-8'), body.encode('utf-8'), hashlib.sha256).digest()
        signature = base64.b64encode(hash)
        if signature == request.headers['X-Line-Signature']:
            print('=============Log=============\nSignature is valid')
        else:
            print('=============Log=============\nSignature is invalid')
        

        #return a json response, status code 200
        return JsonResponse({'status': 'true'}, status=200)