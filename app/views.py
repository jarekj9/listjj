from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from .models import *
from .forms import *

# for auth:
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login

# for registration:
from django.contrib.auth.models import User

# api:
from .serializers import JournalSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

import datetime
import csv

# filter only users, that are members of group
def is_member(user):
    """Test user membership to authorize the access"""
    return user.groups.filter(name="accessGroup").exists()


def register(request):
    """View to Register new user"""
    if request.method == "POST":
        form = UserRegisterForm(request.POST)  # can use simpler: UserCreationForm
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            login(request, user)
            return redirect("/")

        else:
            for msg in form.error_messages:
                print(form.error_messages[msg])

            return render(
                request=request,
                template_name="registration/signup.html",
                context={"form": form},
            )

    form = UserRegisterForm
    return render(
        request=request,
        template_name="registration/signup.html",
        context={"form": form},
    )


@login_required
@user_passes_test(is_member)
def addnote(request):
    """Add note/post for a user"""
    if request.method == "POST":
        form = NoteForm(request.POST, login=request.user)
        if form.is_valid():
            date = datetime.date.today()
            value = form.cleaned_data["value"]
            categoryobj = form.cleaned_data["category"]
            description = form.cleaned_data["description"]
            note = Journal(
                login=request.user,
                date=date,
                value=value,
                category=categoryobj,
                description=description,
            )
            note.save()
            return redirect("/")
        else:
            return HttpResponse("Wrong user input")
    else:
        return HttpResponse("No POST request")


@login_required
@user_passes_test(is_member)
def delete_note(request):
    """Delete users note, NOT USED"""
    if request.method == "POST":
        id = request.POST.get("id")
        Journal.objects.filter(id=id).delete()
        return redirect("/")
    else:
        return HttpResponse("No POST request")


@login_required
@user_passes_test(is_member)
def delete_note_ajax(request):
    """Delete users note"""
    if request.method == "POST":
        id = request.POST.get("note_id")
        delete_result = Journal.objects.filter(id=id).delete()
        if delete_result[0]:
            filter = set_filter(request)
            record_list = get_all_notes(request.user, filter)
            value_sum = page_values_sum(record_list)
            return JsonResponse({'deleted': True, 'value_sum': value_sum})
        return JsonResponse({'deleted': False})
    else:
        return HttpResponse("No DELETE request")

@login_required
@user_passes_test(is_member)
def edit_note_view(request, note_id=None):
    """Edit note/post for a user"""

    note_form = NoteForm(request.POST or None, login=request.user)
    if request.method == "POST":
        if note_form.is_valid():
            user = User.objects.get(id=request.user.id)
            note_id = request.POST.get("note_id")
            new_value = note_form.cleaned_data["value"]
            new_category_id = note_form.cleaned_data["category"]
            new_description = note_form.cleaned_data["description"]
            edited_note = Journal.objects.get(id=note_id, login=request.user)
            edited_note.value = new_value
            edited_note.category = new_category_id
            edited_note.description = new_description
            edited_note.save()
            return redirect("/")

    filter = set_filter(request)
    filter_notes_form = FilterNotesForm(
        login=request.user,
        filter=filter,
        initial={
            "category": filter["category"][0],
            "startdate": filter["startdate"],
            "stopdate": filter["stopdate"],
        },
    )
    import_form = ImportForm()

    try:
        edited_note = Journal.objects.get(id=note_id, login=request.user)
    except Journal.DoesNotExist:
        return HttpResponse("You do not have such note.")

    note_form.fields["value"].initial = edited_note.value
    note_form.fields["category"].initial = edited_note.category
    note_form.fields["description"].initial = edited_note.description

    record_list = get_all_notes(request.user, filter)
    return render(
        request,
        "add_note.html",
        {
            "all_records": record_list,
            "summary": page_values_sum(record_list),
            "noteform": note_form,
            "filterform": filter_notes_form,
            "filter": filter,
            "import_form": import_form,
            "message": "",
            "login": request.user,
            "edited_note": edited_note,
        },
    )


