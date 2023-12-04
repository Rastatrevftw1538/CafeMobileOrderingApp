from flask import *
import SMSReminders as SMS

from werkzeug.exceptions import HTTPException
import bcrypt
import os
import time
from markupsafe import escape
import pymongo
import dns
import datetime
import pytz
import venmo
#import flask_admin
#from flask_admin.model import BaseModelView
#import flask_admin.contrib.pymongo
#from wtforms import form, fields, validators


"""DO NOT TOUCH!!!"""
InfoDict = {}
with open('flaskproject/venv/SecretKeys.txt','r') as Info:
    for line in Info:
        (key,value) = line.split()
        InfoDict[str(key)] = value
    AdminInfo = InfoDict["MongoDBInfo"]
myclient = pymongo.MongoClient(
    "mongodb+srv://Customer:12345678910@cluster01-r12ux.mongodb.net/test?retryWrites=true&w=majority"
)
myAdmin = pymongo.MongoClient(AdminInfo
)


mydb = myclient["DataBase"]
mydbAdmin = myAdmin["DataBase"]
cafeDB = myclient["CafeLevelDatabase"]
cafeDBAdmin = myAdmin["CafeLevelDatabase"]

mycolcust = mydb["Customers"]
mycolmenu = mydb["Menu"]
mycolpantry = mydb["PantryMenu"]
mycolmenuAdmin = mydbAdmin["Menu"]
mystats = mydb["OrderData"]
mystatsPantry = mydb["PantryOrderData"]

colorders = cafeDB["Orders"]
colpantryorders = cafeDB["PantryOrders"]

"""DO NOT TOUCH!!!"""

app = Flask(__name__)

#mail = Mail(app)

#Putting Season Key securely in the SecretKeys.txt file
app.secret_key = InfoDict["SeasonKey"]
app._static_folder = "templates/static"


selected = []
specRequ = []
totprice = 0.00
carriers = {
    'AT&T':    '@mms.att.net',
    'T-Mobile': ' @tmomail.net',
    'Verizon':  '@vzwpix.com',
    'Sprint':   '@page.nextel.com'
}

@app.route("/", methods=["GET", "POST"])
def start():
    # if 'username' not in session:
    return render_template("login.html")
    # else:
    # return redirect(url_for("CafeMenu"))


def AddToCafeCart(quan, item, SR):
    split = item.split(":")
    specRequ.append(str(SR))
    selected.append(str(split[0]))
    selected.append(float(split[1]))
    for t in mycolcust.find({"username": session['username']}):
        print(t['myCart']['Items'])
        for num in range(0, quan):
            mycolcust.update_one({"username": str(session['username'])}, {"$push": {"myCart.Items": [{str(
                selected[0]) + " " + str(selected[1]) + " " + str(selected[2]):[float(selected[3]), specRequ[0]]}]}})
    selected.clear()
    specRequ.clear()
    quan = 0


def AddToPantryCart(quan, item, SR):
    split = item.split(":")
    print('split', split)
    specRequ.append(str(SR))
    selected.append(str(split[0]))
    selected.append(float(split[1]))
    for t in mycolcust.find({"username": session['username']}):
        print(t['myCartPantry']['Items'])
        for num in range(0, quan):
            try:
                mycolcust.update_one({"username": str(session['username'])}, {"$push": {"myCartPantry.Items": [{str(
                    selected[0]) + " " + str(selected[1]) + " " + str(selected[2]): [float(selected[3]), specRequ[0]]}]}})
            except:
                print('ERROR', selected, num, specRequ)
    selected.clear()
    specRequ.clear()
    quan = 0


