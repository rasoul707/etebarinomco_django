from django import forms
from accounts.models import CustomUser
from requests.models import CreditRequest
from django.core.exceptions import ValidationError
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget


class StaffLoginForm(forms.Form):
    username = forms.CharField(label="نام کاربری (ID)")
    password = forms.CharField(label="رمز عبور", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full mt-1 p-2 border bg-gray-50 dark:bg-gray-700 rounded-md focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'نام کاربری خود را وارد کنید'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full mt-1 p-2 border bg-gray-50 dark:bg-gray-700 rounded-md focus:ring-blue-500 focus:border-blue-500',
            'placeholder': '••••••••'
        })


class AdminUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'gender', 'user_type', 'is_active']
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'email': 'آدرس ایمیل',
            'phone_number': 'شماره تلفن',
            'gender': 'جنسیت',
            'user_type': 'نوع کاربر',
            'is_active': 'وضعیت فعالیت (فعال/غیرفعال)',
        }
        widgets = {
            'gender': forms.Select,
            'user_type': forms.Select,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full mt-1 p-2 border bg-gray-50 dark:bg-gray-700 rounded-md focus:ring-blue-500 focus:border-blue-500'
            })

class PostalTrackingForm(forms.ModelForm):
    class Meta:
        model = CreditRequest
        fields = ['postal_tracking_code']
        labels = {
            'postal_tracking_code': 'کد رهگیری پستی'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['postal_tracking_code'].widget.attrs.update({
            'class': 'w-full p-2 border bg-gray-50 dark:bg-gray-700 rounded-r-md text-left',
            'dir': 'ltr',
            'placeholder': 'کد ۲۴ رقمی پست...'
        })

# admin
class AdminPasswordChangeForm(forms.Form):
    new_password = forms.CharField(
        label="رمز عبور جدید",
        widget=forms.PasswordInput(attrs={'class': 'w-full mt-1 p-2 border bg-gray-50 dark:bg-gray-700 rounded-md'})
    )
    confirm_password = forms.CharField(
        label="تکرار رمز عبور جدید",
        widget=forms.PasswordInput(attrs={'class': 'w-full mt-1 p-2 border bg-gray-50 dark:bg-gray-700 rounded-md'})
    )

    def clean_confirm_password(self):
        cd = self.cleaned_data
        if cd.get("new_password") and cd.get("confirm_password") and cd["new_password"] != cd["confirm_password"]:
            raise ValidationError("رمزهای عبور با یکدیگر مطابقت ندارند.")
        return cd.get("confirm_password")

# admin
class AdminCreditRequestEditForm(forms.ModelForm):
    birth_date = JalaliDateField(label="تاریخ تولد", widget=AdminJalaliDateWidget)
    guarantor_birth_date = JalaliDateField(label="تاریخ تولد ضامن", required=False, widget=AdminJalaliDateWidget)

    class Meta:
        model = CreditRequest
        exclude = ['applicant']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    'class': 'w-full mt-1 p-2 border bg-gray-50 dark:bg-gray-700 rounded-md'
                })
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['rows'] = 2
        if 'postal_tracking_code' in self.fields:
            self.fields['postal_tracking_code'].widget.attrs.update({'placeholder': 'کد ۲۴ رقمی پست', 'dir': 'ltr'})


class StaffCreditRequestEditForm(forms.ModelForm):
    birth_date = JalaliDateField(label="تاریخ تولد", widget=AdminJalaliDateWidget)
    guarantor_birth_date = JalaliDateField(label="تاریخ تولد ضامن", required=False, widget=AdminJalaliDateWidget)

    class Meta:
        model = CreditRequest
        exclude = ['applicant']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, AdminJalaliDateWidget)):
                field.widget.attrs.update({'class': 'w-full mt-1 p-2 border bg-gray-50 dark:bg-gray-700 rounded-md'})
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['rows'] = 2


class AdminUserCreationForm(forms.ModelForm):
    password = forms.CharField(label="رمز عبور", widget=forms.PasswordInput)
    password2 = forms.CharField(label="تکرار رمز عبور", widget=forms.PasswordInput)

    gender = forms.ChoiceField(
        choices=CustomUser.GENDER_CHOICES,
        widget=forms.RadioSelect,
        label="جنسیت",
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'gender', 'user_type']
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'email': 'آدرس ایمیل',
            'phone_number': 'شماره تلفن (برای متقاضی) / نام کاربری (برای پرسنل)',
            'gender': 'جنسیت',
            'user_type': 'نوع کاربر (سطح دسترسی)',
        }
        widgets = {
            'gender': forms.RadioSelect,
            'user_type': forms.Select,
        }

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') and cd.get('password2') and cd['password'] != cd['password2']:
            raise forms.ValidationError('رمزهای عبور با یکدیگر مطابقت ندارند.')
        return cd.get('password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.update({'class': 'w-full mt-1 p-2 border bg-gray-50 dark:bg-gray-700 rounded-md focus:ring-blue-500 focus:border-blue-500'})
