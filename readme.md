# flask-rest-sample

## 简介
flask-rest-sample 是一个使用Python编写的REST API，可以对多个资源提供增删改查服务，用于快速构建REST应用。  
1. Web框架使用Flask
2. ORM框架使用peewee
3. 安全方面使用了flask-jwt插件进行JWT(Json Web Token)认证
4. 由于flask-rest/flask-restplus侵略性较强，本次没有使用。
5. 可以考虑自行使用flasgger添加SwaggerUI文档。

## 第三方依赖
- peewee
- pymysql
- Flask
- Flask-JWT
- flask-script

## 主要代码示例
1. 建模时尽量避免使用外键等约束条件，保证模型结构上一致，可以做到共用一个公共服务。
2. 可使用`@rest.route`添加多个资源

```
# 基本API
@rest.route('/api/reports', methods=['GET', 'POST'])
@rest.route('/api/reports/<id>', methods=['GET', 'PUT', 'DELETE'])
@rest.route('/api/res2', methods=['GET', 'POST'])
@rest.route('/api/res2/<id>', methods=['GET', 'PUT', 'DELETE'])  #只要模型结构一致，可以添加多个资源
@jwt_required()
def common_rest_api(id=None):
    model_name = request.path.split('/')[2]  
    pee_wee_model = utils.get_model_by_name(model_name)  #从URL中确定模型
    if not pee_wee_model:
        return utils.jsonresp(status=400, errinfo='model_name不正确')

    if id:
        # 查询
        if request.method == 'GET':
            try:
                model = pee_wee_model.get(pee_wee_model.id == id)
            except:
                return utils.jsonresp(status=404, errinfo='查询不到资料')
            return utils.jsonresp(jsonobj=utils.obj_to_dict(model))
        # 修改
        elif request.method == 'PUT':
            json_dict = request.get_json(silent=True, force=True)
            if not json_dict: return utils.jsonresp(status=400, errinfo='参数格式不正确')
            try:
                model = pee_wee_model.get(pee_wee_model.id == id)
            except:
                return utils.jsonresp(status=404, errinfo='查询不到资料')
            utils.dict_to_obj(dict=json_dict, obj=model, exclude=('id',))  # 去掉ID字段
            model.save()
            return utils.jsonresp(status=201)
        # 删除
        elif request.method == 'DELETE':
            try:
                pee_wee_model.get(pee_wee_model.id == id).delete_instance()
            except:
                return utils.jsonresp(status=404, errinfo='查询不到资料')
            return utils.jsonresp(status=204)
        else:
            return utils.jsonresp(status=405, errinfo='不支持的HTTP方法')
    else:
        # 全量查询（支持分页、排序、搜索）
        if request.method == 'GET':
            # 处理查询参数
            logger.debug(request.args)
            try:
                # 当前页码
                page = request.args.get('page', '')
                if page: page = int(page) + 1
                # 每页展示数量
                length = request.args.get('length', '')
                if length:
                    length = int(length)
                else:
                    length = cfg.ITEMS_PER_PAGE
                # 排序
                sort = request.args.get('sort', '')
                if sort:
                    sort_column = sort.split(',')[0]
                    sort_direction = sort.split(',')[1]
            except:
                return utils.jsonresp(status=400, errinfo='参数格式不正确')

            # 查询
            query = pee_wee_model.select()
            total_count = query.count()

            # 排序
            if sort:
                if sort_column in pee_wee_model._meta.fields:
                    field = getattr(pee_wee_model, sort_column)
                    if sort_direction != 'asc':
                        field = field.desc()
                    query = query.order_by(field)
            # 分页
            if page:
                query = query.paginate(page, length)

            dict = {'content': utils.query_to_list(query), 'totalElements': total_count}
            return utils.jsonresp(jsonobj=dict)
        # 新增
        elif request.method == 'POST':
            json_dict = request.get_json(silent=True, force=True)
            if not json_dict: return utils.jsonresp(status=400, errinfo='参数格式不正确')
            user = utils.dict_to_obj(dict=json_dict, obj=pee_wee_model(), exclude=['id'])  # 去掉ID字段
            user.save()
            return utils.jsonresp(status=201)
        else:
            return utils.jsonresp(status=405, errinfo='不支持的HTTP方法')
```

## 环境配置
### venv虚拟环境安装配置
```
sudo pip3 install virtualenv
virtualenv venv
. venv/bin/activate
```

### 第三方依赖安装
```
pip3 install -r requirements.txt

```
### 系统参数配置
1. 编辑`config.py`， 修改SECRET_KEY及MySQL数据库相关参数
```
SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret'
DB_HOST = '127.0.0.1'
DB_USER = 'foobar'
DB_PASSWD = 'foobar'
DB_DATABASE = 'foobar'
```
2. 编辑log-app.conf，修改日志路径
```
args=('/path/to/log/flask-rest-sample.log','a','utf8')
```

### 数据库初始化
1. 自动建表
直接运行`python3 models.py`

2. 插入管理员用户（默认admin/admin)
```
INSERT INTO `user` (`id`, `username`, `password`, `fullname`, `email`, `phone`, `status`)
VALUES
	(1, 'admin', 'pbkdf2:sha1:1000$Km1vdx3W$9aa07d3b79ab88aae53e45d26d0d4d4e097a6cd3', '管理员', 'admin@admin.com', '18612341234', 1);
```

### 启动应用
```
nohup ./manage.py runserver 2>&1 &
或
./run_app_dev.py (仅限测试)
```


## REST接口说明
以reports资源为例：
- GET  /api/reports/<id>  查询  
200 成功


- PUT  /api/reports/<id>  修改  
201 成功

- DELETE  /api/reports/<id>  删除  
204 成功

- POST  /api/reports  新增  
200 成功

- GET  /api/reports  全量查询  
200 成功
> 支持分页（URL参数：page、length）及排序(URL参数：sort)  
> 参数示例：`?page=1&length=5&sort=serial_number,desc`  



## JWT认证简单说明
1. 向`/api/auth`发起用户认证请求
```
POST http://127.0.0.1:5000/api/auth
Content-Type: application/json

{
    "username": "admin",
    "password": "admin"
}
```

2. 获取响应，取得access_token
```
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE0OTE2MzUyNTQsIm5iZiI6MTQ5MTYzNTI1NCwiaWRlbnRpdHkiOjEsImV4cCI6MTQ5MTYzNTU1NH0.wq-uer9LbRP5hEYGT4WfD5O4jf7k7du2Q1K6musKzvU"
}
```
3. 在接下来的HTTP请求头中，加入`Authorization`，值为`JWT+空格+access_token`

以获取当前用户信息为例  
请求：
```
GET http://127.0.0.1:5000/api/identity
Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE0OTE2MzUyNTQsIm5iZiI6MTQ5MTYzNTI1NCwiaWRlbnRpdHkiOjEsImV4cCI6MTQ5MTYzNTU1NH0.wq-uer9LbRP5hEYGT4WfD5O4jf7k7du2Q1K6musKzvU
```

响应：
```
{
  "email": "admin@admin.com",
  "fullname": "管理员",
  "username": "admin",
  "phone": "18612341234"
}
```