@app.route("/CafeLouis", methods=["GET", "POST"])
def CafeMenu():
    if 'username' in session:
        for u in mycolcust.find({"username": session['username']}):
            user = u
        # Main Menu:
        quan = 0
        timeThing = datetime.datetime
        menuItems = []
        menuDescs = []
        menuChoice = []
        menuStartPrice = []
        # for t in mycolcust.find({'_id':str(currentUser['_id'])}):

        hour = timeThing.now(tz=pytz.timezone("America/Los_Angeles")).hour
        minute = timeThing.now(tz=pytz.timezone("America/Los_Angeles")).minute

        # For when to display items.
        # if timeThing.now().isoweekday() < 6:
        # if float(hour+(float(minute/100))) >= 7.30 and float(hour+(float(minute/100))) <= 20.00:
        # if float(hour+(float(minute/100))) < 11.00:
        for i in mycolmenu.find({'aval': {'$in': ['AllDay', 'Morn']}}):
            menuItems.append(i['item'])
            menuDescs.append(i['desc'])
            for price in list(i['choice'].values())[0].values():
                menuStartPrice.append(price)
                break
            tempChoice = []
            for x in i['choice']:
                tempChoice.append(x)
            menuChoice.append(tempChoice)
        return render_template(
            "Menu.html",
            items=menuItems,
            descs=menuDescs,
            choice=menuChoice,
            startPrice=menuStartPrice,
            user=user,
        )
        abort(403)
        return render_template("login.html")


@app.route("/GaelPantry", methods=["GET", "POST"])
def PantryMenu():
    if 'username' in session:
        for u in mycolcust.find({"username": session['username']}):
            user = u
        # Main Menu:
        quan = 0
        timeThing = datetime.datetime
        menuItems = []
        menuDescs = []
        menuChoice = []
        menuStartPrice = []
        # for t in mycolcust.find({'_id':str(currentUser['_id'])}):

        hour = timeThing.now(tz=pytz.timezone("America/Los_Angeles")).hour
        minute = timeThing.now(tz=pytz.timezone("America/Los_Angeles")).minute

        # For when to display items.
        for i in mycolpantry.find({'aval': {'$in': ['AllDay']}}):
            menuItems.append(i['item'])
            menuDescs.append(i['desc'])
            for price in list(i['choice'].values())[0].values():
                menuStartPrice.append(price)
                break
            tempChoice = []
            for x in i['choice']:
                tempChoice.append(x)
            menuChoice.append(tempChoice)
        return render_template(
            "MenuPantry.html",
            items=menuItems,
            descs=menuDescs,
            choice=menuChoice,
            startPrice=menuStartPrice,
            user=user,
        )
    else:
        abort(403)
        return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def Login():
    if request.method == "POST":
        if str(request.form["Login"]) == "LoginCafe":
            for u in mycolcust.find({"username": request.form["uname"]}):
                if str(request.form["uname"]) == u["username"]:
                    if bcrypt.checkpw(str(request.form["psw"]).encode("utf-8"),u["hashed_pass"]):
                        session["username"] = request.form["uname"]
                        session.permanent = True
                        session.modified = True
                        return redirect(url_for("CafeMenu"))
                    else:
                        return render_template("login.html")
                else:
                    return render_template("login.html")
        elif str(request.form["Login"]) == "LoginPantry":
            try:
                if mycolcust.find_one({"username": request.form["uname"]}):
                    u = mycolcust.find_one({"username": request.form["uname"]})
                    if str(request.form["uname"]) == u["username"]:
                        if bcrypt.checkpw(str(request.form["psw"]).encode("utf-8"),u["hashed_pass"]):
                            session["username"] = request.form["uname"]
                            session.permanent = True
                            session.modified = True
                            return redirect(url_for("PantryMenu"))
                        else:
                            return render_template("login.html")
                    else:
                        return render_template("login.html")
            except:
                return render_template("login.html")
        elif str(request.form["Login"]) == "SignUp":
            return render_template("signup.html")
    else:
        return render_template("login.html")


@app.route("/logout")
def Logout():
    #g.user = ""
    session.permanent = False
    session.pop("username")
    myclient.close()
    return start()


