from django.shortcuts import render, redirect

def layout(request):
    return render(request, 'dashboard/layout/layout.html')

def layout_edit(request):
    return render(request, 'dashboard/layout/layout_edit.html')