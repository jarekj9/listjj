from .models import *

# for registration:
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from django.forms.widgets import NumberInput, TextInput

import datetime


class UserRegisterForm(UserCreationForm):
    """Better form to use instead of UserCreationForm"""

    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, max_length=50)
    last_name = forms.CharField(required=True, max_length=50)

    # Meta inspects the current model of the class User, then ensures that 6 of the fields inside of it are there
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]


class CategoryForm(forms.Form):
    category = forms.CharField(max_length=100)


class CategoryModelChoiceField(
    forms.ModelChoiceField
):  # to display specific label in ChoiceField
    def label_from_instance(self, obj):
        return obj.category


class NoteForm(forms.Form):
    """Form for adding new note"""

    def __init__(
        self, *args, **kwargs
    ):  # I need to access 'request.user' via constructor during object creation
        login = kwargs.pop("login")
        super(NoteForm, self).__init__(*args, **kwargs)
        self.fields["category"].queryset = Categories.objects.filter(login=login)
        self.fields["value"] = forms.FloatField(initial=0)

        try:
            default_category = Categories.objects.get(
                login=login, id=login.profile.default_category.id
            )
        except AttributeError:  # profile.default_category does not exist yet
            default_category = (0, 0)
        self.fields["category"].initial = default_category

    class Meta:  # because date variable is ignored in the Form (it is set in addnote method)
        model = Journal
        exclude = ["date"]

    value = forms.FloatField(widget=NumberInput())
    category = CategoryModelChoiceField(
        required=True, widget=forms.Select, queryset=None, initial=0
    )  # queryset for category is set in constructor
    description = forms.CharField(max_length=100, widget=TextInput())


class FilterNotesForm(forms.Form):
    """Form allows to filter notes on the main page"""

    def __init__(
        self, *args, **kwargs
    ):  # I need to access 'request.user' via constructor during object creation
        self.login = kwargs.pop("login")  # login is request.user
        self.filter = kwargs.pop("filter")
        super(FilterNotesForm, self).__init__(*args, **kwargs)
        self.fields["category"].queryset = Categories.objects.filter(login=self.login)

        try:
            default_category = Categories.objects.get(
                login=self.login, id=self.login.profile.default_category.id
            )
        except AttributeError:  # profile.default_category does not exist yet
            default_category = (0, 0)

    startdate = forms.DateField(
        label=u"From ",
        initial=None,
        widget=forms.DateInput(attrs={"id": "datepicker1", "style": "width:100px"}),
    )
    stopdate = forms.DateField(
        label=u"To ",
        initial=None,
        widget=forms.DateInput(attrs={"id": "datepicker2", "style": "width:100px"}),
    )
    category = CategoryModelChoiceField(
        label="Category ",
        required=False,
        widget=forms.Select(attrs={"onChange": "refresh()"}),
        empty_label="all",
        queryset=None,
    )  # queryset is None because i have it in init


class ImportForm(forms.Form):
    file = forms.FileField(
        label="Choose file to import from csv ",
        help_text="",
    )
