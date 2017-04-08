from . import rest
from flask_jwt import JWT, current_identity,jwt_required
from app.models import User
from app import utils
from flask import Response
from werkzeug.security import check_password_hash


# 身份认证
def authenticate(username, password):
    try:
        user = User.get(User.username == username)
        password_hash = user.password
        # if safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        if check_password_hash(password_hash, password):
            return user
    except:
        pass


# 返回身份信息
def identity(payload):
    user_id = payload['identity']
    user = User.get(User.id == user_id, User.status == True)
    return {'username': user.username, 'fullname': user.fullname, 'email': user.email, 'phone': user.phone}


# jwt = JWT(rest, authenticate, identity)


# 获取token
# POST /api/auth  {"username":"yourname","password":"yourpwd"}

# 获取用户信息
@rest.route('/api/identity')
@jwt_required()
def users_current():
    return Response(str(current_identity).replace("'", '"'), mimetype='application/json', status=200)
