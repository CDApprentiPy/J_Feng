# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, redirect
from django.core.urlresolvers import reverse
from .forms import Register, Login
from django.contrib import messages
from .models import User
import bcrypt


# Create your views here.
def index(request):
    forms = {
        "registration_form": Register(),
        "login_form": Login(),
    }
    return render(request, "login_reg/index.html", forms)

def success(request, id, session_type):
    content = {
        "user": User.objects.get(id=id),
        "session_type": session_type,
    }
    return render(request, "login_reg/success.html", content)

def process(request):
    if request.method == "POST":
        errors = User.objects.registration_validate(request.POST)
        if len(errors):
            for tab, error in errors.iteritems():
                messages.error(request, error)
            return redirect(reverse("logreg:logreg_index"))
        else:
            register = Register(request.POST)
            if register.is_valid():
                user = User()
                user.first_name = register.cleaned_data["first_name"].capitalize()
                user.last_name = register.cleaned_data["last_name"].capitalize()
                user.email = register.cleaned_data["email"]
                user.birthday = register.cleaned_data["birthday"]
                user.password = bcrypt.hashpw(register.cleaned_data["password"].encode(), bcrypt.gensalt())
                user.save()

                curr_user = User.objects.get(email=user.email)

                try:
                    request.session["user_logged"]
                except KeyError:
                    request.session["user_logged"] = True
                    request.session["user_id"] = curr_user.id
                    request.session["session_type"] = "registration"
                return redirect(reverse("logreg:logreg_success", kwargs={'id':request.session["user_id"],'session_type':request.session["session_type"]}))

def login(request):
    if request.method == "POST":
        errors = User.objects.login_validate(request.POST)
        if len(errors):
            for tab, error in errors.iteritems():
                messages.error(request, error)
            return redirect(reverse("logreg:logreg_index"))
        else:
            login = Login(request.POST)
            if login.is_valid():
                curr_user = User.objects.get(email=request.POST["email"])

                try:
                    request.session["user_logged"]
                except KeyError:
                    request.session["user_logged"] = True
                    request.session["user_id"] = curr_user.id
                    request.session["session_type"] = "login"
                return redirect(reverse("logreg:logreg_success", kwargs={'id':request.session["user_id"],'session_type':request.session["session_type"]}))

def logout(request):
    del request.session["user_logged"]
    return redirect(reverse("logreg:logreg_index"))