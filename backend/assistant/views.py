from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import json

# JWT & DRF Specific Imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

# AI Engine Import (Strict gpt-4o-mini function)
# Note: Agar ai-engine.py file 'assistant' folder ke bahar hai toh '.ai_engine' use karein
try:
    from .ai_engine import ask_ai 
except ImportError:
    from assistant.ai_engine import ask_ai

from assistant.mongo import (
    create_new_chat,
    add_message,
    get_user_chats,
    get_chat_messages,
    delete_chat,
    delete_all_user_chats,
    get_message_count,       
    increment_message_count  
)

# =====================================================
# JWT AUTHENTICATION VIEW (API)
# =====================================================

class JWTLogin(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password required"}, status=400)

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if not user:
            return Response({"error": "Invalid credentials"}, status=401)

        # Django session start karo taaki home_page redirect loop na ho
        login(request, user) 

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "email": user.email,
            "username": user.username
        })

# =====================================================
# PAGE VIEWS (HTML)
# =====================================================

@login_required(login_url='login')
def home_page(request):
    return render(request, "assistant/home.html")

def login_page(request):
    if request.user.is_authenticated:
        logout(request)
        return render(request, "assistant/login.html", {"error": "Previous session closed. Login again to continue."})
    return render(request, "assistant/login.html")

def signup_page(request):
    if request.user.is_authenticated:
        logout(request)
        return render(request, "assistant/signup.html", {"error": "Session cleared. You can now create a new account."})

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        if User.objects.filter(username=email).exists():
            return render(request, "assistant/signup.html", {"error": "User already exists"})

        User.objects.create_user(username=email, email=email, password=password)
        return redirect('login') 

    return render(request, "assistant/signup.html")

def logout_user(request):
    logout(request)
    return redirect('login')

# =====================================================
# CHAT APIs - JWT PROTECTED
# =====================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_api(request):
    """
    AI Memory + Admin Access + Message Limit Logic + Strict gpt-4o-mini
    """
    try:
        data = request.data
        message = data.get("message", "").strip()
        chat_id = data.get("chat_id")
        user_id = request.user.id
        user_email = request.user.email

        # 🛡️ Admin Bypass + Limit check
        admin_email = "tusharsharma0991@gmail.com"
        
        if user_email != admin_email:
            current_count = get_message_count(user_id)
            if current_count >= 10:
                return Response({
                    "reply": "Bhai, aapki daily limit (10 messages) poori ho chuki hai. Admin access se try karein!",
                    "error": "LIMIT_REACHED"
                }, status=403) 

        if not message:
            return Response({"error": "Message required"}, status=400)

        if not chat_id:
            chat_id = create_new_chat(user_id, message)

        # Context build-up (Last 5 messages for memory)
        history = get_chat_messages(user_id, chat_id)
        context = ""
        for m in history[-5:]: 
            context += f"{m['role']}: {m['content']}\n"
        
        full_prompt = f"{context}user: {message}"
        
        # Calling your new strict ai-engine function
        reply = ask_ai(full_prompt)

        # Save messages to MongoDB
        add_message(user_id, chat_id, "user", message)
        add_message(user_id, chat_id, "assistant", reply)

        # 📈 Increment message count
        increment_message_count(user_id)

        return Response({
            "reply": reply,
            "chat_id": chat_id
        })

    except Exception as e:
        print(f"CRITICAL ERROR in ask_api: {e}")
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    return Response({
        "username": request.user.username,
        "email": request.user.email
    })

@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_chats_api(request):
    user_id = request.user.id
    if request.method == 'DELETE':
        delete_all_user_chats(user_id)
        return Response({"success": True, "message": "All history deleted"})
    chats = get_user_chats(user_id)
    return Response({"chats": chats})

@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def chat_messages_api(request, chat_id):
    if request.method == 'DELETE':
        delete_chat(request.user.id, chat_id)
        return Response({"success": True})
    messages = get_chat_messages(request.user.id, chat_id)
    return Response({"messages": messages})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_chat_api(request, chat_id):
    delete_chat(request.user.id, chat_id)
    return Response({"success": True})