@login_required
@user_passes_test(is_member)
def add_category_view(request):
    """Add new category for a user"""
    form = CategoryForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            category = form.cleaned_data["category"]
            newcategory = Categories(login=request.user, category=category)
            newcategory.save()
            return redirect("/modify_categories")
        else:
            return HttpResponse("Wrong user input")
    else:
        return render(
            request,
            "modify_categories.html",
            {
                "categoryform": form,
                "categories": Categories.objects.filter(login=request.user).values_list(
                    "id", "category"
                ),
                "login": request.user,
            },
        )


@login_required
@user_passes_test(is_member)
def delete_category(request):
    """Will delete category, which belongs to user"""
    if request.method == "POST":
        user = User.objects.get(id=request.user.id)
        user.profile.default_category = None
        user.save()
        category_id = request.POST.get("category_id")
        Categories.objects.filter(id=category_id, login=request.user).delete()
        request.session.update(
            {"category": [None]}
        )  # reset category in cookies to avoid any errors
        return redirect("/modify_categories")
    else:
        return HttpResponse("No POST request")


@login_required
@user_passes_test(is_member)
def edit_category_view(request, category_id=None):
    """View to edit category name, which belongs to user"""

    form = CategoryForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = User.objects.get(id=request.user.id)
        new_category_name = form.cleaned_data["category"]
        category_id = request.POST.get("category_id")
        edited_category = Categories.objects.get(id=category_id, login=request.user)
        edited_category.category = new_category_name
        edited_category.save()
        return redirect("/modify_categories")

    try:
        old_category_name = Categories.objects.get(
            id=category_id, login=request.user
        ).category
    except Categories.DoesNotExist:
        return HttpResponse("You do not have such category")
    form.fields["category"].initial = old_category_name
    return render(
        request,
        "modify_categories.html",
        {
            "categoryform": form,
            "categories": Categories.objects.filter(login=request.user).values_list(
                "id", "category"
            ),
            "login": request.user,
            "old_category_name": old_category_name,
            "category_id": category_id,
        },
    )


@login_required
@user_passes_test(is_member)
def set_default_category(request):
    """To set default category in user.profile - for category filter and adding notes"""
    user = User.objects.get(id=request.user.id)
    if request.method == "POST":
        id = request.POST.get("category_id")
        if id == "remove_default":
            user.profile.default_category = None
            user.save()
            return redirect("/modify_categories")

        user.profile.default_category = Categories.objects.get(
            id=id, login=request.user
        )
        user.save()
        return redirect("/modify_categories")

    return HttpResponse("No POST request")


@login_required
@user_passes_test(is_member)
def export_notes(request):
    """Returns csv file for download, with all user notes"""
    csv_response = HttpResponse(content_type="text/csv")
    csv_response["Content-Disposition"] = 'attachment; filename="export.csv"'
    all_records = Journal.objects.filter(login=request.user)

    for item in all_records:
        one_row_tab = [
            item.id,
            item.login.username,
            item.date,
            item.value,
            item.category.category,
            item.description,
        ]
        writer = csv.writer(csv_response)
        writer.writerow(one_row_tab)

    return csv_response


@login_required
@user_passes_test(is_member)
def import_notes(request):
    """Takes uploaded csv file and adds its data to database. Also adds missing categories."""
    if request.method == "POST":
        importform = ImportForm(request.POST, request.FILES)
        if importform.is_valid():
            file = request.FILES["file"]

            try:
                data = file.read().decode("utf-8")
            except UnicodeDecodeError:
                return HttpResponse("Cannot decode this file, is this a valid csv ?")
            lines = data.split("\n")[:-1]

            try:
                for row in lines:
                    rowtab = row.split(",")
                    if not Categories.objects.filter(category=rowtab[4]).exists():
                        missing_category = Categories(login=request.user, category=rowtab[4])
                        missing_category.save()

                    note = Journal(
                        login=request.user,
                        date=rowtab[2],
                        value=rowtab[3],
                        category=Categories.objects.get(category=rowtab[4]),
                        description=rowtab[5],
                    )
                    note.save()
                return redirect("/")
            except IndexError:
                return HttpResponse(
                    "The file has errors, each line needs to have 6 comma-separated fields"
                )
        else:
            return HttpResponse("Invalid file")
    else:
        return HttpResponse("No POST request")


