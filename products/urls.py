from django.urls import path
from .views import CategoryView, BookView, SkillNestedView, UpdateSkillView, AllSkillView, SkillView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('category/', CategoryView.as_view(), name="category"),
    path('skill/', SkillView.as_view(), name="skill"),
    path('list_skill/', SkillNestedView.as_view(), name='list_skill'),
    path('all_skill/<int:id>/', AllSkillView.as_view(), name='all_skill'),
    path('book/', BookView.as_view(), name='book'),
    path('skills/<int:id>/update/', UpdateSkillView.as_view(), name='skill-post-update'),
    #  path('upload_video/', VideoCreateView.as_view(), name='upload_video'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
urlpatterns += [
    path('api/media/<path:path>/', serve, {'document_root': settings.MEDIA_ROOT}),
]