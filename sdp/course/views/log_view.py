from ..forms import LoginForm, RegisterForm
from django.shortcuts import render_to_response, render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth, messages
from django.template import RequestContext
from django.forms.formsets import formset_factory
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from ..models import Staff, Course, Instructor, Participant, Administrator, HR
#from django.views.decorators.csrf import csrf_protect, csrf_exempt
#from django.template.context_processors import csrf

# detect the latest group type the current user choose to login


def typeSelect(id):
    if Participant.objects.filter(user__pk=id).exists():
        return Participant.objects.get(user__pk=id).last_login_type
    elif Instructor.objects.filter(user__pk=id).exists():
        return Instructor.objects.get(user__pk=id).last_login_type
    elif HR.objects.filter(user__pk=id).exists():
        return HR.objects.get(user__pk=id).last_login_type
    elif Administrator.objects.filter(user__pk=id).exists():
        return Administrator.objects.get(user__pk=id).last_login_type
    else:
        return "Staff"


def assignType(id, login_type):
    if Participant.objects.filter(user__pk=id).exists():
        role = Participant.objects.get(user__pk=id)
        role.last_login_type = login_type
        role.save()
    if Instructor.objects.filter(user__pk=id).exists():
        role = Instructor.objects.get(user__pk=id)
        role.last_login_type = login_type
        role.save()
    if HR.objects.filter(user__pk=id).exists():
        role = HR.objects.get(user__pk=id)
        role.last_login_type = login_type
        role.save()
    if Administrator.objects.filter(user__pk=id).exists():
        role = Administrator.objects.get(user__pk=id)
        role.last_login_type = login_type
        role.save()


def login(request):
    from . import instructor_view as iv, participant_view as pv, administrator_view as av, hr_view as hv
    if request.method == 'GET':
        if request.user.is_authenticated():
            last_login_type = typeSelect(request.user.id)
            if last_login_type == "Participant":
                return pv.index(request)
            elif last_login_type == "Instructor":
                return iv.index(request)
            elif last_login_type == "HR":
                return hv.index(request)
            elif last_login_type == "Administrator":
                return av.index(request)
            else:
                return logout(request)
        else:
            form = LoginForm()
            return render_to_response('login.html', RequestContext(request, {'form': form, }))
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            staff_type = request.POST.get('staff_type')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                if staff_type == "1":
                    print('here')
                    auth.login(request, user)
                    if user.groups.filter(name='Participant').exists():
                        return pv.index(request)
                    else:
                        # TODO: wrong access
                        return logout(request)
                elif staff_type == '2':
                    auth.login(request, user)
                    if user.groups.filter(name='Instructor').exists():
                        return iv.index(request)
                    else:
                        # TODO: wrong access
                        return logout(request)
                elif staff_type == '3':
                    auth.login(request, user)
                    if user.groups.filter(name='HR').exists():
                        return hv.index(request)
                    else:
                        # TODO: wrong access
                        return logout(request)
                elif staff_type == '4':
                    auth.login(request, user)
                    if user.groups.filter(name='Administrator').exists():
                        return av.index(request)
                    else:
                        # TODO: wrong access
                        return logout(request)
                else:
                    # TODO: login for other users
                    return render_to_response('login.html', RequestContext(request, {'form': form, }))
            else:
                return render_to_response('login.html', RequestContext(request, {'form': form, 'password_is_wrong': True, }))
        else:
            return render_to_response('login.html', RequestContext(request, {'form': form, }))


@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")


def participant_registration(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render_to_response('registration.html', RequestContext(request, {'form': form, }))
    else:
        from . import instructor_view as iv, participant_view as pv, administrator_view as av, hr_view as hv
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            passwordValidate = request.POST.get('password_again', '')
            if Participant.objects.filter(user__username=username).exists():
                return render_to_response('registration.html', RequestContext(request, {'form': form, 'duplicate_username': True}))
            if password != passwordValidate:
                return render_to_response('registration.html', RequestContext(request, {'form': form, 'password_is_wrong': True}))
            participant_init = Participant.objects.get(user__username='0')
            participant_init.register(username, password)
            return render_to_response('registration.html', RequestContext(request, {'form': form, 'register_success' : True}))
        else:
            return render_to_response('registration.html', RequestContext(request, {'form': form, }))
