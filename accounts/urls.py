from django.urls import path
from .views import RegisterView, LoginView, UserListDeleteView, UserView, ProfileView, GetProfileView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/', UserView.as_view(), name='users'),
    path('delete/<int:pk>/', UserListDeleteView.as_view(), name='delete_user'),
    path('profile/create/', ProfileView.as_view(), name='profile'),
    path('profile/all/', GetProfileView.as_view()),
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)