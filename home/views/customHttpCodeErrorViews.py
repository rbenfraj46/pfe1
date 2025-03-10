# -*- coding: utf-8 -*-

"""
---DocStart---
 Description:
 -----------
 Add custom page error for 403 , 404 et 50X for production server.
 -----------
"""
from django.shortcuts import render

# customizing django handlers
def handler404(request, exception):
    return render(request, 'error_page/404.html', status=404)

def handler400(request, exception):
    return render(request, 'error_page/400.html', status=400)

def handler403(request, *args, **argv):
    return render(request, 'error_page/403.html', status=403)

def handler405(request, *args, **argv):
    return render(request, 'error_page/405.html', status=405)