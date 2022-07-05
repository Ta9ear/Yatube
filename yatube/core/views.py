from django.shortcuts import render


def page_not_found(request, exception):
    """Renders 404 not found page"""
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def server_error(request):
    """Renders 500 internal server error page"""
    return render(request, 'core/500.html', status=500)


def permission_denied(request, exception):
    """Renders 403 forbidden page"""
    return render(request, 'core/403.html', status=403)


def csrf_failure(request, reason=''):
    """Renders 403 csrf failure page"""
    return render(request, 'core/403csrf.html')