@app.route("/signup", methods=["POST"])
def SignUp():
    if request.method == "POST":
        if request.form["SignUp"] == "SignUp":
            custDict = {}
            full_name = (
                str(request.form["fname"]).strip()
                + " "
                + str(request.form["lname"]).strip()
            )
            custDict["_id"] = str(request.form["smcID"])
            custDict["name"] = str(full_name)
            custDict["username"] = str(request.form["uname"].strip())
            custDict["phoneNum"] = str(
                request.form["PNum"])+'{}'.format(carriers[request.form['PCarrier']])
            custDict["hashed_pass"] = bcrypt.hashpw(
                str(request.form["psw"]).encode("utf-8"), bcrypt.gensalt())
            custDict['myCart'] = {"TotalPrice": float(0.00), "Items": []}
            custDict['myCartPantry'] = {"TotalPrice": int(0.00), "Items": []}
            custDict['Rewards'] = {"Points": 0, "Free?": False}
            custDict['PantryPoints'] = int(10)
            custDict['timeToReset'] = datetime.datetime.now(tz=pytz.timezone(
                "America/Los_Angeles")).today() + datetime.timedelta(days=7)
            #custDict['myCart']['TotalPrice'] = float(0.00)
            x = mycolcust.insert_one(custDict)
            return render_template("login.html")
        elif request.form["SignUp"] == "Cancel":
            return render_template("login.html")


@app.route("/selections/Cafe", methods=["GET", "POST"])
def SelectionCafe():
    if 'username' in session:
        for u in mycolcust.find({"username": session['username']}):
            user = u
        tempSel = []
        data = request.form.to_dict()
        dataItem = list(data.values())
        tempSel.append(str(dataItem[0]))
        listOption = []
        listCustnPrice = []
        price = 0
        for a in dataItem:
            tempList = []
            tempCustnPrice = []
            for i in mycolmenu.find({"item": str(a)}):
                for y in i["choice"]:
                    tempList.append(y)
                    tempDict = {}
                    for z in i["choice"][str(y)]:
                        tempDict.update({z: i["choice"][str(y)][str(z)]})
                    tempCustnPrice.append(tempDict)
                listCustnPrice.append(tempCustnPrice)
                listOption.append(tempList)
        selected.clear()
        selected.append(str(tempSel[0]))
        return render_template(
            "selections.html",
            itemList=dataItem,
            optionsList=listOption,
            len1=len(dataItem),
            user=user,
        )
    else:
        abort(403)
        return render_template("login.html")


@app.route("/order/Cafe", methods=["GET", "POST"])
def OrderCafe():
    if 'username' in session:
        for u in mycolcust.find({"username": session['username']}):
            user = u
        tempSel = []
        if request.method == "POST":
            data = request.form.to_dict()
            dataItem = list(data.values())
            tempSel.append(str(dataItem[0]))
            dataName = list(data.keys())
            listOption = []
            listCustnPrice = []
            price = 0
            for a in dataItem:
                tempList = []
                tempCustnPrice = []
                for i in mycolmenu.find({"item": str(dataName[dataItem.index(a)])}):
                    for y in i["choice"][a]:
                        tempList.append(y)
                        tempCustnPrice.append(float(i["choice"][a][y]))
                    listCustnPrice.append(tempCustnPrice)
                    listOption.append(tempList)
            selected.append(tempSel[0])
            return render_template(
                "order.html",
                itemList=dataItem,
                optionsList=listOption,
                priceList=listCustnPrice,
                price=price,
                len1=len(dataItem),
                user=user,
            )
        else:
            return render_template("Menu.html")
    else:
        abort(403)
        return render_template("login.html")


@app.route("/redirectCafe", methods=["GET", "POST"])
def RedirectOrderCafe():
    if 'username' in session:
        if request.method == "POST":
            AddToCafeCart(int(request.form["Quantity"]), str(
                request.form["Item"]), str(request.form.get("Special Request")))
            if str(request.form["WhereTo"]) == "Add to Cart!":
                return redirect(url_for("CafeMenu"))
            elif str(request.form["WhereTo"]) == "Add and Checkout!":
                return redirect(url_for("CheckoutCafe"))
    else:
        abort(403)
        return render_template("login.html")


