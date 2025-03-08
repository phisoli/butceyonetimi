# butceyonetimi
# ParaSekreterim - Django Authentication Sistemi

Bu proje, modern bir finans yönetimi uygulaması için geliştirilmiş güvenli bir kimlik doğrulama (authentication) sistemidir.

## Proje Yapısı

```
auth_project/
├── accounts/                    # Kullanıcı yönetimi uygulaması
│   ├── migrations/             # Veritabanı migration dosyaları
│   ├── templates/accounts/     # Uygulama template'leri
│   │   ├── home.html          # Ana sayfa template'i
│   │   ├── login.html         # Giriş sayfası template'i
│   │   ├── register.html      # Kayıt sayfası template'i
│   │   ├── password_reset_request.html    # Şifre sıfırlama istek sayfası
│   │   └── password_reset_confirm.html    # Şifre sıfırlama onay sayfası
│   ├── models.py              # Veritabanı modelleri
│   ├── forms.py               # Form tanımlamaları
│   ├── views.py               # View fonksiyonları
│   └── apps.py                # Uygulama konfigürasyonu
├── auth_project/              # Proje ana dizini
│   ├── settings.py            # Proje ayarları
│   └── urls.py                # Ana URL yapılandırması
├── static/                    # Statik dosyalar
│   └── css/
│       └── style.css         # Özel CSS stilleri
├── templates/                 # Genel template'ler
│   └── base.html             # Ana template
└── manage.py                 # Django yönetim scripti
```

## Dosya İçerikleri ve Açıklamaları

### 1. accounts/models.py
```python
# CustomUser modeli (AbstractUser'dan miras alır)
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # Benzersiz email adresi
    is_email_verified = models.BooleanField(default=False)  # Email doğrulama durumu

# Şifre sıfırlama için token modeli
class PasswordResetToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Kullanıcı ilişkisi
    token = models.UUIDField(default=uuid.uuid4, editable=False)   # Benzersiz token
    created_at = models.DateTimeField(auto_now_add=True)           # Oluşturulma tarihi
    is_used = models.BooleanField(default=False)                   # Kullanım durumu
```

### 2. accounts/forms.py
```python
# Kullanıcı kayıt formu
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Zorunlu email alanı
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

# Giriş formu
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='E-posta veya Kullanıcı Adı')
    password = forms.CharField(label='Şifre', widget=forms.PasswordInput)

# Şifre sıfırlama istek formu
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label='E-posta')

# Yeni şifre belirleme formu
class SetNewPasswordForm(forms.Form):
    password1 = forms.CharField(label='Yeni Şifre', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Yeni Şifre (Tekrar)', widget=forms.PasswordInput)
```

### 3. accounts/views.py
```python
# Kayıt view'ı
@require_http_methods(["GET", "POST"])
def register_view(request):
    # POST isteği: Form gönderimi
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    # GET isteği: Boş form gösterimi
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# Giriş view'ı
def login_view(request):
    # Form doğrulama ve kullanıcı girişi
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# Ana sayfa view'ı
@login_required  # Giriş yapmış kullanıcı gerektirir
def home_view(request):
    return render(request, 'accounts/home.html')

# Şifre sıfırlama view'ları
def password_reset_request(request):
    # Şifre sıfırlama email'i gönderme
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            token = PasswordResetToken.objects.create(user=user)
            # Email gönderme işlemi...
    else:
        form = PasswordResetRequestForm()
    return render(request, 'accounts/password_reset_request.html', {'form': form})
```

### 4. auth_project/settings.py
```python
# Önemli ayarlar
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
    'widget_tweaks',  # Form görünümü için
    'accounts',       # Kullanıcı yönetimi uygulaması
]

# Kimlik doğrulama ayarları
AUTH_USER_MODEL = 'accounts.CustomUser'  # Özel kullanıcı modeli
LOGIN_REDIRECT_URL = 'home'             # Giriş sonrası yönlendirme
LOGOUT_REDIRECT_URL = 'login'           # Çıkış sonrası yönlendirme
LOGIN_URL = 'login'                     # Giriş URL'i

# Email ayarları (geliştirme ortamı için)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### 5. static/css/style.css
```css
/* Renk değişkenleri */
:root {
    --primary-color: #2ecc71;    /* Ana renk (yeşil) */
    --secondary-color: #27ae60;  /* İkincil renk */
    --accent-color: #3498db;     /* Vurgu rengi (mavi) */
    --danger-color: #e74c3c;     /* Tehlike rengi (kırmızı) */
    --text-color: #2c3e50;       /* Metin rengi */
}

/* Genel stil tanımlamaları */
body {
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #f6f8fa 0%, #e9ecef 100%);
}

/* Navbar stilleri */
.navbar {
    background: linear-gradient(to right, var(--primary-color), var(--accent-color)) !important;
}

/* Kart stilleri */
.card {
    border: none;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
}

/* Buton stilleri */
.btn-primary {
    background: var(--primary-color);
    border: none;
    border-radius: 30px;
}
```

### 6. templates/base.html
Ana template dosyası, tüm sayfaların temel yapısını içerir:
- Bootstrap ve Font Awesome entegrasyonu
- Responsive navbar
- Mesaj gösterimi sistemi
- İçerik bloğu

### 7. Template Dosyaları (accounts/templates/accounts/)
Her template dosyası (`login.html`, `register.html`, vb.):
- base.html'den miras alır
- Bootstrap grid sistemi kullanır
- Form görüntüleme ve doğrulama
- Hata mesajları gösterimi
- Responsive tasarım

## Güvenlik Özellikleri

1. CSRF koruması
2. Şifre hashleme
3. Session yönetimi
4. Login required decorator
5. Form doğrulama
6. Güvenli şifre sıfırlama

## Kullanılan Teknolojiler

- Django 4.x
- Bootstrap 5
- Font Awesome
- Django Widget Tweaks
- SQLite (Veritabanı)

## Kurulum ve Çalıştırma

1. Migrations oluşturma:
```bash
python manage.py makemigrations
```

2. Veritabanını güncelleme:
```bash
python manage.py migrate
```

3. Superuser oluşturma:
```bash
python manage.py createsuperuser
```

4. Sunucuyu başlatma:
```bash
python manage.py runserver
```
