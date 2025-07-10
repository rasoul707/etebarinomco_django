import re
from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser

class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(label="آدرس ایمیل")
    password = forms.CharField(label="رمز عبور", widget=forms.PasswordInput)
    password2 = forms.CharField(label="تکرار رمز عبور", widget=forms.PasswordInput)
    gender = forms.ChoiceField(
        choices=CustomUser.GENDER_CHOICES, 
        widget=forms.RadioSelect, 
        label="جنسیت"
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'gender', 'email', 'phone_number']
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'phone_number': 'شماره تلفن همراه',
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[آ-ی\s]+$', first_name):
            raise ValidationError('نام فقط باید شامل حروف فارسی باشد.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[آ-ی\s]+$', last_name):
            raise ValidationError('نام خانوادگی فقط باید شامل حروف فارسی باشد.')
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError('این ایمیل قبلاً ثبت شده است.')
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not re.match(r'^09\d{9}$', phone):
            raise ValidationError('فرمت شماره تلفن صحیح نیست. مثال: 09123456789')
        if CustomUser.objects.filter(phone_number=phone).exists():
            raise ValidationError('این شماره تلفن قبلاً ثبت شده است.')
        return phone

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') and cd.get('password2') and cd['password'] != cd['password2']:
            raise forms.ValidationError('رمزهای عبور با یکدیگر مطابقت ندارند.')
        return cd.get('password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.RadioSelect):
                common_class = 'w-full mt-1 p-2 border bg-gray-50 rounded-md focus:ring-blue-500 focus:border-blue-500'
                if 'password' in field_name:
                    field.widget.attrs.update({'class': common_class + ' pr-4 pl-10 text-left', 'dir': 'ltr'})
                else:
                    field.widget.attrs.update({'class': common_class})
        
        self.fields['first_name'].widget.attrs.update({'placeholder': 'مثال: علی'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'مثال: رضایی'})
        self.fields['email'].widget.attrs.update({'placeholder': 'your@email.com', 'dir': 'ltr'})
        self.fields['phone_number'].widget.attrs.update({'placeholder': '09123456789', 'dir': 'ltr'})

class LoginForm(forms.Form):
    phone_number = forms.CharField(label="شماره تلفن همراه")
    password = forms.CharField(label="رمز عبور", widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone_number'].widget.attrs.update({'class': 'w-full mt-1 p-2 border bg-gray-50 rounded-md focus:ring-blue-500 focus:border-blue-500 text-left', 'dir': 'ltr', 'placeholder': '09123456789'})
        self.fields['password'].widget.attrs.update({'class': 'w-full mt-1 p-2 border bg-gray-50 rounded-md focus:ring-blue-500 focus:border-blue-500 pr-4 pl-10 text-left', 'dir': 'ltr'})
