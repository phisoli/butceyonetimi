from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Bu e-posta adresi zaten kullanılıyor.')
        return email

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='E-posta veya Kullanıcı Adı')
    password = forms.CharField(label='Şifre', widget=forms.PasswordInput)

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label='E-posta')

class SetNewPasswordForm(forms.Form):
    password1 = forms.CharField(label='Yeni Şifre', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Yeni Şifre (Tekrar)', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Şifreler eşleşmiyor.')
