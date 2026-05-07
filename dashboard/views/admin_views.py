from django.shortcuts import render, redirect
from dashboard.models.custom_user import CustomUser
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

def user_registration(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # 🔴 Password check
        if password != confirm_password:
            return render(request, 'dashboard/admin/user_registration.html', {
                'error': 'Passwords do not match'
            })

        # 🔴 Username unique
        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'dashboard/admin/user_registration.html', {
                'error': 'Username already exists'
            })

        # 🔴 Email unique
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'dashboard/admin/user_registration.html', {
                'error': 'Email already exists'
            })

        # 🔹 Create user
        user = CustomUser(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            role=role,
        )

        # 🔹 Profile picture
        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES.get('profile_picture')

        # 🔥 Hash password
        user.set_password(password)

        user.save()
        return redirect('user_table')

    return render(request, 'dashboard/admin/user_registration.html')

def profile(request):
    user = request.user

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')

        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES.get('profile_picture')

        user.save()
        return redirect('profile')

    return render(request, 'dashboard/admin/profile.html')

def user_table(request):
    search = request.GET.get('search', '')

    users = CustomUser.objects.all().order_by('-id')

    # 🔍 Search only
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    # 📄 Pagination
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard/admin/user_table.html', {
        'page_obj': page_obj,
        'search': search
    })
