from django.core.paginator import Paginator
from django.urls import reverse

UNITS_ON_PAGE = 10


def paginate(posts_list, request):
    """Paginates template."""
    paginator = Paginator(posts_list, UNITS_ON_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def check_is_exist_form_post(self, first_object, form_data):
    """Check if post exist test forms."""
    check_dict = {
        first_object.author.username: self.user.username,
        first_object.text: form_data['text'],
        first_object.group.id: form_data['group'],
        first_object.image: 'posts/' + str(form_data['image'])
    }
    for post_field, expected_field in check_dict.items():
        with self.subTest(post_field=post_field):
            self.assertEqual(post_field, expected_field)


def check_is_exist_form_comment(self, first_object, form_data):
    """Check if comment exist test forms."""
    check_dict = {
        first_object.author.username: self.user.username,
        first_object.post: form_data['post'],
        first_object.text: form_data['text'],
    }
    for post_field, expected_field in check_dict.items():
        with self.subTest(post_field=post_field):
            self.assertEqual(post_field, expected_field)


def check_is_exist_view(self, first_object):
    """Check if user exist test views."""
    check_dict = {
        first_object.author.username: self.post.author.username,
        first_object.text: self.post.text,
        first_object.group.title: self.post.group.title,
        first_object.image: self.post.image
    }
    for post_field, expected_field in check_dict.items():
        with self.subTest(post_field=post_field):
            self.assertEqual(post_field, expected_field)


def reverse_from_tuple_edit(self):
    """Reverse tuple for edit."""
    return reverse(
        self.EDIT[0],
        args=self.EDIT[2]
    )


def reverse_from_tuple_detail(self):
    """Reverse tuple for detail."""
    return reverse(
        self.DETAIL[0],
        args=self.DETAIL[2]
    )
