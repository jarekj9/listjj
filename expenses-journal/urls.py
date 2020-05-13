from django.urls import path, include

from django.contrib import admin

admin.autodiscover()

import app.views

#for auth:
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf.urls import include


urlpatterns = [
    path("", app.views.index, name="index"),
    path("deletenote", app.views.deletenote, name="deletenote"),
    path("addnote", app.views.addnote, name="addnote"),
    path("modify_categories", app.views.add_category, name="modify_categories"),
    path("export", app.views.export_view, name="export"),
    path("import", app.views.import_view, name="import"),
    path("delete_category", app.views.delete_category, name="delete_category"),
    path("admin/", admin.site.urls),
	path("register/", app.views.register, name="register"),
    path("accounts/logout/", app.views.register, name="register"),
]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]