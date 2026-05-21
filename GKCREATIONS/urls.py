from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# Serve media files in development (WhiteNoise handles static; media needs this)
# In production on Render, media files need cloud storage (e.g. Cloudinary/S3)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production, still serve media via Django (works on Render free tier)
    # Note: Render's filesystem is ephemeral — uploaded files reset on redeploy
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
