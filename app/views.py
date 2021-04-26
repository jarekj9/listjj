import shutil
import os
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.http import JsonResponse
from django.views import View
from django.core.files.storage import FileSystemStorage
from django.core import serializers
from django.http import HttpResponse, Http404, StreamingHttpResponse, FileResponse
from .models import *
from .forms import *


# for auth:
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin

# for registration:
from django.contrib.auth.models import User

# api:
from .serializers import JournalSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from .notes_service import NotesService
import datetime
import csv
import urllib, mimetypes
from wsgiref.util import FileWrapper


# filter only users, that are members of group
def is_member(user):
    """Test user membership to authorize the access"""
    return user.groups.filter(name="accessGroup").exists()

class GroupMembershipRequired(UserPassesTestMixin):
    '''Manage user permissions to access views'''
    def test_func(self):
        return self.request.user.groups.filter(name="accessGroup").exists()

class NotesListView(LoginRequiredMixin, GroupMembershipRequired, NotesService, View):
    '''Main Page'''

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.filter = self.set_filter(request)
        self.note_form = NoteForm(login=request.user, recent_category=self.get_recent_category(request))
        self.edited_note_id = None
        if kwargs.get('edited_note_id'):
            self.edited_note_id = kwargs.pop('edited_note_id')
            self.note_form = kwargs.pop('note_form')
        self.filter_notes_form = self.make_filter_notes_form(request)
        return super().dispatch(request, *args, **kwargs)

    def make_filter_notes_form(self, request):
        filter_notes_form = FilterNotesForm(
            request.POST or None,
            login=request.user,
            filter=self.filter,
            initial={
                "category": self.filter["category"][0],
                "startdate": self.filter["startdate"],
                "stopdate": self.filter["stopdate"],
            })
        return filter_notes_form

    def get(self, request):
        """View main page"""
        import_form = ImportForm()
        record_list = self.get_all_notes(request.user, self.filter)
        temp_path = os.path.join('media', 'attachments', f'{request.user.id}', 'temp')
        shutil.rmtree(temp_path, ignore_errors=True)

        return render(request, "add_note.html",
            {
                "all_records": record_list,
                "summary": self.page_values_sum(record_list),
                "noteform": self.note_form,
                "edited_note_id": self.edited_note_id,
                "filterform": self.filter_notes_form,
                "filter": self.filter,
                "import_form": import_form,
                "message": "",
                "login": request.user,
            })

    def post(self, request):
        """Refresh main page after filter has changed"""
        if self.filter_notes_form.is_valid():
            category_obj = self.filter_notes_form.cleaned_data["category"]
            category_id = None if not category_obj else category_obj.id
            filter = {
                "startdate": str(self.filter_notes_form.cleaned_data["startdate"]),
                "stopdate": str(self.filter_notes_form.cleaned_data["stopdate"]),
                "category": [category_id],  # it is always [None] or [int]
                "setdate": str(datetime.date.today()),  # for cookies expiration only
            }
            request.session.update(filter)
            return redirect("/")
        else:
            return HttpResponse("Wrong user input")


class DownloadFileView(LoginRequiredMixin, GroupMembershipRequired, View):
    def get(self, request, *args, **kwargs):
        attachment_id = kwargs.get('attachment_id')
        attachment = Attachment.objects.get(id=attachment_id)
        file_wrapper = FileWrapper(open(attachment.file.path,'rb'))
        file_mimetype = mimetypes.guess_type(attachment.file.path)
        response = HttpResponse(file_wrapper, content_type=file_mimetype )
        response['X-Sendfile'] = attachment.file
        response['Content-Length'] = os.stat(attachment.file.path).st_size
        response['Content-Disposition'] = 'attachment; filename=%s/' % str(attachment.file_name) 
        return response

class EditNoteView(LoginRequiredMixin, GroupMembershipRequired, View):

    def dispatch(self, request, *args, **kwargs):
        self.note_form = NoteForm(request.POST or None, login=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, note_id):
        """Prepare edit form and pass to NotesListView"""
        try:
            edited_note = Journal.objects.get(id=note_id, login=request.user)
        except Journal.DoesNotExist:
            return HttpResponse("You do not have such note.")

        self.note_form.fields["value"].initial = edited_note.value
        self.note_form.fields["category"].initial = edited_note.category
        self.note_form.fields["description"].initial = edited_note.description

        return NotesListView.as_view()(request, note_form=self.note_form, edited_note_id=note_id)

    def post(self, request):
        """Save edited note"""
        if self.note_form.is_valid():
            note_id = request.POST.get("note_id")
            new_value = self.note_form.cleaned_data["value"]
            new_category_id = self.note_form.cleaned_data["category"]
            new_description = self.note_form.cleaned_data["description"]
            edited_note = Journal.objects.get(id=note_id, login=request.user)
            edited_note.value = new_value
            edited_note.category = new_category_id
            edited_note.description = new_description
            edited_note.save()
            return redirect("/")


