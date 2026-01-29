from django.urls import path
from . import views  # Saare views (JWTLogin bhi) yahin se aayenge

urlpatterns = [
    # Static Pages (HTML)
    path("", views.home_page, name="home"),
    path("login/", views.login_page, name="login"),
    path("signup/", views.signup_page, name="signup"),
    path("logout/", views.logout_user, name="logout"),
    path('api/user-details/', views.get_user_details, name='user_details'),

    # JWT Token API (Ab ye main views se connect hai)
    path("api/jwt/login/", views.JWTLogin.as_view(), name="jwt-login"),

    # Chat API Endpoints
    path("api/ask/", views.ask_api),
    path("api/chats/", views.user_chats_api),
    path("api/chat/<str:chat_id>/", views.chat_messages_api),
    path("api/chat/<str:chat_id>/delete/", views.delete_chat_api),
]