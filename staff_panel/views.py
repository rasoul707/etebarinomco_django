from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .forms import StaffLoginForm
from .decorators import staff_required, admin_required
from accounts.models import CustomUser
from requests.models import CreditRequest, Ticket, TicketMessage
from requests.forms import TicketReplyForm
from .decorators import admin_required
from .forms import AdminUserEditForm, AdminPasswordChangeForm
from requests.models import CreditRequest
from .forms import AdminUserEditForm, AdminCreditRequestEditForm
from .forms import PostalTrackingForm
from .forms import AdminUserCreationForm
from .forms import AdminPasswordChangeForm

def staff_login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.user_type == 'ADMIN':
            return redirect('admin_dashboard')
        elif request.user.user_type == 'STAFF':
            return redirect('staff_dashboard')

    form = StaffLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser or user.user_type == 'ADMIN':
                login(request, user)
                return redirect('admin_dashboard')
            elif user.user_type == 'STAFF':
                login(request, user)
                return redirect('staff_dashboard')
            else:
                form.add_error(None, "شما دسترسی لازم برای ورود به این پنل را ندارید.")
        else:
            form.add_error(None, "نام کاربری یا رمز عبور اشتباه است.")

    return render(request, 'staff_panel/login.html', {'form': form})


@login_required
@staff_required
def staff_dashboard_view(request):
    requests_to_review = CreditRequest.objects.filter(status__icontains='submitted').order_by('-updated_at')
    context = {'requests': requests_to_review}
    return render(request, 'staff_panel/dashboard.html', context)


@login_required
@staff_required
def request_detail_view(request, request_id):
    from .forms import StaffCreditRequestEditForm

    credit_request = get_object_or_404(CreditRequest, id=request_id)

    form = StaffCreditRequestEditForm(instance=credit_request)

    if request.method == 'POST':
        action = request.POST.get('action')
        current_status = credit_request.status

        if action == 'approve':
            status_progression = {
                'step1_submitted': 'step2_draft',
                'step2_submitted': 'step3_draft',
                'step3_submitted': 'step4_draft',
                'final_submission': 'approved',
            }

            if current_status in status_progression:
                if current_status == 'final_submission' and not (request.user.is_superuser or request.user.user_type == 'ADMIN'):
                    messages.error(request, "شما دسترسی لازم برای تایید نهایی این درخواست را ندارید.")
                    return redirect('staff_request_detail', request_id=credit_request.id)

                credit_request.status = status_progression[current_status]
                credit_request.rejection_reason = ""
                credit_request.save()
                messages.success(request, "مرحله با موفقیت تایید شد.")
            return redirect('staff_dashboard')

        elif action == 'reject':
            reason = request.POST.get('rejection_reason', 'نقص در اطلاعات یا مدارک.')
            rejection_step = request.POST.get('rejection_step')
            rejection_map = {
                '1': 'step1_rejected',
                '2': 'step2_rejected',
                '3': 'step3_rejected',
                'final': 'rejected'
            }
            if rejection_step in rejection_map:
                credit_request.status = rejection_map[rejection_step]
                credit_request.rejection_reason = reason
                credit_request.save()
                messages.error(request, "درخواست کاربر رد شد و برای اصلاح ارجاع داده شد.")
            return redirect('staff_dashboard')

        elif action == 'submit_tracking' and credit_request.status == 'approved':
            tracking_code = request.POST.get('postal_tracking_code', '').strip()
            if tracking_code:
                credit_request.postal_tracking_code = tracking_code
                credit_request.status = 'completed'
                credit_request.save()
                messages.success(request, "کد رهگیری پستی با موفقیت ثبت و وضعیت درخواست تکمیل شد.")
            else:
                messages.error(request, "لطفاً کد رهگیری را وارد نمایید.")
            return redirect('staff_dashboard')

        else:
            form = StaffCreditRequestEditForm(request.POST, request.FILES, instance=credit_request)
            if form.is_valid():
                form.save()
                messages.success(request, "اطلاعات درخواست با موفقیت به‌روزرسانی شد.")
                return redirect('staff_request_detail', request_id=credit_request.id)

    status = credit_request.status
    show_guarantor = credit_request.guarantor_full_name is not None
    show_documents = credit_request.applicant_id_card_front is not None
    is_step1_active = status.startswith('step1_')
    is_step2_active = status.startswith('step2_')
    is_step3_active = status.startswith('step3_')

    context = {
        'credit_request': credit_request,
        'form': form,
        'show_guarantor': show_guarantor,
        'show_documents': show_documents,
        'is_step1_active': is_step1_active,
        'is_step2_active': is_step2_active,
        'is_step3_active': is_step3_active,
    }
    return render(request, 'staff_panel/request_detail.html', context)


