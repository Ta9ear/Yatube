from django.shortcuts import render


def page_not_found(request, exception):
    """Renders 404 not found page"""
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')
