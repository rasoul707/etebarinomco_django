from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    CreditRequestStep1Form, 
    CreditRequestStep2Form, 
    CreditRequestStep3Form, 
    CreditRequestStep4Form,
    TicketCreationForm,
    TicketReplyForm
)
from .models import CreditRequest, Ticket, TicketMessage
import base64
from django.core.files.base import ContentFile

@login_required
def user_dashboard_view(request):
    credit_request = CreditRequest.objects.filter(applicant=request.user).first()
    
    context = {
        'credit_request': credit_request,
        'current_step': 0,
        'is_rejected': False,
        'is_submitted': False,
        'next_step_url_name': None,
    }

    if credit_request:
        status = credit_request.status

        step_map = {
            1: ['step1_draft', 'step1_submitted', 'step1_rejected'],
            2: ['step2_draft', 'step2_submitted', 'step2_rejected'],
            3: ['step3_draft', 'step3_submitted', 'step3_rejected'],
            4: ['step4_draft'],
            5: ['final_submission', 'approved', 'completed', 'rejected'],
        }

        for step, statuses in step_map.items():
            if status in statuses:
                context['current_step'] = step
                break

        context['is_rejected'] = 'rejected' in status
        context['is_submitted'] = 'submitted' in status

        next_step_url_map = {
            'step1_draft': 'create_request_step1',
            'step1_rejected': 'create_request_step1',
            'step2_draft': 'create_request_step2',
            'step2_rejected': 'create_request_step2',
            'step3_draft': 'create_request_step3',
            'step3_rejected': 'create_request_step3',
            'step4_draft': 'create_request_step4',
        }

        context['next_step_url_name'] = next_step_url_map.get(status)

    return render(request, 'requests/dashboard.html', context)

# Step 1
@login_required
def create_request_step1(request):
    instance = CreditRequest.objects.filter(applicant=request.user).first()
    if request.method == 'POST':
        form = CreditRequestStep1Form(request.POST, instance=instance)
        if form.is_valid():
            credit_request = form.save(commit=False)
            credit_request.applicant = request.user
            credit_request.status = 'step1_submitted'
            credit_request.save()
            messages.success(request, 'مرحله اول با موفقیت ثبت و برای بررسی ارسال شد.')
            return redirect('request_signature') 
    else:
        form = CreditRequestStep1Form(instance=instance)
    return render(request, 'requests/step1_form.html', {'form': form})

# step 2
@login_required
def create_request_step2(request):
    instance = get_object_or_404(CreditRequest, applicant=request.user)
    if request.method == 'POST':
        form = CreditRequestStep2Form(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'اطلاعات ضامن با موفقیت ثبت شد. لطفاً امضای ضامن را وارد کنید.')
            return redirect('request_guarantor_signature') 
    else:
        form = CreditRequestStep2Form(instance=instance)
    return render(request, 'requests/step2_form.html', {'form': form})


# step 3
@login_required
def create_request_step3(request):
    instance = get_object_or_404(CreditRequest, applicant=request.user)
    if request.method == 'POST':
        form = CreditRequestStep3Form(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            credit_request = form.save(commit=False)
            credit_request.status = 'step3_submitted'
            credit_request.save()
            messages.success(request, 'مرحله سوم با موفقیت ثبت و برای بررسی ارسال شد.')
            return redirect('user_dashboard')
    else:
        form = CreditRequestStep3Form(instance=instance)
    return render(request, 'requests/step3_form.html', {'form': form})

# step 4
@login_required
def create_request_step4(request):
    instance = get_object_or_404(CreditRequest, applicant=request.user)
    if request.method == 'POST':
        form = CreditRequestStep4Form(request.POST)
        if form.is_valid():
            instance.status = 'step4_draft'
            instance.save()
            return redirect('subscription_payment')
    else:
        form = CreditRequestStep4Form()
    return render(request, 'requests/step4_form.html', {'form': form})

# ticket list
@login_required
def ticket_list_view(request):
    tickets = Ticket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'requests/ticket_list.html', {'tickets': tickets})

# ticket create
@login_required
def ticket_create_view(request):
    if request.method == 'POST':
        form = TicketCreationForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            TicketMessage.objects.create(
                ticket=ticket,
                user=request.user,
                message=form.cleaned_data['message']
            )
            messages.success(request, 'تیکت شما با موفقیت ایجاد شد.')
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketCreationForm()
    return render(request, 'requests/ticket_create.html', {'form': form})


# ticket detail and replay
@login_required
def ticket_detail_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    if request.method == 'POST':
        form = TicketReplyForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = ticket
            message.user = request.user
            message.save()
            messages.success(request, 'پاسخ شما با موفقیت ثبت شد.')
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketReplyForm()
    return render(request, 'requests/ticket_detail.html', {'ticket': ticket, 'form': form})

