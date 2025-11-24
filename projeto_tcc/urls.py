from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- URLs de Reset de Senha (Globais) ---
    path('reset_password/',
        auth_views.PasswordResetView.as_view(
            template_name="home/reset_senha/password_reset_form.html",
            email_template_name="home/reset_senha/password_reset_email.html",
            success_url=reverse_lazy('password_reset_done')
        ),
        name='password_reset'),

    path('reset_password/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name="home/reset_senha/password_reset_done.html"
        ),
        name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name="home/reset_senha/password_reset_confirm.html",
            success_url=reverse_lazy('password_reset_complete')
        ),
        name='password_reset_confirm'), 

    path('reset_password/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name="home/reset_senha/password_reset_complete.html"
        ),
        name='password_reset_complete'),

    path('', include('home.urls', namespace='home')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    

urlpatterns += staticfiles_urlpatterns()