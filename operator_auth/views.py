from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

def operator_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # username OR email
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard_index')  # simple redirect
        else:
            return render(request, 'operator_auth/login.html', {
                'error': 'Invalid Username / Email or Password'
            })
    return render(request, 'operator_auth/login.html')

def operator_logout(request):
    if request.method == "POST":
        logout(request)
        return render(request, 'operator_auth/logout.html')

    return redirect('dashboard_index')  # fallback safety