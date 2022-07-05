from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostCreateFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_create_user_form(self):
        """Valid form creates new user."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Teodor',
            'last_name': 'Ruzvelt',
            'username': 'Teddy',
            'email': 'Teddy@yandex.ru',
            'password1': 'Kakoytoparol12*',
            'password2': 'Kakoytoparol12*'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name='Teodor',
                last_name='Ruzvelt',
                username='Teddy',
                email='Teddy@yandex.ru'
            ).exists()
        )
