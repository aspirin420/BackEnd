#!/usr/bin/python
# -*- coding: UTF-8 -*-
from flask import Flask,render_template,jsonify,request,g, url_for,abort
from flask_cors import CORS
from . import auth
from models import *
import hashlib
import json
import os
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from store_info import store_info
from user_info import user_info
from order_info import order_info

from user_login import user_login
from type_search import type_search
from store_by_id import store_by_id
from orders_by_user_id import orders_by_user_id

# extensions

app.register_blueprint(store_info)
app.register_blueprint(user_info)
app.register_blueprint(order_info)

app.register_blueprint(user_login)
app.register_blueprint(type_search)
app.register_blueprint(store_by_id)
app.register_blueprint(orders_by_user_id)

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(id=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})
@app.route('/api/users/<username>')
def get_user(username):
    user = User.query.filter_by(id=username).first()
    if not user:
        abort(400)
    return jsonify({'username': user.username})
@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({ 'data': 'Hello, %s!' % g.user.username })


@app.route("/")
def home():
    '''
    页面之间的跳转交给前端路由负责，后端不用再写大量的路由
    '餐馆信息 : /index 注册信息 : /sign_up 订单详情 : /user/<userID>/orders/<orderID> 登陆信息 : /login 单个店铺点单信息 : host/index/store_name'
    '''
    return render_template('index.html')

@app.route('/test', methods=['GET', 'POST'])
def test():
    ''' 这个API用来测试跨域 '''
    return 'success'


# @app.route('/user/<userID>/orders/<orderID>', methods=['GET', 'POST'])
# def order_info_detail(userID, orderID):
#     '''
#     SXT
#     订单详情api
#     用户身份和订单信息确认后输出订单详细信息,失败返回（401）
#     '''
#     if request.method == 'GET':
#         status_code = '201'
#         order_hash = hashlib.md5(orderID)
#         order_detail = {
#             'status_code': status_code,
#             'storeName': 'test_srore_name',
#             'foodList': [''],
#             'mealFee': '123',
#             'ServiceFee': '123',
#             'totalFee': '123',
#             'Offer': '123',
#             'paymentMethod': '1',
#             'Date': '2017-01-08 17:05:24',
#             'orderNumber': order_hash.hexdigest()
#         }
#         # json_order_data = json.dumps(order_detail, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
#         json_order_data = jsonify(order_detail)
#         return json_order_data