from django.shortcuts import render
from django.http import HttpResponse,Http404
import requests
import json
from django.shortcuts import redirect

from .models import Merchant,menuItem,Order,OrderItem
from django.views.decorators.csrf import csrf_exempt



# Create your views here.
def merchant(request):
    context = {
    }
    return render(request, 'merchantapp/merchantlogin.html', context)

def merchantlogin(request):
    email = request.POST['email']
    password = request.POST['password']
    lat = request.POST['lat']
    lng = request.POST['lng']
    zomatoid = request.POST['zomatoid']

    request.session['email'] = str(email)
    request.session['lat'] = str(lat)
    request.session['lng'] = str(lng)

    print email
    print password
    print lat
    print lng
    print zomatoid

    try:
		#auth
		# headers = {'X-API-TOKEN': 'your_token_here'}
		payload = {'client_id': 'PLKVUJC3TP', 'client_secret': 'b651c852-5c48-4125-8e32-97cd631dcea2', 'grant_type':'client_credentials','access_lifetime':'7200'}
		r = requests.post("https://sandbox.unocoin.co/oauth/token", data=payload)
		pjson = json.loads(r.text)
		access_token = pjson['access_token']
		request.session['access_token'] = access_token
		print 'access_token = ',access_token
		request.session['access_token'] = str(access_token)

		# Authorised auth
		url = "https://sandbox.unocoin.co/api/v1/authentication/signin"

		payload = "signinsecpwd=999999&email_id="+str(email)+"&signinpassword="+password+"&redirect_uri=https%3A%2F%2Fa74914f8.ngrok.io&response_type=code&client_id=PLKVUJC3TP&scope=all"
		headers = {
		    'authorization': "Bearer "+str(access_token),
		    'content-type': "application/x-www-form-urlencoded",
		    'cache-control': "no-cache",
		    'postman-token': "320443d5-93a4-00bb-2a57-81a080a4b1bd"
		    }

		response = requests.request("POST", url, data=payload, headers=headers)
		print response.text
		pjson = json.loads(response.text)
		code = pjson['code']
		print code
		request.session['code'] = str(code)

		#authorized access token
		url = "https://sandbox.unocoin.co/oauth/token"
		payload = "client_id=PLKVUJC3TP&client_secret=b651c852-5c48-4125-8e32-97cd631dcea2&code="+code+"&redirect_uri=https%3A%2F%2Fa74914f8.ngrok.io&grant_type=authorization_code&access_lifetime=100000"
		headers = {
		    'content-type': "application/x-www-form-urlencoded",
		    'cache-control': "no-cache",
		    'postman-token': "a1cbd922-ac98-50e7-0eed-d150c255a9c0"
		    }
		response = requests.request("POST", url, data=payload, headers=headers)
		pjson = json.loads(response.text)
		authorized_access_token = pjson['access_token']
		request.session['authorized_access_token'] = str(authorized_access_token)
		print str(authorized_access_token)
		#getting merchant bitcoin details
		url = "https://sandbox.unocoin.co/api/v1/wallet/bitcoinaddress"
		headers = {
		'content-type': "application/json",
		'authorization': "Bearer "+str(authorized_access_token),
		'cache-control': "no-cache",
		'postman-token': "ab0e8f43-71d2-86fb-d778-35cf50e83492"
		}

		response = requests.request("POST", url, headers=headers)
		print response.text
		pjson = json.loads(response.text)
		#print(response.text)
		b_addr = pjson['bitcoinaddress']
		Merchant(bit_addr=b_addr,merchant_id=zomatoid,merchant_email=email).save()
    except:
        HttpResponse('Invalid login.<a href="a74914f8.ngrok.io/merchantapp">Login</a>')
    context = {
        'lat':lat,
        'lng':lng,
    }
    return render(request, 'merchantapp/selectrestaurant.html', context)



def test(request):
    context = {
    }
    return render(request, 'merchantapp/selectrestaurant.html', context)


def merchant_order(request):
    context = {
    }
    return render(request, 'merchantapp/login.html', context)

def order(request):
    email = request.POST['email']
    password = request.POST['password']
    zomatoid = request.POST['zomatoid']
    request.session['email'] = str(email)
    request.session['zomatoid'] = zomatoid

    print email
    print password

    #auth
    # headers = {'X-API-TOKEN': 'your_token_here'}
    payload = {'client_id': 'PLKVUJC3TP', 'client_secret': 'b651c852-5c48-4125-8e32-97cd631dcea2', 'grant_type':'client_credentials','access_lifetime':'7200'}
    r = requests.post("https://sandbox.unocoin.co/oauth/token", data=payload)
    pjson = json.loads(r.text)
    access_token = pjson['access_token']
    request.session['access_token'] = access_token
    print 'access_token = ',access_token
    request.session['access_token'] = str(access_token)

    # Authorised auth
    url = "https://sandbox.unocoin.co/api/v1/authentication/signin"

    payload = "signinsecpwd=999999&email_id="+str(email)+"&signinpassword="+password+"&redirect_uri=https%3A%2F%2Fa74914f8.ngrok.io&response_type=code&client_id=PLKVUJC3TP&scope=all"
    headers = {
        'authorization': "Bearer "+str(access_token),
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'postman-token': "320443d5-93a4-00bb-2a57-81a080a4b1bd"
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    print response.text
    pjson = json.loads(response.text)
    code = pjson['code']
    print code
    request.session['code'] = str(code)

    return redirect('refresh_order')

            # return HttpResponse('Invalid login.<a href="a74914f8.ngrok.io/merchantapp/merchant">Login</a>')

def refresh_order(request):
    zomatoid = request.session['zomatoid']
    merchantobj = Merchant.objects.get(merchant_id = zomatoid)
    order_list = Order.objects.filter(merchant = merchantobj)

    dic = []
    print order_list
    for order in order_list:
        x = {}
        x['eta'] = order.eta
        x['orderid'] = order.id
        order_items = OrderItem.objects.filter(order=order)
        print order_items
        d = {}
        for item in order_items:
            d[item.item.name] = item.qty
        x['items'] = d
        dic.append(x)

    print dic
    context = {'orders':dic }
    return render(request, 'merchantapp/orderpage.html', context)


@csrf_exempt
def delete(request):
    id = request.POST['order_id']
    Order.objects.get(id=id).delete()
    return HttpResponse('ok')
