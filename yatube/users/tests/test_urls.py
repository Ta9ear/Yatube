from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Guest')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_for_all_users(self):
        """Testing response status code for users app."""
        urls = [
            '/auth/login/',
            '/auth/signup/',
            '/auth/password_change/done/',
            '/auth/password_change/',
            '/auth/password_reset/done/',
            '/auth/password_reset/',
            '/auth/reset/done/',
            '/auth/logout/',
            '/auth/reset/any/any/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Ошибка доступа к странице {url}'
                )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/login/': 'users/login.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/reset/any/any/': 'users/password_reset_confirm.html'
        }

        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Ошибка шаблона при вызове {url}'
                )
