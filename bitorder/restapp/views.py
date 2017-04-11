from django.shortcuts import render
from django.http import HttpResponse,Http404
import requests
import json
from django.views.decorators.clickjacking import xframe_options_exempt
from csp.decorators import csp_update
import urllib2
from merchantapp.models import menuItem,Merchant,Order,OrderItem
from datetime import datetime, timedelta


# Create your views here.
def customer(request):
    context = {
    }
    return render(request, 'restapp/login.html', context)

@csp_update(FRAME_SRC='self')
@xframe_options_exempt
def customerlogin(request):
    email = request.POST['email']
    password = request.POST['password']
    lat = request.POST['lat']
    lng = request.POST['lng']

    request.session['email'] = str(email)
    request.session['lat'] = str(lat)
    request.session['lng'] = str(lng)

    print email
    print password
    print lat
    print lng

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
        print authorized_access_token


        #get zomato restaurants
        url = "https://developers.zomato.com/api/v2.1/geocode"
        querystring = {"lat":str(lat),"lon":str(lng)}
        headers = {
            'user-key': "b50d2bf26248c454b30ca3a56271a6e0",
            'cache-control': "no-cache",
            'postman-token': "d3bf5b38-54b1-61fc-d497-aacfd1ecc743"
            }
        response = requests.request("GET", url, headers=headers, params=querystring)
        print response.text
        pjson = json.loads(response.text)
        restaurants = pjson['nearby_restaurants']
        for restaurant in restaurants:
            print restaurant['restaurant']['name'],restaurant['restaurant']['location']['latitude'],restaurant['restaurant']['location']['longitude'],restaurant['restaurant']['id']

    except:
        HttpResponse('Invalid login.<a href="a74914f8.ngrok.io/restapp">Login</a>')
    context = {
        'lat':lat,
        'lng':lng,
        'restaurants':restaurants,
    }
    return render(request, 'restapp/selectrestaurant.html', context)



@csp_update(FRAME_SRC='self')
@xframe_options_exempt
def test(request):
    context = {

    }
    return render(request, 'restapp/selectrestaurant.html', context)