@app.route("/CheckoutCafe/<int:index>", methods=["GET"])
def Clear(index):
    if 'username' in session:
        for u in mycolcust.find({"username": session['username']}):
            user = u
        print(index)
        mycolcust.find_one_and_update({"username": session['username']}, {
                                      "$set": {f"myCart.Items.{index}": ""}})
        mycolcust.find_one_and_update({"username": session['username']}, {
                                      "$pull": {f"myCart.Items": ""}})
        return redirect(url_for("CheckoutCafe"))
    else:
        abort(403)
        return render_template("login.html")


@app.route("/CheckoutPantry/<int:index>", methods=["GET"])
def ClearPantry(index):
    if 'username' in session:
        for u in mycolcust.find({"username": session['username']}):
            user = u
        print(index)
        mycolcust.find_one_and_update({"username": session['username']}, {
                                      "$set": {f"myCartPantry.Items.{index}": ""}})
        mycolcust.find_one_and_update({"username": session['username']}, {
                                      "$pull": {f"myCartPantry.Items": ""}})
        return redirect(url_for("CheckoutPantry"))
    else:
        abort(403)
        return render_template("login.html")


@app.route("/rewards", methods=["GET", "POST"])
def Rewards():
    if 'username' in session:
        for u in mycolcust.find({"username": session['username']}):
            user = u
        if user["Rewards"]["Points"] == 7:
            mycolcust.find_one_and_update({"username": session['username']}, {
                                          "$set": {"Rewards.Free?": True}})
        return render_template("Rewards.html", user=user, points=int(user["Rewards"]["Points"]), free=bool(user["Rewards"]["Free?"]))
    else:
        abort(403)
        return render_template("login.html")


@app.route("/CheckoutCafe", methods=["GET", "POST"])
def CheckoutCafe():
    if 'username' in session:
        freeItem = None
        freeCoffeeItems = []
        for items in mycolmenu.find({"aval": {"$in": ["AllDay"]}}):
            freeCoffeeItems.append(items["item"])
        madeFree = False
        for u in mycolcust.find({"username": session['username']}):
            user = u
        totprice = 0.00
        print(len(user['myCart']['Items']))
        for x in range(0, len(user['myCart']['Items'])):
            print(x)
            # print(list(user['myCart']['Items'][x][0].values()))
            price = float(list(user['myCart']['Items'][x][0].values())[0][0])
            if bool(user["Rewards"]["Free?"]) and madeFree == False:
                for free in freeCoffeeItems[::1]:
                    print(free)
                    if str(list(user['myCart']['Items'][x][0].keys())[0]).split(" ")[0] == str(free):
                        print(
                            str(list(user['myCart']['Items'][x][0].keys())[0]).split(" ")[0])
                        price = 0.00
                        madeFree = True
                        freeItem = str(
                            list(user['myCart']['Items'][x][0].keys())[0])
            print(float(list(user['myCart']['Items'][x][0].values())[0][0]))
            totprice += price
            print(totprice)
        mycolcust.find_one_and_update({"username": session['username']}, {
                                      "$set": {"myCart.TotalPrice": round(float(totprice), 2)}})
        print(freeItem)
        return render_template(
            "checkout.html",
            user=user,
            TotalPrice=round(float(totprice), 2),
            free=bool(user["Rewards"]["Free?"]),
            FreeItem=freeItem
        )
    else:
        abort(403)
        return render_template("login.html")

# GAELPANTRY SECTION


@app.route("/selections/Pantry", methods=["GET", "POST"])
def SelectionPantry():
    if 'username' in session:
        for u in mycolcust.find({"username": session['username']}):
            user = u
        tempSel = []
        data = request.form.to_dict()
        dataItem = list(data.values())
        tempSel.append(str(dataItem[0]))
        listOption = []
        listCustnPrice = []
        price = 0

        # OPTOMIZE LATER
        for a in dataItem:
            tempList = []
            tempCustnPrice = []
            for i in mycolpantry.find({"item": str(a)}):
                for y in i["choice"]:
                    tempList.append(y)
                    tempDict = {}
                    for z in i["choice"][str(y)]:
                        tempDict.update({z: i["choice"][str(y)][str(z)]})
                    tempCustnPrice.append(tempDict)
                listCustnPrice.append(tempCustnPrice)
                listOption.append(tempList)
        selected.clear()
        selected.append(str(tempSel[0]))
        return render_template(
            "selectionsPantry.html",
            itemList=dataItem,
            optionsList=listOption,
            len1=len(dataItem),
            user=user,
        )
    else:
        abort(403)
        return render_template("login.html")


