from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Django admin
    path('z-admin-z/', admin.site.urls),
    
    # User management
    path("accounts/", include("accounts_app.urls")),  
    path('accounts/', include('allauth.urls')),
    path('routs/', include("scheduler_app.urls")),
    path('', TemplateView.as_view(template_name = 'home.html'), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
