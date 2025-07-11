from django.db import models
from django.conf import settings

class CreditRequest(models.Model):
    REQUEST_TYPE_CHOICES = (
        ('loan_purchase', 'خرید امتیاز وام'),
        ('goods_loan', 'وام خرید کالا'),
        ('direct_credit', 'تخصیص اعتبار خرید کالا'),
    )
    STATUS_CHOICES = (
        ('step1_draft', 'مرحله ۱: پیش‌نویس اطلاعات فردی'),
        ('step1_submitted', 'مرحله ۱: ارسال شده برای بررسی'),
        ('step1_rejected', 'مرحله ۱: نیاز به اصلاح اطلاعات'),
        ('step2_draft', 'مرحله ۲: پیش‌نویس اطلاعات ضامن'),
        ('step2_submitted', 'مرحله ۲: ارسال شده برای بررسی'),
        ('step2_rejected', 'مرحله ۲: نیاز به اصلاح اطلاعات'),
        ('step3_draft', 'مرحله ۳: پیش‌نویس بارگذاری مدارک'),
        ('step3_submitted', 'مرحله ۳: ارسال شده برای بررسی'),
        ('step3_rejected', 'مرحله ۳: نیاز به اصلاح مدارک'),
        ('step4_draft', 'مرحله ۴: پیش‌نویس تایید قوانین'),
        ('final_submission', 'تایید نهایی، در انتظار بررسی کارشناس'),
        ('approved', 'تایید نهایی توسط کارشناسی'),
        ('rejected', 'رد شده'),
        ('completed', 'تکمیل شده (کد پستی ثبت شد)'),
    )
    
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="متقاضی")
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES, verbose_name="نوع درخواست", null=True)
    requested_amount = models.BigIntegerField(verbose_name="مبلغ درخواستی", null=True)


    payment_receipt = models.FileField(
        upload_to='payment_receipts/',
        verbose_name="فیش پرداخت",
        blank=True,
        null=True
    )
    

    validation_payment_receipt = models.FileField(
        upload_to='payment_receipts/',
        verbose_name="فیش پرداخت اعتبار سنجی",
        blank=True,
        null=True
    )

    
    subscription_payment_receipt = models.FileField(
        upload_to='payment_receipts/',
        verbose_name="فیش پرداخت حق اشتراک",
        blank=True,
        null=True
    )


    validation_document = models.FileField(
        upload_to='validation_document/',
        verbose_name="سند اعتبار سنجی",
        blank=True,
        null=True
    )


    full_name = models.CharField(max_length=100, verbose_name="نام و نام خانوادگی", blank=True, null=True)
    father_name = models.CharField(max_length=100, verbose_name="نام پدر", blank=False, null=True )
    national_id = models.CharField(max_length=10, verbose_name="کد ملی", blank=False, null=True)
    card_serial = models.CharField(max_length=20, verbose_name="سریال کارت ملی", blank=False, null=True)
    birth_date = models.DateField(verbose_name="تاریخ تولد", blank=False, null=True)
    birth_place_province = models.CharField(max_length=50, verbose_name="استان محل تولد", blank=False, null=True)
    birth_place_city = models.CharField(max_length=50, verbose_name="شهر محل تولد", blank=False, null=True)
    landline_number = models.CharField(max_length=15, verbose_name="شماره تلفن ثابت", blank=False, null=True)
    province = models.CharField(max_length=50, verbose_name="استان محل سکونت", blank=False, null=True)
    city = models.CharField(max_length=50, verbose_name="شهر محل سکونت", blank=False, null=True)
    area = models.CharField(max_length=100, verbose_name="منطقه", blank=False, null=True)
    address_line = models.TextField(verbose_name="خیابان و آدرس دقیق", blank=False, null=True)
    plaque = models.CharField(max_length=10, verbose_name="پلاک", blank=False, null=True)
    unit = models.CharField(max_length=10, verbose_name="واحد", blank=False, null=True)
    postal_code = models.CharField(max_length=10, verbose_name="کد پستی", blank=False, null=True)
    iban = models.CharField(max_length=26, verbose_name="شماره شبا (بدون IR)", blank=False, null=True)
    account_number = models.CharField(max_length=20, verbose_name="شماره حساب بانکی", blank=False, null=True)
    applicant_signature = models.ImageField(upload_to='signatures/', blank=True, null=True, verbose_name="امضای متقاضی")
    guarantor_signature = models.ImageField(upload_to='signatures/', blank=True, null=True, verbose_name="امضای ضامن")

    
    guarantor_full_name = models.CharField(max_length=100, verbose_name="نام و نام خانوادگی ضامن", blank=True, null=True)
    guarantor_national_id = models.CharField(max_length=10, verbose_name="کد ملی ضامن", blank=True, null=True)
    guarantor_card_serial = models.CharField(max_length=20, verbose_name="سریال کارت ملی جدید ضامن", blank=True, null=True)
    guarantor_birth_date = models.DateField(verbose_name="تاریخ تولد ضامن", blank=True, null=True)
    guarantor_phone_number = models.CharField(max_length=11, verbose_name="شماره تماس ضامن", blank=True, null=True)
    guarantor_address = models.TextField(verbose_name="آدرس محل سکونت ضامن", blank=True, null=True)
    guarantor_credit_score = models.IntegerField(verbose_name="رتبه اعتبارسنجی ضامن(به انگلیسی)", blank=True, null=True)
    guarantor_consent = models.BooleanField(default=False, verbose_name="پذیرش قوانین توسط ضامن")

    applicant_id_card_front = models.FileField(upload_to='documents/applicant/', blank=True, null=True, verbose_name="تصویر روی کارت ملی متقاضی")
    applicant_id_card_back = models.FileField(upload_to='documents/applicant/', blank=True, null=True, verbose_name="تصویر پشت کارت ملی متقاضی")
    applicant_birth_certificate = models.FileField(upload_to='documents/applicant/', blank=True, null=True, verbose_name="تصویر شناسنامه متقاضی")
    guarantor_id_card_front = models.FileField(upload_to='documents/guarantor/', blank=True, null=True, verbose_name="تصویر روی کارت ملی ضامن")
    guarantor_id_card_back = models.FileField(upload_to='documents/guarantor/', blank=True, null=True, verbose_name="تصویر پشت کارت ملی ضامن")
    guarantor_birth_certificate = models.FileField(upload_to='documents/guarantor/', blank=True, null=True, verbose_name="تصویر شناسنامه ضامن")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='step1_draft', verbose_name="وضعیت پرونده")
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="دلیل رد شدن مرحله")
    postal_tracking_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="کد رهگیری پستی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")

    def __str__(self):
        return f"درخواست آقای/خانم {self.full_name} - وضعیت: {self.get_status_display()}"




class Ticket(models.Model):
    STATUS_CHOICES = (
        ('open', 'باز'),
        ('closed', 'بسته شده'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets', verbose_name="کاربر")
    title = models.CharField(max_length=200, verbose_name="عنوان تیکت")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open', verbose_name="وضعیت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    def __str__(self):
        return f"تیکت {self.title} برای {self.user.username}"

class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages', verbose_name="تیکت")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="ارسال کننده")
    message = models.TextField(verbose_name="متن پیام")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")

    def __str__(self):
        return f"پیام از {self.user.username} در تیکت {self.ticket.id}"