@app.route("/order/Pantry", methods=["GET", "POST"])
def OrderPantry():
    if 'username' in session:
        for u in mycolcust.find({"username": session['username']}):
            user = u
        tempSel = []
        if request.method == "POST":
            data = request.form.to_dict()
            dataItem = list(data.values())
            tempSel.append(str(dataItem[0]))
            dataName = list(data.keys())
            listOption = []
            listCustnPrice = []
            price = 0
            for a in dataItem:
                tempList = []
                tempCustnPrice = []
                for i in mycolpantry.find({"item": str(dataName[dataItem.index(a)])}):
                    for y in i["choice"][a]:
                        tempList.append(y)
                        tempCustnPrice.append(float(i["choice"][a][y]))
                    listCustnPrice.append(tempCustnPrice)
                    listOption.append(tempList)
            selected.append(tempSel[0])
            return render_template(
                "orderPantry.html",
                itemList=dataItem,
                optionsList=listOption,
                priceList=listCustnPrice,
                price=price,
                len1=len(dataItem),
                user=user,
            )
        else:
            return render_template("MenuPantry.html")
    else:
        abort(403)
        return render_template("login.html")


@app.route("/redirectPantry", methods=["GET", "POST"])
def RedirectOrderPantry():
    if 'username' in session:
        if request.method == "POST":
            AddToPantryCart(int(request.form["Quantity"]), str(
                request.form["Item"]), str(request.form.get("Special Request")))
            if str(request.form["WhereTo"]) == "Add to Cart!":
                return redirect(url_for("PantryMenu"))
            elif str(request.form["WhereTo"]) == "Add and Checkout!":
                return redirect(url_for("CheckoutPantry"))
    else:
        abort(403)
        return render_template("login.html")


@app.before_request
def PantryPoints():
    timeThing = datetime.datetime
    dateThing = timeThing.now(tz=pytz.timezone("America/Los_Angeles")).today()
    if 'username' in session:
        for u in mycolcust.find({"username": session['username']}):
            user = u
        # print(dateThing)
        #print(user["timeToReset"] + datetime.timedelta(days=7))
        # if user["PantryPoints"] < 10:
        try:
            if dateThing >= user["timeToReset"]:
                mycolcust.find_one_and_update({"username": session['username']}, {
                    "$set": {"PantryPoints": 10}})
                mycolcust.find_one_and_update({"username": session['username']}, {
                    "$set": {"timeToReset": dateThing + datetime.timedelta(days=7)}})
        except:
            print("Could not find user")


@app.route("/CheckoutPantry", methods=["GET", "POST"])
def CheckoutPantry():
    if 'username' in session:
        freeItem = None
        freeCoffeeItems = []
        for items in mycolmenu.find({"aval": {"$in": ["AllDay"]}}):
            freeCoffeeItems.append(items["item"])
        madeFree = False
        for u in mycolcust.find({"username": session['username']}):
            user = u
        totprice = 0.00
        print(len(user['myCartPantry']['Items']))
        for x in range(0, len(user['myCartPantry']['Items'])):
            print(x)
            # print(list(user['myCart']['Items'][x][0].values()))
            price = float(
                list(user['myCartPantry']['Items'][x][0].values())[0][0])
            if bool(user["Rewards"]["Free?"]) and madeFree == False:
                for free in freeCoffeeItems[::1]:
                    print(free)
                    if str(list(user['myCartPantry']['Items'][x][0].keys())[0]).split(" ")[0] == str(free):
                        print(
                            str(list(user['myCartPantry']['Items'][x][0].keys())[0]).split(" ")[0])
                        price = 0.00
                        madeFree = True
                        freeItem = str(
                            list(user['myCartPantry']['Items'][x][0].keys())[0])
            print(
                float(list(user['myCartPantry']['Items'][x][0].values())[0][0]))
            totprice += price
            print(totprice)
        mycolcust.find_one_and_update({"username": session['username']}, {
                                      "$set": {"myCartPantry.TotalPrice": round(float(totprice), 2)}})
        print(freeItem)
        return render_template(
            "checkoutPantry.html",
            user=user,
            TotalPrice=round(float(totprice), 2),
            free=bool(user["Rewards"]["Free?"]),
            FreeItem=freeItem
        )
    else:
        abort(403)
        return render_template("login.html")


