from django.contrib import admin
from django.urls import path
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', accounts_views.register_view, name='register'),
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('password-reset/', accounts_views.password_reset_request, name='password_reset_request'),
    path('reset-password/<uuid:token>/', accounts_views.password_reset_confirm, name='password_reset_confirm'),
]
