from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.messages import get_messages
from .forms import RegistrationForm, LoginForm
from .models import CustomUser

def home_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.user_type == 'ADMIN':
            return redirect('admin_dashboard')
        elif request.user.user_type == 'STAFF':
            return redirect('staff_dashboard')
        else:
            return redirect('user_dashboard')
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['phone_number']
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user, backend='accounts.backends.PhoneBackend')
            messages.success(request, f'سلام {user.get_full_name()}، به اعتبارینو بازرگانی محمدی خوش آمدید!')
            return redirect('user_dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

    

def login_view(request):
    if request.user.is_authenticated:
        if request.user.user_type == 'ADMIN' or request.user.is_superuser:
            return redirect('admin_dashboard')
        elif request.user.user_type == 'STAFF':
            return redirect('staff_dashboard')
        else:
            return redirect('user_dashboard')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        phone_number = form.cleaned_data.get('phone_number')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=phone_number, password=password)
        
        if user is not None:
            login(request, user)
            if user.user_type == 'ADMIN' or user.is_superuser:
                return redirect('admin_dashboard')
            elif user.user_type == 'STAFF':
                return redirect('staff_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            form.add_error(None, "شماره تلفن یا رمز عبور اشتباه است.")
            
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    storage = get_messages(request)
    for message in storage:
        pass
    storage.used = True
    
    logout(request)
    messages.info(request, 'شما با موفقیت خارج شدید.')
    return redirect('home')

def terms_and_conditions_view(request):
    return render(request, 'terms.html')
