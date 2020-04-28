from django.urls import path, include

from django.contrib import admin

admin.autodiscover()

import app.views

#for auth:
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf.urls import include





# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("", app.views.index, name="index"),
    path("db/", app.views.db, name="db"),
    path("admin/", admin.site.urls),

	path("register/", ap.views.register, name="register"),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'),name='logout'),
]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]