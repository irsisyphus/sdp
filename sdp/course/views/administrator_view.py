import datetime as dt
from django.template.defaulttags import register
from django.core.serializers import json
from django.db.models import Q
from ..models import Category, Staff, Course, Instructor, Module, Participant, Administrator
from django.shortcuts import render_to_response,render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth, messages
from django.template import RequestContext
from django.forms.formsets import formset_factory
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from . import log_view as lv

@login_required
def index(request):
    lv.assignType(request.user.id, "Administrator")
    hour = dt.datetime.now().hour
    if hour < 6 or hour > 19:
        title = "Good night, "
    elif hour < 12:
        title = "Good morning, "
    elif hour < 17:
        title = "Good afternoon, "
    else:
        title = "Good evening, "
    administrator = Administrator.objects.get(user__pk=request.user.id)
    # no need to check, this method is guaranteed to work
    title += str(administrator) + "!"
    content = "Daily Notices:"
    return render_to_response('administrator/index.html', locals())

@login_required
def category(request):
    admin = Administrator.objects.get(user__pk=request.user.id)
    counts = admin.viewCategories()
    return render_to_response('administrator/category.html',locals())

@login_required
def priority(request):
    admin = Administrator.objects.get(user__pk=request.user.id)
    all = admin.viewAllUsers()

    allUD = dict()
    allUsers = []
    cnt=0
    allUsers.append(allUD)
    type = dict()
    page = 0
    type_now=0    #0=all, 1=instructor, 2=participant, 3=HR, 4=administrator
    for u in all:
        allUsers[cnt][u.pk]=u.username
        str = ""
        if u.groups.filter(name='Participant').exists():
            if len(str)==0:
                str+="Participant"
            else:
                str+="/Participant"
        if u.groups.filter(name='Instructor').exists():
            if len(str) == 0:
                str += "Instructor"
            else:
                str += "/Instructor"
        if u.groups.filter(name='HR').exists():
            if len(str) == 0:
                str += "HR"
            else:
                str += "/HR"
        if u.groups.filter(name='Administrator').exists():
            if len(str) == 0:
                str += "Admin"
            else:
                str += "/Admin"
        type[u.pk] = str
        if len(allUsers[cnt])==10:
            allUD = dict()
            allUsers.append(allUD)
            cnt+=1
    if len(allUsers[cnt]) == 0:
        num = range(len(allUsers)-1) 
    else:
        num = range(len(allUsers))
    return render_to_response('administrator/priority.html',locals())

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
@login_required
def category_info(request):
    category_id = request.POST['category_id']
    category_name = request.POST['category_name']
    parent_category = Category.objects.get(pk=category_id)
    mycourses = Course.objects.filter(category = parent_category)
    courses = []
    cnt = 0
    for i in mycourses:
        courses.append(i)
        cnt+=1
        if cnt>4:
            break
    # courses = Course.objects.filter(Q(category = parent_category, is_open = True) | Q(category = parent_category, is_open = False, instructor = parent_instructor))
    return render_to_response('administrator/category_info.html', locals())

@login_required
def category_create(request):
    return render_to_response('administrator/create_category.html', locals())


@login_required
def category_create_finish(request):
    category_name = request.POST['category_name']
    admin = Administrator.objects.get(user__pk=request.user.id)
    admin.createCategory(category_name)
    return HttpResponse("Success")

@login_required
def category_delete(request):
    category_id = request.POST['category_id']
    admin = Administrator.objects.get(user__pk=request.user.id)
    if admin.deleteCategory(category_id):
        counts = admin.viewCategories()
        return render_to_response('administrator/delete_category_true.html', locals())
    else:
        counts = admin.viewCategories()
        return render_to_response('administrator/delete_category_false.html', locals())

@login_required
def generate_user(request):
    i = request.POST['i']
    type_now = request.POST['type_now']
    type_now = int(type_now)
    i = int(i)
    admin = Administrator.objects.get(user__pk=request.user.id)
    all = admin.viewAllUsers()

    allUD = dict()
    allUsers = []
    cnt = 0
    allUsers.append(allUD)
    type = dict()
    for u in all:
        flag = 0
        if type_now==0:
            flag = 1
        str = ""
        if u.groups.filter(name='Participant').exists():
            if type_now==2:
                flag = 1
            if len(str) == 0:
                str += "Participant"
            else:
                str += "/Participant"
        if u.groups.filter(name='Instructor').exists():
            if type_now==1:
                flag = 1
            if len(str) == 0:
                str += "Instructor"
            else:
                str += "/Instructor"
        if u.groups.filter(name='HR').exists():
            if type_now==3:
                flag = 1
            if len(str) == 0:
                str += "HR"
            else:
                str += "/HR"
        if u.groups.filter(name='Administrator').exists():
            if type_now==4:
                flag = 1
            if len(str) == 0:
                str += "Admin"
            else:
                str += "/Admin"
        if flag==1:
            type[u.pk] = str
            allUsers[cnt][u.pk] = u.username
        if len(allUsers[cnt]) == 10:
            allUD = dict()
            allUsers.append(allUD)
            cnt += 1
    allU = allUsers[i]
    page = i
    num = range(len(allUsers))
    return render_to_response('administrator/generateUsersForm.html', locals())

@login_required
def designate(request):
    id = request.POST['id']
    admin = Administrator.objects.get(user__pk=request.user.id)
    user = admin.getUser(id)
    if user.groups.filter(name='Instructor').exists():
        return render_to_response('administrator/designate_false.html')
    else:
        admin.designateInstructor(user)
        return render_to_response('administrator/designate_true.html')

@login_required
def generate_by_name(request):
    name = request.POST['name']
    admin = Administrator.objects.get(user__pk=request.user.id)
    u = admin.getUserByName(name)
    if u != None:
        username = u.username
        id = u.pk
        str = ""
        if u.groups.filter(name='Participant').exists():
            if len(str) == 0:
                str += "Participant"
            else:
                str += "/Participant"
        if u.groups.filter(name='Instructor').exists():
            if len(str) == 0:
                str += "Instructor"
            else:
                str += "/Instructor"
        if u.groups.filter(name='HR').exists():
            if len(str) == 0:
                str += "HR"
            else:
                str += "/HR"
        if u.groups.filter(name='Administrator').exists():
            if len(str) == 0:
                str += "Admin"
            else:
                str += "/Admin"
        return render_to_response('administrator/generate_by_name.html',locals())
    else:
        return render_to_response('administrator/not_found.html',locals())
