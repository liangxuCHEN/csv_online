from django.shortcuts import render

from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from django.views import generic
from mywork.models import TableModel, AuthTableModel
from mywork.forms import AuthenticationForm

import json
import ethercalc
# Create your views here.

class TableListView(generic.ListView):
    model = TableModel
    template_name = "index.html"
    paginate_by = 10   # 一个页面显示的条目
    context_object_name = "table_list"


#重写表格列表
def table_list(request):
    if request.user.is_authenticated:
        tables = []
        auth_tables = AuthTableModel.objects.filter(users=request.user)
        for a_tab in auth_tables:
            tables.append(a_tab.table)

        return render(request, 'table_list.html', {'table_list': tables })
    else:
        return HttpResponseRedirect('/login')



def table_view(request, table_id):
    if request.user.is_authenticated:
        content = {}
        table = TableModel.objects.filter(pk=table_id).first()

        if table:
            content['table'] = table
            # 同组别用户列表
            content['users'] = get_users(request.user)
            # 已有权限用户
            auth_table = AuthTableModel.objects.filter(table=table).first()
            if auth_table:
                content['editors'] = auth_table.users.all()

        return render(request, 'main_table.html', content)
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

        content = {'table': table, 'users': users}

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
        return render(request, 'main_table.html', {'table': table})
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
                return HttpResponseRedirect('/')
            else:
                content['info'] = u"帐号或密码错误"
                content['form'] = AuthenticationForm()
                return render(request, 'login.html', content)
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def get_users(user):
    groups = Group.objects.filter(user=user)
    users = {}
    for g in groups:
        users[g.name] = g.user_set.all()

    return users