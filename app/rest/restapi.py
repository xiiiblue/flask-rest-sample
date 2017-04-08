from flask_jwt import jwt_required
from flask import request
from . import rest
from app import utils
from app.models import *
import logging
from logging.config import fileConfig
fileConfig('conf/log-app.conf')
logger = logging.getLogger(__name__)


# 基本API
@rest.route('/api/reports', methods=['GET', 'POST'])
@rest.route('/api/reports/<id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def common_rest_api(id=None):
    model_name = request.path.split('/')[2]
    pee_wee_model = utils.get_model_by_name(model_name)
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
                # 搜索
                search_value = request.args.get('searchValue', '')
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