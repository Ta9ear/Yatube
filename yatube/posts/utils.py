from django.core.paginator import Paginator

UNITS_ON_PAGE = 10


def paginate(posts_list, request):
    """Paginates template."""
    paginator = Paginator(posts_list, UNITS_ON_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