def get_all_notes(login, filter):
    """Returns list of dicts with notes for specific user"""
    output = []

    if filter["category"] == [None]:
        filter["category"] = Categories.objects.all()

    all_records = Journal.objects.filter(
        login=login,
        date__range=(filter["startdate"], filter["stopdate"]),
        category__in=filter["category"],
    ).order_by("date")
    for item in all_records:
        output.append(
            {
                "id": item.id,
                "login": item.login.username,  # related object
                "date": item.date.strftime("%d-%m-%Y"),
                "value": item.value,
                "category": item.category.category,  # related object
                "description": item.description,
            }
        )

    return output


def page_values_sum(notes):
    """Counts summary for specific notes from def "show_notes" """
    value_sum = sum([item.get("value") for item in notes])
    return value_sum


class JournalViewSet(viewsets.ModelViewSet):
    """Api access"""
    permission_classes = (IsAuthenticated,)  # without it api is open
    queryset = Journal.objects.all().select_related('category')
    serializer_class = JournalSerializer


def set_filter(request):
    """Set filter with default category and dates, to display notes"""
    filter = {
        "startdate": datetime.date.today() - datetime.timedelta(days=365),
        "stopdate": datetime.date.today(),
        "category": [None],
    }

    if request.user.profile.default_category:  # change filter category to user default if user has it
        default_category = Categories.objects.get(
            login=request.user.id, id=request.user.profile.default_category.id
        )
        filter.update({"category": [default_category,]})

    # if filter was NOT set today - dont read any further
    if str(request.session.get("setdate")) < str(datetime.date.today()):
        return filter

    # change filter to last choices from cookies, if it exist
    if request.session.get("category") not in [[None], None,]:
        category_id = Categories.objects.get(id=request.session["category"][0])
        filter.update(
            {
                "category": [category_id],
                "startdate": request.session.get("startdate"),
                "stopdate": request.session.get("stopdate"),
            })
    return filter


@login_required
@user_passes_test(is_member)
def index(request):
    """View with the main page"""
    filter = set_filter(request)
    note_form = NoteForm(login=request.user)
    filter_notes_form = FilterNotesForm(
        request.POST or None,
        login=request.user,
        filter=filter,
        initial={
            "category": filter["category"][0],
            "startdate": filter["startdate"],
            "stopdate": filter["stopdate"],
        },
    )
    import_form = ImportForm()

    if request.method == "POST":
        if filter_notes_form.is_valid():
            category_obj = filter_notes_form.cleaned_data["category"]
            category_id = None if not category_obj else category_obj.id
            filter = {
                "startdate": str(
                    filter_notes_form.cleaned_data["startdate"]
                ),  # filtering dates
                "stopdate": str(filter_notes_form.cleaned_data["stopdate"]),
                "category": [category_id],  # it is always [None] or [int]
                "setdate": str(datetime.date.today()),
            }  # for cookies expiration only

            request.session.update(
                filter
            )  # save to cookies: last form start/stop dates and category.id
        else:
            return HttpResponse("Wrong user input")

    record_list = get_all_notes(request.user, filter)
    return render(
        request,
        "add_note.html",
        {
            "all_records": record_list,
            "summary": page_values_sum(record_list),
            "noteform": note_form,
            "filterform": filter_notes_form,
            "filter": filter,
            "import_form": import_form,
            "message": "",
            "login": request.user,
        },
    )