@app.route("/order-placed/<string:payMethod>", methods=["GET", "POST"])
def OrderPlaced(payMethod, venmoUser=None):
    freeCoffeeItems = []
    if 'username' in session:
        for u in mycolcust.find({"username": session['username']}):
            user = u
        for items in mycolmenu.find({"aval": {"$in": ["AllDay"]}}):
            freeCoffeeItems.append(items["item"])
        # print(request.form["Username"])
        if payMethod == "Venmo":
            if len(user["myCart"]["Items"]) == 0:
                return redirect(url_for("CheckoutCafe"))
            timeToAccept = 60
            try:
                toBeRemoved = user["phoneNum"].index("@")
                # print(toBeRemoved)
                VenNumber = str(user["phoneNum"])[:toBeRemoved]
                priceToPay = round(float(
                    user['myCart']['TotalPrice'])+float(user['myCart']['TotalPrice'])*0.0725, 2)
                venmo.payment.charge(
                    VenNumber, priceToPay, f"Cafe Louis Order Number {int(colorders.count()+1)}")
                # print(venmo.auth.get_access_token())
                #venmoCheck = venmo_api.Client(venmo.auth.get_access_token())
                #print(venmo.user.search("Matthew Zhang"))
            except:
                return redirect(url_for("Checkout"))
        elif payMethod == "Flex Dollars":
            if len(user["myCart"]["Items"]) == 0:
                return redirect(url_for("CheckoutCafe"))
            priceToPay = round(float(user['myCart']['TotalPrice']), 2)
        elif payMethod == "Cash In Person":
            if len(user["myCart"]["Items"]) == 0:
                return redirect(url_for("CheckoutCafe"))
            print(round(float(user['myCart']['TotalPrice']) +
                        float(user['myCart']['TotalPrice'])*0.0725, 2))
            priceToPay = round(float(
                user['myCart']['TotalPrice'])+float(user['myCart']['TotalPrice'])*0.0725, 2)
        elif payMethod == "Pantry":
            if len(user["myCartPantry"]["Items"]) == 0:
                return redirect(url_for("CheckoutPantry"))
            priceToPay = int(user['myCartPantry']['TotalPrice'])
            textSupport = "Text Reminders has been enabled and sent, order time may take 15 minutes to complete."
            orderDict = {}
            if int(colpantryorders.count()) > 99:
                x = colpantryorders.delete_many({"orderProgress": "Completed"})
                print(x)
            orderDict['Que'] = int(colpantryorders.count()+1)
            orderDict['Name'] = user['name']
            orderDict['smcID'] = user['_id']
            orderDict['PhoneNumber'] = user['phoneNum']
            orderDict['Order'] = user['myCartPantry']['Items']
            orderDict['TotalPrice'] = priceToPay
            orderDict['orderProgress'] = "New"
            orderDict['payMethod'] = payMethod
            try:
                SMS.send(
                    f"Your order has been placed!\nYour order number is: {orderDict['Que']}\n\nRemember, you are paying for your order with {payMethod}", orderDict['PhoneNumber'])
            except:
                textSupport = "Text Reminders failed, order time may take 15 minutes to complete."
            finally:
                # Find out what's wrong with this for loop
                timeThing = datetime.datetime
                dateThing = timeThing.now(
                    tz=pytz.timezone("America/Los_Angeles")).today()
                for s in range(0, len(user['myCartPantry']['Items'])):
                    print(list(user['myCartPantry']['Items'][s][0].keys())[0])
                    mystatsPantry.insert_one({"date": dateThing, "order number": orderDict['Que'], "id": user['_id'], "name": user["name"], "item": list(
                        user['myCartPantry']['Items'][s][0].keys())[0], "points used": priceToPay})
                colpantryorders.insert_one(orderDict)
                totprice = 0.00
                mycolcust.find_one_and_update({"username": session['username']}, {
                                              "$set": {"PantryPoints": user["PantryPoints"]-int(priceToPay)}})
                mycolcust.find_one_and_update({"username": session['username']}, {
                                              "$set": {"myCartPantry.Items": []}})
                mycolcust.find_one_and_update({"username": str(session['username'])}, {
                                              "$set": {"myCartPantry.TotalPrice": round(float(totprice), 2)}})
                return render_template('orderplacedPantry.html', txtSup=textSupport, orderNum=orderDict['Que'], user=orderDict['Name'])

        textSupport = "Text Reminders has been enabled and sent, order time may take 15 minutes to complete."
        orderDict = {}
        if int(colorders.count()) > 99:
            x = colorders.delete_many({"orderProgress": "Completed"})
            print(x)
        orderDict['Que'] = int(colorders.count()+1)
        orderDict['Name'] = user['name']
        orderDict['smcID'] = user['_id']
        orderDict['PhoneNumber'] = user['phoneNum']
        orderDict['Order'] = user['myCart']['Items']
        orderDict['TotalPrice'] = priceToPay
        orderDict['orderProgress'] = "New"
        orderDict['payMethod'] = payMethod
        try:
            SMS.send(
                f"Your order has been placed!\nYour order number is: {orderDict['Que']}\n\nRemember, you are paying for your order with {payMethod}", orderDict['PhoneNumber'])
        except:
            textSupport = "Text Reminders failed, order time may take 15 minutes to complete."
        finally:
            timeThing = datetime.datetime
            dateThing = timeThing.now(
                tz=pytz.timezone("America/Los_Angeles")).today()
            for s in range(0, len(user['myCart']['Items'])):
                print(list(user['myCart']['Items'][s][0].keys())[0])
                print(dateThing)
                mystats.insert_one({"date": dateThing, "order number": orderDict['Que'], "id": user['_id'], "name": user["name"], "item": list(
                    user['myCart']['Items'][s][0].keys())[0], "total price": priceToPay, "pay method": payMethod})
            colorders.insert_one(orderDict)
            totprice = 0.00
            if user["Rewards"]["Free?"] == True:
                for x in range(0, len(user['myCart']['Items'])):
                    for free in freeCoffeeItems[::1]:
                        if str(list(user['myCart']['Items'][x][0].keys())[0]).split(" ")[0] == str(free):
                            mycolcust.find_one_and_update({"username": session['username']}, {
                                                          "$set": {"Rewards.Free?": False}})
                            mycolcust.find_one_and_update({"username": session['username']}, {
                                                          "$set": {"Rewards.Points": 0}})
            else:
                mycolcust.find_one_and_update({"username": session['username']}, {
                                              "$set": {"Rewards.Points": int(user["Rewards"]["Free?"]+1)}})
            mycolcust.find_one_and_update({"username": session['username']}, {
                                          "$set": {"myCart.Items": []}})
            mycolcust.find_one_and_update({"username": str(session['username'])}, {
                                          "$set": {"myCart.TotalPrice": round(float(totprice), 2)}})
            return render_template('orderplaced.html', txtSup=textSupport, orderNum=orderDict['Que'], user=orderDict['Name'])
    else:
        abort(403)
        return render_template("login.html")


if __name__ == "__main__":
    app.jinja_env.cache = {}
    app.run(host='localhost', port=8088, debug=True)
# CAFE ADMIN LOGIN PAGE

'''

Use ths to remove everything from the cart.

mycolcust.find_one_and_update({"_id":currentUser["_id"]},{"$pull":{"myCart.Items":{}}})

'''
