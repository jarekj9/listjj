from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from .models import *
#for auth:
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout, authenticate, login
#for registration:
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms.widgets import NumberInput, TextInput
from .serializers import JournalSerializer
from rest_framework import viewsets

import app.main
import datetime
import csv

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
    def __init__(self, *args, **kwargs):   # I need to access 'request.user' via constructor during object creation
        login = kwargs.pop('login')
        super(NoteForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Categories.objects.filter(login=login)
        self.fields['value'] = forms.IntegerField(initial=0)

    class Meta:         # because date variable is ignored in the Form (it is set in addnote method)
        model = Journal
        exclude = ["date"]

    value = forms.FloatField(widget=NumberInput()) 
    category = CategoryModelChoiceField(required=True, widget=forms.Select, queryset = None, initial=0)   #queryset for category is set in constructor
    description = forms.CharField(max_length=100, widget=TextInput(attrs={'size': '20'}))

class FilterNotesForm(forms.Form):
    def __init__(self, *args, **kwargs):   # I need to access 'request.user' via constructor during object creation
        login = kwargs.pop('login')
        super(FilterNotesForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Categories.objects.filter(login=login)

    def initial_start_date():
        return datetime.date.today() - datetime.timedelta(days=30)

    startdate = forms.DateField(label=u'From ',initial=initial_start_date)
    stopdate = forms.DateField(label=u'To ',initial=datetime.date.today)
    category = CategoryModelChoiceField(required=False,empty_label='all', widget=forms.Select, queryset = None)

class ImportForm(forms.Form):
    file = forms.FileField(
        label='Import from csv',
        help_text=''
    )

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
            date = datetime.date.today()
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
def export_view(request):
    return export_data(request.user)

def export_data(login):
    
    csv_response = HttpResponse(content_type='text/csv')
    csv_response['Content-Disposition'] = 'attachment; filename="export.csv"'
    all_records = Journal.objects.filter(login = login)
    
    for item in all_records:
        one_row_tab = [item.id, item.login.username, item.date, item.value, 
               item.category.category, item.description]
        writer = csv.writer(csv_response)
        writer.writerow(one_row_tab)

    return csv_response

@login_required
@user_passes_test(is_member)
def import_view(request):
    '''Takes uploaded csv file and adds its data to database. Also adds missing categories.'''
    if request.method == 'POST':
        importform = ImportForm(request.POST, request.FILES)
        if importform.is_valid():
            file = request.FILES['file']      
            
            try:
                data = file.read().decode("utf-8")  
            except UnicodeDecodeError:
                return HttpResponse('Cannot decode this file, is this a valid csv ?')
            lines = data.split("\n")[:-1]
            
            try:
                for row in lines:
                    rowtab = row.split(',')
                    if not Categories.objects.filter(category = rowtab[4]).exists():
                        missing_category = Categories(login=request.user, category = rowtab[4])
                        missing_category.save()

                    note = Journal(login = request.user, 
                                date = rowtab[2],
                                value = rowtab[3],
                                category = Categories.objects.get(category = rowtab[4]),
                                description = rowtab[5])
                    note.save()
                #import pdb; pdb.set_trace()
                return redirect('/')
            except IndexError:
                return HttpResponse('The file has errors, each line needs to have 6 comma-separated fields')
        else:
            return HttpResponse('Invalid file')
    else:
        return HttpResponse('No POST request')


def all_notes(login, filter):
    '''Returns list of dicts with notes for specific user'''
    output=[]

    if not filter['category'][0]: filter['category'] = Categories.objects.all()

    all_records = Journal.objects.filter(login = login,
                                         date__range = (filter['startdate'],filter['stopdate']),
                                         category__in = filter['category']).order_by('date')
    for item in all_records:
        output.append({'id':item.id,
                       'login':item.login.username,  #related object
                       'date':item.date.strftime("%d-%m-%Y"),
                       'value':item.value,
                       'category':item.category.category,  #related object
                       'description':item.description})
    
    return output

def page_summary(notes):
    '''Counts summary for specific notes from def "show_notes" '''
    valuesum = sum([item.get('value') for item in notes])
    return valuesum


class JournalViewSet(viewsets.ModelViewSet):
    queryset = Journal.objects.all()
    serializer_class = JournalSerializer


@login_required
@user_passes_test(is_member)
def index(request,
          filter={'startdate': datetime.date.today() - datetime.timedelta(days=30),
                  'stopdate': datetime.date.today(),
                  'category': [None]}
         ):

    note_form = NoteForm(login=request.user)
    filter_notes_form = FilterNotesForm(request.POST or None,login=request.user)
    import_form = ImportForm()

    if request.method == "POST":   #filtering dates
        if filter_notes_form.is_valid():
            filter = {'startdate': filter_notes_form.cleaned_data['startdate'],
                      'stopdate': filter_notes_form.cleaned_data['stopdate'],
                      'category': [filter_notes_form.cleaned_data['category']]}
        else:
            return HttpResponse("Wrong user input")

    
    record_list = all_notes(request.user, filter)
    return render(request, 'add_note.html', {'all_records': record_list,
                                             'summary': page_summary(record_list),
                                             'noteform': note_form,
                                             'filterform': filter_notes_form,
                                             'filter': filter,
                                             'import_form':import_form, 
                                             'message': '',
                                             'login': request.user})


