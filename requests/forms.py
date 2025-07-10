import re
import jdatetime
from django import forms
from django.core.exceptions import ValidationError
from .models import CreditRequest, Ticket, TicketMessage
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget


def validate_iranian_national_code(code):
    if not isinstance(code, str) or not code.isdigit() or len(code) != 10:
        raise ValidationError('کد ملی باید یک عدد ۱۰ رقمی باشد.')

    if len(set(code)) == 1:
        raise ValidationError('کد ملی وارد شده معتبر نمی‌باشد.')

    check_sum = sum(int(code[i]) * (10 - i) for i in range(9))
    control_digit = int(code[9])
    remainder = check_sum % 11

    is_valid = (remainder < 2 and control_digit == remainder) or \
               (remainder >= 2 and control_digit == 11 - remainder)

    if not is_valid:
        raise ValidationError('کد ملی وارد شده معتبر نمی‌باشد.')


class CreditRequestStep1Form(forms.ModelForm):
    birth_date = JalaliDateField(
        label="تاریخ تولد", 
        widget=AdminJalaliDateWidget
    )

    class Meta:
        model = CreditRequest
        fields = [
            'full_name', 'father_name', 'national_id', 'card_serial', 'birth_date', 
            'birth_place_province', 'birth_place_city', 'landline_number',
            'province', 'city', 'area', 'address_line', 'plaque', 'unit', 'postal_code',
            'iban', 'account_number'
        ]
        widgets = {
            'address_line': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full mt-1 p-2 border bg-gray-50 dark:bg-gray-700 rounded-md focus:ring-blue-500 focus:border-blue-500'
            })


class CreditRequestStep2Form(forms.ModelForm):
    guarantor_birth_date = forms.CharField(
        required=True,
        label="تاریخ تولد ضامن",
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'class': 'w-full mt-1 p-2 border bg-gray-50 dark:bg-gray-700 rounded-md focus:ring-blue-500 focus:border-blue-500 pwt-datepicker',
            'placeholder': 'مثال: 1370/01/01'
        })
    )

    guarantor_consent = forms.BooleanField(
        required=True,
        label="اینجانب صحت اطلاعات فوق را تایید کرده و قوانین مربوط به ضمانت را می‌پذیرم."
    )

    class Meta:
        model = CreditRequest
        fields = [
            'guarantor_full_name', 'guarantor_national_id', 'guarantor_card_serial',
            'guarantor_birth_date', 'guarantor_phone_number', 'guarantor_address',
            'guarantor_credit_score', 'guarantor_consent'
        ]
        widgets = {
            'guarantor_address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'w-full mt-1 p-2 border bg-gray-50 dark:bg-gray-700 rounded-md focus:ring-blue-500 focus:border-blue-500')

    def clean_guarantor_national_id(self):
        national_id = self.cleaned_data.get('guarantor_national_id')
        validate_iranian_national_code(national_id)
        return national_id

    def clean_guarantor_birth_date(self):
        raw_date = self.cleaned_data.get('guarantor_birth_date')
        if not raw_date:
            raise forms.ValidationError("تاریخ تولد الزامی است.")
        try:
            raw_date = raw_date.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789'))
            year, month, day = map(int, raw_date.split('/'))
            j_date = jdatetime.date(year, month, day)
            return j_date.togregorian()
        except Exception:
            raise forms.ValidationError("فرمت تاریخ نامعتبر است. از فرمت YYYY/MM/DD استفاده کنید.")

    def clean(self):
        cleaned_data = super().clean()
        g_nid = cleaned_data.get("guarantor_national_id")
        applicant_nid = self.instance.national_id
        if g_nid and applicant_nid and g_nid == applicant_nid:
            self.add_error('guarantor_national_id', 'کد ملی ضامن نمی‌تواند با کد ملی متقاضی یکسان باشد.')
        return cleaned_data



class CreditRequestStep3Form(forms.ModelForm):
    class Meta:
        model = CreditRequest
        fields = [
            'applicant_id_card_front', 'applicant_id_card_back', 'applicant_birth_certificate',
            'guarantor_id_card_front', 'guarantor_id_card_back', 'guarantor_birth_certificate',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            })



class CreditRequestStep4Form(forms.Form):
    terms_accepted = forms.BooleanField(
        label="ضمن مطالعه دقیق شرایط و قوانین، تمام موارد فوق را می‌پذیرم.",
        required=True
    )


class TicketCreationForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea, label="متن پیام")

    class Meta:
        model = Ticket
        fields = ['title', 'message']
        labels = {
            'title': 'عنوان تیکت',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'class': 'w-full mt-1 p-2 border bg-gray-50 dark:bg-gray-700 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'موضوع تیکت خود را وارد کنید'
        })
        self.fields['message'].widget.attrs.update({
            'class': 'w-full mt-1 p-2 border bg-gray-50 dark:bg-gray-700 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500',
            'rows': 5,
            'placeholder': 'لطفاً مشکل یا سوال خود را با جزئیات کامل شرح دهید...'
        })


class TicketReplyForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ['message']
        labels = {
            'message': "پاسخ شما:"
        }
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].widget.attrs.update({
            'class': 'w-full mt-1 p-2 border bg-gray-50 dark:bg-gray-700 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'پاسخ خود را اینجا بنویسید...'
        })
