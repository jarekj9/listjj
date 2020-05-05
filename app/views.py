from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
import app.main

#for auth:
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout, authenticate, login
#for registration:
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

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
        
class NoteForm(forms.Form):

    categories= [
    ('inne', 'inne'),
    ('samochod', 'samochod'),
    ('mieszkanie', 'mieszkanie'),
    ]
    
    value = forms.IntegerField() 
    category = forms.CharField(widget=forms.Select(choices=categories))
    description = forms.CharField(max_length=100)

def deletenote(request):
    if request.method == "POST":
        id = request.GET.get('id')
        return HttpResponse(id)

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
 
            
def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, "db.html", {"greetings": greetings})

    
@login_required
@user_passes_test(is_member)
def index(request):
    noteform = NoteForm()
    all_records = app.main.main()
    
    if request.method == "POST":
           
        form = NoteForm(request.POST)
        if form.is_valid():
            value = form.cleaned_data['value']
            category = form.cleaned_data['category']
            description = form.cleaned_data['description']
            note = Journal(value=value, category=Categories.objects.get(category=category), description=description)
            note.save()
        
            return render(request, "journal_add_note.html", {"all_records":app.main.main(), 'noteform':noteform, 'message':'Note saved.'})
        else:
            return render(request, "journal_add_note.html", {"all_records":app.main.main(), 'noteform':noteform, 'message':'Wrong form input'})
        
    else: 
        return render(request, "journal_add_note.html", {"all_records":app.main.main(), 'noteform':noteform, 'message':''})


