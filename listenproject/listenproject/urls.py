from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dictation.urls')),  # 正确地引用 dictation 应用的路由
    path('accounts/', include('django.contrib.auth.urls')),  # ✅ 添加这行
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)