@login_required
def request_start_view(request):
    if CreditRequest.objects.filter(applicant=request.user).exists():
        return redirect('user_dashboard')

    if request.method == 'POST':
        payment_receipt_file = request.FILES.get('payment_receipt')

        if not payment_receipt_file:
            return render(request, 'requests/request_start.html', {'error': 'لطفاً فیش واریزی را ارسال کنید.'})

        
        CreditRequest.objects.create(
            applicant=request.user,
            status='step1_draft',
            payment_receipt=payment_receipt_file,
        )
        
        return redirect('request_initial')

    return render(request, 'requests/request_start.html')



@login_required
def request_initial_view(request):
    credit_request = get_object_or_404(CreditRequest, applicant=request.user)

    if request.method == 'POST':
        req_type = request.POST.get('request_type')
        amount_str = ''.join(filter(str.isdigit, request.POST.get('amount', '0')))

        if not req_type:
            return render(request, 'requests/request_start.html', {'error': 'لطفاً نوع درخواست را انتخاب کنید.'})
        
        if not amount_str:
            return render(request, 'requests/request_start.html', {'error': 'لطفاً مبلغ مورد نظر را وارد کنید.'})

        amount = int(amount_str)

        if not 50000000 <= amount <= 2000000000:
            return render(request, 'requests/request_start.html', {
                'error': 'مبلغ درخواستی باید بین ۵۰ میلیون تا ۲ میلیارد تومان باشد.'
            })

        credit_request.request_type = req_type
        credit_request.requested_amount = amount
        credit_request.status = 'step1_draft'
        credit_request.save()
        
        
        return redirect('create_request_step1')

    return render(request, 'requests/request_initial.html')





@login_required
def signature_view(request):
    credit_request = get_object_or_404(CreditRequest, applicant=request.user)

    if request.method == 'POST':
        signature_data_url = request.POST.get('signature_data')
        if signature_data_url:
            format, imgstr = signature_data_url.split(';base64,') 
            ext = format.split('/')[-1] 
            data = ContentFile(base64.b64decode(imgstr), name=f'signature_{request.user.id}.{ext}')

            credit_request.applicant_signature = data
            credit_request.status = 'step1_draft'
            credit_request.save()
            
            return redirect('validation_payment')
        else:
            messages.error(request, 'لطفاً قبل از ادامه، امضای خود را ثبت کنید.')

    return render(request, 'requests/signature_pad.html')




@login_required
def validation_payment_view(request):
    credit_request = get_object_or_404(CreditRequest, applicant=request.user)

    if request.method == 'POST':
        payment_receipt_file = request.FILES.get('payment_receipt')

        if not payment_receipt_file:
            return render(request, 'requests/validation_payment.html', {'error': 'لطفاً فیش واریزی را ارسال کنید.'})
        
        credit_request.validation_payment_receipt=payment_receipt_file
        credit_request.status = 'step1_submitted'
        credit_request.save()
        
        return redirect('user_dashboard')

    return render(request, 'requests/validation_payment.html')




@login_required
def subscription_payment_view(request):
    credit_request = get_object_or_404(CreditRequest, applicant=request.user)

    if request.method == 'POST':
        payment_receipt_file = request.FILES.get('payment_receipt')

        if not payment_receipt_file:
            return render(request, 'requests/subscription_payment.html', {'error': 'لطفاً فیش واریزی را ارسال کنید.'})
        
        credit_request.subscription_payment_receipt=payment_receipt_file
        credit_request.status = 'final_submission'
        credit_request.save()


        messages.success(request, 'درخواست شما با موفقیت نهایی شد و برای بررسی ارسال گردید.')
        
        return redirect('user_dashboard')

    return render(request, 'requests/subscription_payment.html')




@login_required
def guarantor_signature_view(request):
    credit_request = get_object_or_404(CreditRequest, applicant=request.user)

    if request.method == 'POST':
        signature_data_url = request.POST.get('signature_data')
        if signature_data_url:
            format, imgstr = signature_data_url.split(';base64,') 
            ext = format.split('/')[-1] 
            data = ContentFile(base64.b64decode(imgstr), name=f'guarantor_signature_{request.user.id}.{ext}')

            credit_request.guarantor_signature = data
            credit_request.status = 'step2_submitted'
            credit_request.save()
            
            messages.success(request, 'امضای ضامن با موفقیت ثبت و درخواست شما برای بررسی ارسال شد.')
            return redirect('user_dashboard')
        else:
            messages.error(request, 'لطفاً قبل از ادامه، امضای ضامن را ثبت کنید.')

    return render(request, 'requests/guarantor_signature_pad.html')