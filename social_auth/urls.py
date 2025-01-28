from django.urls import path
from social_auth import views

urlpatterns = [
    path('home/', views.HomeView.as_view()),
    path('google-auth/', views.GoogleAuthView.as_view()),
    path('google/callback/', views.GoogleCallbackView.as_view()),
    path("facebook-auth/", views.FacebookLoginView.as_view()),
    path("facebook/callback/", views.FacebookCallbackView.as_view()),
]
