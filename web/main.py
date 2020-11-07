import requests
import json
from flask import Flask, request, render_template, session,redirect,url_for

import myConfig
import myModel

import hashlib

# web server for debug
app = Flask(__name__)
# session
app.config["SECRET_KEY"] = myConfig.flask_secret_key
app.config["PERMANENT_SESSION_LIFETIME"] = myConfig.flask_permanent_session_lifetime

@app.route("/", methods=["GET"])
def Index():
    return render_template("www/Index.html")

@app.route("/About", methods=["GET"])
def About():
    return render_template("www/About.html")

@app.route("/Logout", methods=["GET"])
def Logout():
    session["role"] = ""
    return redirect(url_for("Login"))

@app.route("/Login", methods=["GET","POST"])
def Login():
    if request.method == "GET":
        return render_template("www/Login.html")
    if request.method == "POST":
        userCheck = myModel.UserCheckModel()
        loginPhone = request.values["phone"]
        loginPassword = request.values["password"]

        try:
            loginRemember = request.values["remember"]
        except:
            loginRemember = ""
        
        userCheck.phone = loginPhone
        # call web api
        url = myConfig.userApi + "check"
        result = requests.post(url,json=userCheck.__dict__)
        # 获取返回值
        response = myModel.ResponseModel()
        response.__dict__ = json.loads(result.text)

        if response.status == "1":
            # 取回信息
            user = myModel.UserModel()
            user.__dict__ = response.result

            if user.role == "admin":
                # 验证密码
                # sha512加密
                sha512 = hashlib.sha512()
                sha512.update(loginPassword.encode("utf-8"))
                sha512_result = sha512.hexdigest()

                if(user.password == sha512_result):

                    if(loginRemember == "on"):
                        # 设置 session 保持
                        session.permanent = True

                    session["role"] = user.role
                    return redirect(url_for("Manage"))

        return render_template("www/Login.html")


@app.route("/Manage", methods=["GET"])
def Manage():
    role = session.get("role")
    if role != "admin":
        # 无权限，重定向到登录页面
        return redirect(url_for("Login"))
    else:
        # 有权限

        # 创建查询请求（查所有订单）
        orderRetrieveModel = myModel.OrderRetrieveModel()
        # call web api
        url = myConfig.orderApi + "retrieve"
        result = requests.post(url,json=orderRetrieveModel.__dict__)
        # 获取返回值
        response = myModel.ResponseModel()
        response.__dict__ = json.loads(result.text)
        # 取出订单
        count = int(response.status)
        orders = response.result
        orderList = []
        
        for item in orders:
            order = myModel.OrderModel()
            order.__dict__ = item
            order.count = round(order.count)
            orderList.append(order)

        return render_template("www/Manage.html",orderList=orderList)

@app.route("/SpotRetrieve", methods=["GET","POST"])
def SpotRetrieve():
    if request.method == "GET":
        # 取得参数
        spotRetrieve = myModel.SpotRetrieveModel()
        queryType = request.values["queryType"]
        queryText = request.values["queryText"]
        # 判断查询条件
        if queryType == "id":
            spotRetrieve.id = queryText
        elif queryType == "name":
            spotRetrieve.name = queryText
        elif queryType == "address":
            spotRetrieve.address = queryText
        else:
            return render_template("www/SpotRetrieve.html",count=0,spotList=[])
        # call web api
        url = myConfig.spotApi + "retrieve"
        result = requests.post(url,json=spotRetrieve.__dict__)
        # 获取返回值
        response = myModel.ResponseModel()
        response.__dict__ = json.loads(result.text)
        # 分别获取每条信息
        count = int(response.status)
        spots = response.result
        spotList = []
        for item in spots:
            spot = myModel.SpotModel()
            spot.__dict__ = item
            spotList.append(spot)
            
        return render_template("www/SpotRetrieve.html",count=count,spotList=spotList)
    
if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port=8000)