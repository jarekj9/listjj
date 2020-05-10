from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
#for auth:
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout, authenticate, login
#for registration:
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

import app.main
import datetime


#filter only users, that are members of group
def is_member(user):
    return user.groups.filter(name='accessGroup').exists()

#better form, can use instead of UserCreationForm
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, max_length=50)
    last_name = forms.CharField(required=True, max_length=50)

    #Meta inspects the current model of the class User, then ensures that 6 of the fields inside of it are there
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class CategoryForm(forms.Form):
    category = forms.CharField(max_length=100)

class CategoryModelChoiceField(forms.ModelChoiceField):  #to display specific label in ChoiceField
    def label_from_instance(self, obj):
         return obj.category

class NoteForm(forms.Form):
    def __init__(self, *args, **kwargs):   #I need to access 'request.user' via constructor during object creation
        login = kwargs.pop('login')
        super(NoteForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Categories.objects.filter(login=login)

    date = forms.DateField(initial=datetime.date.today)
    value = forms.FloatField() 
    category = CategoryModelChoiceField(required=True, widget=forms.Select, queryset = None)   #queryset for category is set in constructor
    description = forms.CharField(max_length=100)

class FilterNotesForm(forms.Form):
    def initial_start_date():
        return datetime.date.today() - datetime.timedelta(days=30)

    startdate = forms.DateField(label=u'From ',initial=initial_start_date)
    stopdate = forms.DateField(label=u'To ',initial=datetime.date.today)

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)   			#can use simpler: UserCreationForm
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            login(request, user)
            return redirect("/")

        else:
            for msg in form.error_messages:
                print(form.error_messages[msg])

            return render(request = request,
                          template_name = "registration/signup.html",
                          context={"form":form})

    form = UserRegisterForm
    return render(request = request,
                  template_name = "registration/signup.html",
                  context={"form":form})

@login_required
@user_passes_test(is_member)
def addnote(request):   
    if request.method == "POST":     
        form = NoteForm(request.POST,login=request.user)
        if form.is_valid():
            date = form.cleaned_data['date']
            value = form.cleaned_data['value']
            categoryobj = form.cleaned_data['category']
            description = form.cleaned_data['description']
            note = Journal(login=request.user, date=date, value=value, category=categoryobj, description=description)
            note.save()
            return redirect("/")
        else:
            return HttpResponse("Wrong user input")
    else:
        return HttpResponse("No POST request")

@login_required
@user_passes_test(is_member)
def deletenote(request):
    if request.method == "POST":
        id = request.POST.get('id')
        Journal.objects.filter(id=id).delete()
        return redirect("/")
    else:
        return HttpResponse("No POST request")

@login_required
@user_passes_test(is_member)
def add_category(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST":     
        if form.is_valid():
            category = form.cleaned_data['category']
            newcategory = Categories(login=request.user, category=category)
            newcategory.save()
            return redirect("/modify_categories")
        else:
            return HttpResponse("Wrong user input")
    else:
        return render(request, "modify_categories.html", {'categoryform':form,
                                                          'categories':Categories.objects.filter(login=request.user).values_list('id','category'),
                                                          'login':request.user })

@login_required
@user_passes_test(is_member)
def delete_category(request):
    if request.method == "POST":
        Categories.objects.filter(id=request.POST.get('category_id'), login=request.user).delete()
        return redirect("/modify_categories")

    else:
        return HttpResponse("No POST request")

    
@login_required
@user_passes_test(is_member)
def index(request,
          startdate = datetime.date.today() - datetime.timedelta(days=30),
          stopdate = datetime.date.today()):

    note_form = NoteForm(login=request.user)
    filter_notes_form = FilterNotesForm(request.POST or None)

    if request.method == "POST":   #filtering dates
        if filter_notes_form.is_valid():
            startdate = filter_notes_form.cleaned_data['startdate']
            stopdate = filter_notes_form.cleaned_data['stopdate']
        else:
            return HttpResponse("Wrong user input")

    
    all_records = app.main.show_notes(request.user, startdate, stopdate)
    return render(request, 'add_note.html', {'all_records': all_records,
                                             'summary': app.main.page_summary(all_records),
                                             'noteform': note_form,
                                             'filterform': filter_notes_form, 
                                             'message': '',
                                             'login': request.user})