@login_required
@staff_required
def print_customer_info_view(request, user_id):
    customer = get_object_or_404(CustomUser, id=user_id, user_type='APPLICANT')
    credit_request = CreditRequest.objects.filter(applicant=customer).first()

    context = {
        'customer': customer,
        'credit_request': credit_request,
    }
    return render(request, 'staff_panel/print_customer_info.html', context)


@login_required
@staff_required
def customer_list_view(request):
    query = request.GET.get('q', '').strip()
    customers_queryset = CustomUser.objects.filter(user_type='APPLICANT')

    if query:
        user_info_q = (
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query)
        )
        matching_request_users_ids = CreditRequest.objects.filter(
            national_id__icontains=query
        ).values_list('applicant_id', flat=True)

        national_id_q = Q(id__in=matching_request_users_ids)
        customers = customers_queryset.filter(user_info_q | national_id_q).distinct()
    else:
        customers = customers_queryset.order_by('-date_joined')

    context = {
        'customers': customers,
        'search_query': query,
    }
    return render(request, 'staff_panel/customer_list.html', context)


@login_required
@staff_required
def staff_ticket_list_view(request):
    tickets = Ticket.objects.all().order_by('-created_at')
    context = {
        'tickets': tickets,
    }
    return render(request, 'staff_panel/ticket_list.html', context)