def menu(request,id):
    print request.session['access_token']
    print request.session['authorized_access_token']
    print id


    url = "https://developers.zomato.com/api/v2.1/restaurant"
    querystring = {"res_id":str(id)}
    headers = {
        'user-key': "b50d2bf26248c454b30ca3a56271a6e0",
        'cache-control': "no-cache",
        'postman-token': "d3bf5b38-54b1-61fc-d497-aacfd1ecc743"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    pjson = json.loads(response.text)
    print pjson['menu_url']
    merchant_lat = pjson['location']['latitude']
    merchant_lng = pjson['location']['longitude']

    resp = requests.get('https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins='+request.session["lat"]+','+request.session["lng"]+'&destinations='+merchant_lat+'%2C'+merchant_lng+'&key=AIzaSyCN6QzJMFObAFkIJingkOjgYGfT4bWEN2o')
    djson = json.loads(resp.text)
    request.session['eta'] = djson['rows'][0]['elements'][0]['duration']['value']
    print request.session['lat'],request.session['lng']
    print merchant_lat,merchant_lng

    merchantobj = Merchant.objects.get(merchant_id = id)
    menu_items = menuItem.objects.filter(merchant= merchantobj)
    print menu_items
    context = {
        'items':menu_items,
    }
    return render(request, 'restapp/menu.html', context)

def order(request):
    order_list = {}
    for key in request.POST:
        value = request.POST[key]
        if key.isdigit():
            order_list[key] = int(value)
    items = order_list.keys()
    menuitem = menuItem.objects.get(id = items[0])
    merchantobj = menuitem.merchant

    total = request.POST['total']

    x = datetime.now() + timedelta(seconds=request.session['eta'])
    x += timedelta(hours=5,minutes=30)
    orderobj = Order(merchant = merchantobj, client = request.session['email'],eta=x.strftime('%H:%M:%S'))
    orderobj.save()

    url = "https://sandbox.unocoin.co/api/v1/wallet/bitcoinaddress"
    headers = {
        'content-type': "application/json",
        'authorization': "Bearer "+request.session['authorized_access_token'],
        'cache-control': "no-cache",
        'postman-token': "265e927f-81d2-0ba0-29b8-cd946117fd73"
        }

    response = requests.request("POST", url, headers=headers)
    print(response.text)




    pjson = json.loads(response.text)
    btc_balance = float(pjson['btc_balance'])

    url = "https://sandbox.unocoin.co/api/v1/general/prices"

    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'authorization': "Bearer 9c3b95976759e1c56c13e8560fa4bfae552f2c67",
        'cache-control': "no-cache",
        'postman-token': "74ea5736-455d-ebc0-3e62-e9e2304131e1"
        }

    response = requests.request("POST", url, headers=headers)

    print(response.text)
    pjson = json.loads(response.text)
    buybtc = float(pjson['buybtc'])
    total_btc = float(total)/buybtc
    if(btc_balance < 0.5):
        url = "https://sandbox.unocoin.co/api/v1/settings/addaccount"
        payload = "accountnum=2100010022100229&ifsc=vysa0002290&nickname=A"
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'authorization': "Bearer "+request.session['authorized_access_token'],
            'cache-control': "no-cache",
            'postman-token': "99e65e70-7c92-5e59-9764-3fc18d659d2a"
            }

        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)
        #doing INR deposit
        url = "https://sandbox.unocoin.co/api/v1/wallet/inr_deposit"

        payload = "inr_amount=40000"
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'authorization': "Bearer "+request.session['authorized_access_token'],
            'cache-control': "no-cache",
            'postman-token': "fc9104ef-51b1-03b8-d46f-8b0a4ec213cc"
            }
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)

        url = "https://sandbox.unocoin.co/api/v1/general/prices"

        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'authorization': "Bearer 9c3b95976759e1c56c13e8560fa4bfae552f2c67",
            'cache-control': "no-cache",
            'postman-token': "74ea5736-455d-ebc0-3e62-e9e2304131e1"
            }

        response = requests.request("POST", url, headers=headers)

        print(response.text)
        pjson = json.loads(response.text)
        buytax = float(pjson['buytax'])
        buyfees = float(pjson['buyfees'])
        buybtc = float(pjson['buybtc'])

        btc = float(total)/float(buybtc)
        btc_worth_inr = btc*buybtc
        withfee = btc_worth_inr*1.01
        withtax = withfee + (btc_worth_inr*0.01*(buytax/100))

        #buyingbtc
        url = "https://sandbox.unocoin.co/api/v1/trading/buyingbtc"

        payload = "destination=My%20wallet&inr="+str(btc_worth_inr)+"&total="+str(withtax)+"&btc="+str(btc)+"&fee="+str(btc_worth_inr*0.01)+"&tax="+str(withtax-withfee)+"&rate="+str(buybtc)
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'authorization': "Bearer "+request.session['authorized_access_token'],
            'cache-control': "no-cache",
            'postman-token': "7dea3571-9485-f9dd-76e8-97f62f7642d9"
            }

        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)

    url = "https://sandbox.unocoin.co/api/v1/wallet/sendingbtc"

    payload = "to_address="+merchantobj.bit_addr+"&btcamount="+str(total_btc)
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'authorization': "Bearer "+request.session['authorized_access_token'],
        'cache-control': "no-cache",
        'postman-token': "94a864c8-e814-c485-d5da-bd2653bbb81f"
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.text)




    for key,value in order_list.iteritems():
        if value>0:
            menuitem = menuItem.objects.get(id = key)
            OrderItem(order=orderobj,item=menuitem,qty=value).save()
    context = {
        'orderid':orderobj.id,
    }
    return render(request, 'restapp/ordercode.html', context)
