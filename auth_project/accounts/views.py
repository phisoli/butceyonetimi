from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    PasswordResetRequestForm,
    SetNewPasswordForm
)
from .models import PasswordResetToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import uuid

User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Kayıt başarılı! Hoş geldiniz.')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Başarıyla giriş yaptınız!')
                return redirect('home')
            else:
                messages.error(request, 'Geçersiz kullanıcı adı veya şifre!')
        else:
            messages.error(request, 'Lütfen geçerli bilgiler girin!')
            print(form.errors)  # Hataları konsola yazdır
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('login')

@login_required
def home_view(request):
    return render(request, 'accounts/home.html')

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = PasswordResetToken.objects.create(user=user)
                
                reset_url = f"{request.scheme}://{request.get_host()}/reset-password/{token.token}"
                send_mail(
                    'Şifre Sıfırlama',
                    f'Şifrenizi sıfırlamak için aşağıdaki linke tıklayın:\n\n{reset_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                messages.success(request, 'Şifre sıfırlama bağlantısı e-posta adresinize gönderildi.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'Bu e-posta adresiyle kayıtlı bir kullanıcı bulunamadı.')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'accounts/password_reset_request.html', {'form': form})

def password_reset_confirm(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Geçersiz veya kullanılmış token.')
        return redirect('login')

    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user = reset_token.user
            user.set_password(form.cleaned_data['password1'])
            user.save()
            reset_token.is_used = True
            reset_token.save()
            messages.success(request, 'Şifreniz başarıyla değiştirildi. Şimdi giriş yapabilirsiniz.')
            return redirect('login')
    else:
        form = SetNewPasswordForm()
    
    return render(request, 'accounts/password_reset_confirm.html', {'form': form})


