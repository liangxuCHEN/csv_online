from django.shortcuts import render

from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views import generic
from mywork.models import TableModel, AuthTableModel
from mywork.forms import AuthenticationForm
import ethercalc
# Create your views here.

class TableListView(generic.ListView):
    model = TableModel
    template_name = "index.html"
    paginate_by = 10   # 一个页面显示的条目
    context_object_name = "table_list"


def table_view(request, table_id):
    if request.user.is_authenticated:
        table = TableModel.objects.filter(pk=table_id).first()
        return render(request, 'main_table.html', {'table': table})
    else:
        return HttpResponseRedirect('/login')


def new_table(request):
    if request.user.is_authenticated:
        table = TableModel(table_name='新件文档')
        table.save()
        return render(request, 'main_table.html', {'table': table})
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