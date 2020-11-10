from django.urls import path, include

from django.contrib import admin

admin.autodiscover()

import app.views

#for auth:
from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from django.conf.urls import include


urlpatterns = [
    path("", app.views.index, name="index"),
    path("delete_note", app.views.delete_note, name="delete_note"),
    path("delete_note_ajax", app.views.delete_note_ajax, name="delete_note_ajax"),
    path("addnote", app.views.addnote, name="addnote"),
    path("edit_note", app.views.edit_note_view, name="edit_note"),
    re_path("edit_note/(?P<note_id>[^/]*)/?", app.views.edit_note_view),
    path("modify_categories", app.views.add_category_view, name="modify_categories"),
    path("delete_category", app.views.delete_category, name="delete_category"),
    path("edit_category", app.views.edit_category_view, name="edit_category"),
    re_path("edit_category/(?P<category_id>[^/]*)/?", app.views.edit_category_view),
    path("set_default_category", app.views.set_default_category, name="set_default_category"),
    path("export", app.views.export_notes, name="export"),
    path("import", app.views.import_notes, name="import"),
    path('api/', include('listjj.apiurls')),
    path("admin/", admin.site.urls),
	path("register/", app.views.register, name="register"),

]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]