@login_required
@staff_required
def staff_ticket_detail_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        if 'toggle_status' in request.POST:
            ticket.status = 'closed' if ticket.status == 'open' else 'open'
            ticket.save()
            messages.success(request, f"وضعیت تیکت به '{ticket.get_status_display()}' تغییر یافت.")
            return redirect('staff_ticket_detail', ticket_id=ticket.id)

        form = TicketReplyForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = ticket
            message.user = request.user
            message.save()
            messages.success(request, "پاسخ شما با موفقیت ثبت شد.")
            return redirect('staff_ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketReplyForm()

    context = {
        'ticket': ticket,
        'form': form,
    }
    return render(request, 'staff_panel/ticket_detail.html', context)


@login_required
@admin_required 
def admin_dashboard_view(request):
    total_users = CustomUser.objects.filter(user_type='APPLICANT').count()
    total_requests = CreditRequest.objects.count()
    approved_requests = CreditRequest.objects.filter(status='APPROVED').count()
    rejected_requests = CreditRequest.objects.filter(status='REJECTED').count()

    context = {
        'total_users': total_users,
        'total_requests': total_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
    }
    return render(request, 'staff_panel/admin_dashboard.html', context)

@login_required
@admin_required
def admin_user_list_view(request):
    users = CustomUser.objects.all().order_by('-date_joined')

    context = {
        'users': users,
    }
    return render(request, 'staff_panel/user_list.html', context)

@login_required
@admin_required
def admin_user_edit_choice_view(request, user_id):
    user_to_edit = get_object_or_404(CustomUser, id=user_id)
    context = {
        'user_to_edit': user_to_edit
    }
    return render(request, 'staff_panel/user_edit_choice.html', context)

@login_required
@admin_required
def admin_user_edit_simple_view(request, user_id):
    user_to_edit = get_object_or_404(CustomUser, id=user_id)
    credit_request = CreditRequest.objects.filter(applicant=user_to_edit).first()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete_user':
            user_to_edit.delete()
            messages.success(request, f'کاربر {user_to_edit.username} با موفقیت حذف شد.')
            return redirect('admin_user_list')

        user_form = AdminUserEditForm(request.POST if action == 'update_user_info' else None, instance=user_to_edit)
        password_form = AdminPasswordChangeForm(request.POST if action == 'change_password' else None)
        tracking_form = PostalTrackingForm(request.POST if action == 'update_postal_tracking' else None, instance=credit_request) if credit_request else None

        if action == 'update_user_info' and user_form.is_valid():
            user_form.save()
            messages.success(request, 'اطلاعات حساب کاربری با موفقیت به‌روزرسانی شد.')
            return redirect('admin_user_edit_simple', user_id=user_id)

        if action == 'change_password' and password_form.is_valid():
            user_to_edit.set_password(password_form.cleaned_data['new_password'])
            user_to_edit.save()
            messages.success(request, 'رمز عبور کاربر با موفقیت تغییر یافت.')
            return redirect('admin_user_edit_simple', user_id=user_id)

        if action == 'update_postal_tracking' and tracking_form and tracking_form.is_valid():
            tracking_form.save()
            messages.success(request, 'کد رهگیری پستی با موفقیت ثبت/ویرایش شد.')
            return redirect('admin_user_edit_simple', user_id=user_id)


    else:
        user_form = AdminUserEditForm(instance=user_to_edit)
        password_form = AdminPasswordChangeForm()
        tracking_form = PostalTrackingForm(instance=credit_request) if credit_request else None

    context = {
        'user_to_edit': user_to_edit,
        'credit_request': credit_request,
        'user_form': user_form,
        'password_form': password_form,
        'tracking_form': tracking_form,
    }
    return render(request, 'staff_panel/user_edit_simple.html', context)


@login_required
@admin_required
def admin_user_edit_view(request, user_id):
    user_to_edit = get_object_or_404(CustomUser, id=user_id)
    credit_request = CreditRequest.objects.filter(applicant=user_to_edit).first()

    user_form = AdminUserEditForm(instance=user_to_edit)
    password_form = AdminPasswordChangeForm()
    tracking_form = PostalTrackingForm(instance=credit_request) if credit_request else None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_user_info':
            user_form = AdminUserEditForm(request.POST, instance=user_to_edit)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'اطلاعات حساب کاربری با موفقیت به‌روزرسانی شد.')
                return redirect('admin_user_edit', user_id=user_id)

        elif action == 'change_password':
            password_form = AdminPasswordChangeForm(request.POST)
            if password_form.is_valid():
                user_to_edit.set_password(password_form.cleaned_data['new_password'])
                user_to_edit.save()
                messages.success(request, 'رمز عبور کاربر با موفقیت تغییر یافت.')
                return redirect('admin_user_edit', user_id=user_id)

        elif action == 'update_postal_tracking' and credit_request:
            tracking_form = PostalTrackingForm(request.POST, instance=credit_request)
            if tracking_form.is_valid():
                tracking_form.save()
                messages.success(request, 'کد رهگیری پستی با موفقیت ثبت/ویرایش شد.')
                return redirect('admin_user_edit', user_id=user_id)

        elif action == 'delete_user':
            user_to_edit.delete()
            messages.success(request, f'کاربر {user_to_edit.username} با موفقیت حذف شد.')
            return redirect('admin_user_list')

    context = {
        'user_to_edit': user_to_edit,
        'credit_request': credit_request,
        'user_form': user_form,
        'password_form': password_form,
        'tracking_form': tracking_form,
    }
    return render(request, 'staff_panel/user_edit_page.html', context)


@login_required
@admin_required
def admin_add_user_view(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data.get('phone_number') or form.cleaned_data.get('email')
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f"کاربر جدید '{user.get_full_name()}' با موفقیت ایجاد شد.")
            return redirect('admin_user_list')
    else:
        form = AdminUserCreationForm()

    context = {
        'form': form
    }
    return render(request, 'staff_panel/add_user.html', context)