from django.shortcuts import render

from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from django.views import generic
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from mywork.models import TableModel, AuthTableModel, TableMessageModel
from mywork.forms import AuthenticationForm

import json
from datetime import datetime, timedelta
# import ethercalc
# Create your views here.
from online_work import settings


def allow_all(response):
    """
    解决跨域的问题
    :param response:
    :return:
    """
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "*"
    return response


def set_cookie(response, key, value, days_expire = 7):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  #one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.strftime(datetime.utcnow() + timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN)
    print(response)


class TableListView(generic.ListView):
    model = TableModel
    template_name = "index.html"
    paginate_by = 10   # 一个页面显示的条目
    context_object_name = "table_list"


#重写表格列表
def table_list(request):
    """
    可编写的表单
    :param request: 
    :return: 
    """
    if request.user.is_authenticated:
        tables = []
        auth_tables = AuthTableModel.objects.filter(users=request.user)
        for a_tab in auth_tables:
            tables.append(a_tab.table)

        page_size = 20
        paginator = Paginator(tables, page_size)
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        try:
            table_page = paginator.page(page)
        except (EmptyPage, InvalidPage):
            table_page = paginator.page(paginator.num_pages)

        return render(request, 'table_list.html', {'table_list': table_page })
    else:
        return HttpResponseRedirect('/login')


def table_view(request, table_id):
    if request.user.is_authenticated:
        content = {'table_domain': settings.TABEL_DOMAIN}
        table = TableModel.objects.filter(pk=table_id).first()

        if table:
            content['table'] = table
            # 同组别用户列表
            content['users'] = get_users(request.user)
            # 已有权限用户
            auth_table = AuthTableModel.objects.filter(table=table).first()
            if auth_table:
                content['editors'] = auth_table.users.all()

            # 备忘录
            messages = TableMessageModel.objects.filter(table=table)
            if messages:
                content['messages'] = [meg.to_json() for meg in messages]


        response = render(request, 'main_table.html', content)
        set_cookie(response, 'power', 'editor')
        return response
    else:
        return HttpResponseRedirect('/login')


def new_table(request):
    if request.user.is_authenticated:
        table = TableModel(table_name='新件文档')
        table.save()

        # 创建权限表
        auth_table = AuthTableModel(table=table)
        auth_table.save()
        # 先保存在添加关联
        auth_table.users.add(request.user)

        # 同组别用户列表
        users = get_users(request.user)

        content = {
            'table': table,
            'users': users,
            'table_domain': settings.TABEL_DOMAIN
        }

        content['editors'] = [request.user]
        return render(request, 'main_table.html', content)
    else:
        return HttpResponseRedirect('/login')


def edit_table(request, table_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            table = TableModel.objects.filter(pk=table_id).first()
            table.table_name = request.POST['table_name']
            table.save()
        return render(request, 'main_table.html', {'table': table, 'table_domain': settings.TABEL_DOMAIN})
    else:
        return HttpResponseRedirect('/login')


@csrf_exempt
def add_editor(request, tab_id, user_id):
    if request.user.is_authenticated:
        user = User.objects.filter(id=user_id).first()
        if user is None:
            return HttpResponse(json.dumps({'status': 400, 'message': '用户不存在'}), content_type="application/json")

        auth_table = AuthTableModel.objects.filter(table_id=tab_id).first()
        if auth_table is None:
            return HttpResponse(json.dumps({'status': 400, 'message': '授权出错'}), content_type="application/json")

        auth_table.users.add(user)
        return HttpResponse(json.dumps({'status': 200, 'message': 'OK'}), content_type="application/json")

    else:
        return HttpResponse(json.dumps({'status': 500, 'message': '权限不足'}), content_type="application/json")


@csrf_exempt
def deleted_editor(request, tab_id, user_id):
    if request.user.is_authenticated:
        user = User.objects.filter(id=user_id).first()
        if user is None:
            return HttpResponse(json.dumps({'status': 400, 'message': '用户不存在'}), content_type="application/json")

        auth_table = AuthTableModel.objects.filter(table_id=tab_id).first()
        if auth_table is None:
            return HttpResponse(json.dumps({'status': 400, 'message': '授权出错'}), content_type="application/json")

        all_users = auth_table.users.all()

        if user in all_users:
            auth_table.users.remove(user)

        return HttpResponse(json.dumps({'status': 200, 'message': 'OK'}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'status': 500, 'message': '权限不足'}), content_type="application/json")


@csrf_exempt
def add_message(request):
    if request.user.is_authenticated:

        tab_id = request.GET.get('table_id') or -1
        table = TableModel.objects.filter(id=tab_id).first()
        if table is None:
            return HttpResponse(json.dumps({'status': 400, 'message': '表格不存在'}), content_type="application/json")

        # 新增备忘录
        message = request.GET.get('message')

        if message:
            print(message)
            table_message = TableMessageModel(
                table=table,
                user=request.user.username,
                user_id=request.user.id,
                content=message)
            table_message.save()
            return HttpResponse(
                json.dumps({'status': 200, 'message': 'OK', 'content': table_message.to_json()}),
                content_type="application/json")
        else:
            return HttpResponse(json.dumps({'status': 400, 'message': '内容不能为空'}), content_type="application/json")

    else:
        return HttpResponse(json.dumps({'status': 500, 'message': '权限不足'}), content_type="application/json")


def LogoutView(request):
    logout(request)
    return HttpResponseRedirect('/login')

def LoginView(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        content = {}
        if form.is_valid():
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                login(request, user)
                response =redirect(to='/')
                set_cookie(response, 'power', 'editor')
                set_cookie(response, 'user_id', user.id)
                return response
            else:
                content['info'] = u"帐号或密码错误"
                content['form'] = AuthenticationForm()
                return render(request, 'login.html', content)
    else:
        form = AuthenticationForm()

    response = render(request, 'login.html', {'form': form})
    set_cookie(response, 'power', 'public')
    set_cookie(response, 'origin_domain_url', settings.ORIGIN_DOMAIN)
    return response


def check_power(request):
    print(request.GET)
    table_url = request.GET.get('table_name')
    user_id = request.GET.get('user_id')
    table = AuthTableModel.objects.filter(table__table_url=table_url).first()
    if table and user_id:
        has_power = table.users.filter(id=user_id)
        if has_power:
            response = HttpResponse(json.dumps({'status': 200, 'message': '可编辑'}), content_type="application/json")
        else:
            response = HttpResponse(json.dumps({'status': 300, 'message': '可读'}), content_type="application/json")
    else:
        response= HttpResponse(json.dumps({'status': 500, 'message': '缺少参数'}), content_type="application/json")

    return allow_all(response)

def get_users(user):
    groups = Group.objects.filter(user=user)
    users = {}
    for g in groups:
        users[g.name] = g.user_set.all()

    return users