class AddCategoryView(LoginRequiredMixin, GroupMembershipRequired, View):

    def dispatch(self, request, *args, **kwargs):
        self.category_form = CategoryForm(request.POST or None)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Render form to add new category"""
        return render(request, "modify_categories.html",{
                "categoryform": self.category_form,
                "categories": Categories.objects.filter(login=request.user).values_list("id", "category"),
                "login": request.user,
            })

    def post(self, request):
        '''Save new category'''
        if self.category_form.is_valid():
            category = self.category_form.cleaned_data["category"]
            newcategory = Categories(login=request.user, category=category)
            newcategory.save()
            return redirect("/modify_categories")
        else:
            return HttpResponse("Wrong user input")

class EditCategoryView(LoginRequiredMixin, GroupMembershipRequired, View):

    def dispatch(self, request, *args, **kwargs):
        self.category_form = CategoryForm(request.POST or None)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, category_id=None):
        """Render form to edit category name"""
        try:
            old_category_name = Categories.objects.get(id=category_id, login=request.user).category
        except Categories.DoesNotExist:
            return HttpResponse("You do not have such category")
        self.category_form.fields["category"].initial = old_category_name
        return render(request,"modify_categories.html",
            {
                "categoryform": self.category_form,
                "categories": Categories.objects.filter(login=request.user).values_list("id", "category"),
                "login": request.user,
                "old_category_name": old_category_name,
                "category_id": category_id,
            })

    def post(self, request):
        """Save edited category"""
        if self.category_form.is_valid():
            new_category_name = self.category_form.cleaned_data["category"]
            category_id = request.POST.get("category_id")
            edited_category = Categories.objects.get(id=category_id, login=request.user)
            edited_category.category = new_category_name
            edited_category.save()
            return redirect("/modify_categories")

class RegisterView(View):

    def get(self, request):
        form = UserRegisterForm
        return render(
            request=request,
            template_name="registration/signup.html",
            context={"form": form},
        )

    def post(self, request):
        if request.method == "POST":
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect("/accounts/login")

            else:
                for msg in form.error_messages:
                    print(form.error_messages[msg])
                return render(
                    request=request,
                    template_name="registration/signup.html",
                    context={"form": form},
                )


class JournalViewSet(viewsets.ModelViewSet):
    """Api access"""
    permission_classes = (IsAuthenticated,)  # without it api is open
    queryset = Journal.objects.all().select_related('category')
    serializer_class = JournalSerializer


class GetApiTokenView(LoginRequiredMixin, GroupMembershipRequired, View):
    '''Will delete and create token, then return as json response'''
    def get(self,request):
        Token.objects.filter(user=request.user).delete()
        token = Token.objects.create(user=request.user).key
        return JsonResponse({'token': token})
            

class AddNoteView(LoginRequiredMixin, GroupMembershipRequired, NotesService, View):

    def post(self,request):
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
            attachments = self.save_attachments(request, note)
            if attachments:
                attachments = json.loads(serializers.serialize('json', attachments))

            filter = self.set_filter(request)
            record_list = self.get_all_notes(request.user, filter)
            value_sum = self.page_values_sum(record_list)
            return JsonResponse({'saved': True,
                                 'value_sum': value_sum,
                                 'category': categoryobj.category,
                                 'id': note.id,
                                 'date': date.strftime('%d-%m-%Y'),
                                 'attachments': attachments})
        else:
            return JsonResponse({'saved': False})

class SaveTempAttachmentView(LoginRequiredMixin, GroupMembershipRequired, View):
    
    def post(self,request):
        print(request.FILES)
        file = request.FILES.get('file')
        fs = FileSystemStorage(f'media/attachments/{request.user.id}/temp')
        filename = fs.save(file.name, file)
        file_url = fs.url(filename)
        return JsonResponse({'file_url': file_url})

class DeleteNoteView(LoginRequiredMixin, GroupMembershipRequired, NotesService, View):

    def post(self, request):
        """Delete users note, ajax way"""
        id = request.POST.get("note_id")
        attachment = Attachment.objects.filter(journal_id=id)
        attachment_directory = os.path.dirname(attachment[0].file.path) if len(attachment) else None
        if attachment_directory:
            shutil.rmtree(attachment_directory)
        delete_result = Journal.objects.filter(id=id).delete()
        if delete_result[0]:
            filter = self.set_filter(request)
            record_list = self.get_all_notes(request.user, filter)
            value_sum = self.page_values_sum(record_list)
            return JsonResponse({'deleted': True, 'value_sum': value_sum})

class DeleteCategoryView(LoginRequiredMixin, GroupMembershipRequired, View):

    def post(self, request):
        """Will delete category, which belongs to user"""
        user = User.objects.get(id=request.user.id)
        user.profile.default_category = None
        user.save()
        category_id = request.POST.get("category_id")
        Categories.objects.filter(id=category_id, login=request.user).delete()
        request.session.update(
            {"category": [None]}
        )  # reset category in cookies to avoid any errors
        return redirect("/modify_categories")


class SetDefaultCategoryView(LoginRequiredMixin, GroupMembershipRequired, View):
    def post(self, request):
        """To set default category in user.profile - for category filter and adding notes"""
        user = User.objects.get(id=request.user.id)
        id = request.POST.get("category_id")
        if id == "remove_default":
            user.profile.default_category = None
            user.save()
            return redirect("/modify_categories")
        user.profile.default_category = Categories.objects.get(id=id, login=request.user)
        user.save()
        return redirect("/modify_categories")


class ExportNotesView(LoginRequiredMixin, GroupMembershipRequired, View):

    def get(self, request):
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


class ImportNotesView(LoginRequiredMixin, GroupMembershipRequired, View):

    def post(self, request):
        """Takes uploaded csv file and adds its data to database. Also adds missing categories."""
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
                return HttpResponse("The file has errors, each line needs to have 6 comma-separated fields")
        else:
            return HttpResponse("Invalid file")
