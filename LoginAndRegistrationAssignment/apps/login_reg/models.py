# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, redirect
from django.db import models
import re, bcrypt


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

# Create your models here.
class UserManager(models.Manager):
    def registration_validate(self, postData):
        errors = {}
        registered_emails = User.objects.filter(email=postData["email"])
        
        # Checks if form is empty.
        # for key, value in postData.items():
        #     if len(value) < 1:
        #         errors["empty"] = "Please complete all fields."
        #         return errors

        # Checks if email is already registered.
        if len(registered_emails) > 0:
            errors["email"] = "This email is already registered."
            return errors

        # Checks names for character lengths.
        # if len(postData["first_name"]) < 2 or len(postData["last_name"]) < 2:
        #     errors["first_name"] = "Name must be at least 2 characters."

        # Checks names for characters.
        if not postData["first_name"].isalpha() or not postData["last_name"].isalpha():
            errors["first_name"] = "Name must only contain alphabetical letters."

        # Checks if email is valid.
        # if len(postData["email"]) < 1:
        #     errors["email"] = "Email must not be blank."
        if not EMAIL_REGEX.match(postData["email"]):
            errors["email"] = "Email is invalid."

        # Checks password and whether it matches.
        # if len(postData["password"]) < 7:
        #     errors["password"] = "Password must be at least 8 characters."
        if postData["password"] != postData["cpassword"]:
            errors["cpassword"] = "Passwords must match."

        # Checks if birthdate is valid.
        if postData["birthday_month"] != 1 and postData["birthday_month"] != 3 and postData["birthday_month"] != 5 and postData["birthday_month"] != 7 and postData["birthday_month"] != 8 and postData["birthday_month"] != 10 and postData["birthday_month"] != 12:
            if int(postData["birthday_month"]) == 2:
                if int(postData["birthday_year"]) % 4 != 0:
                    if int(postData["birthday_day"]) > 28:
                        errors["birthday"] = "Date must be 28 or earlier."
                elif int(postData["birthday_year"]) % 100 == 0 and int(postData["birthday_year"]) % 400 != 0:
                    if int(postData["birthday_day"]) > 28:
                        errors["birthday"] = "Date must be 28 or earlier."
                else:
                    if int(postData["birthday_day"]) > 29:
                        errors["birthday"] = "Date must be 29 or earlier."
            else:
                if int(postData["birthday_day"]) > 30:
                    errors["birthday"] = "Date must be 30 or earlier."

        return errors

    def login_validate(self, postData):
        errors = {}

        # Check if inputted email is registered (in the database).
        registered_emails = User.objects.filter(email=postData["email"])
        
        if len(registered_emails) == 0:
            errors["email"] = "This email is not registered."
            return errors

        # Check if password matches password in the database.
        password = str(postData["password"])
        hashedpw = str(registered_emails[0].password)

        if not bcrypt.checkpw(password.encode(), hashedpw):
            errors["password"] = "Password is incorrect."
        
        return errors

class User(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.EmailField(max_length=45)
    password = models.CharField(max_length=45)
    birthday = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()