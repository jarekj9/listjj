from django.urls import path, include

from django.contrib import admin

admin.autodiscover()

from app.views import *

#for auth:
from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from django.conf.urls import include


urlpatterns = [
    path('', NotesListView.as_view(),name="index"),
    path("delete_note_ajax", DeleteNoteView.as_view(), name="delete_note_ajax"),
    path("add_note", AddNoteView.as_view(), name="add_note"),
    path("edit_note", EditNoteView.as_view(), name="edit_note"),
    re_path("edit_note/(?P<note_id>[^/]*)/?", EditNoteView.as_view()),
    path('modify_categories', AddCategoryView.as_view(),name="modify_categories"),
    path('delete_category', DeleteCategoryView.as_view(),name="delete_category"),
    path('edit_category', EditCategoryView.as_view(),name="edit_category"),
    re_path("edit_category/(?P<category_id>[^/]*)/?", EditCategoryView.as_view()),
    path('set_default_category', SetDefaultCategoryView.as_view(),name="set_default_category"),
    path('export', ExportNotesView.as_view(),name="export"),
    path('import', ImportNotesView.as_view(),name="import"),
    path('api/', include('listjj.apiurls')),
    path("admin/", admin.site.urls),
    path('register/', RegisterView.as_view(),name="register"),

]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]