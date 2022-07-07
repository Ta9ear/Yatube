from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from .utils import reverse_from_tuple_detail, reverse_from_tuple_edit

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )
        cls.INDEX = (
            'posts:index',
            'posts/index.html',
            None,
        )
        cls.GROUP = (
            'posts:group_list',
            'posts/group_list.html',
            (cls.post.group.slug,),
        )
        cls.PROFILE = (
            'posts:profile',
            'posts/profile.html',
            (cls.post.author.username,),
        )
        cls.DETAIL = (
            'posts:post_detail',
            'posts/post_detail.html',
            (cls.post.id,),
        )
        cls.EDIT = (
            'posts:post_edit',
            'posts/create_post.html',
            (cls.post.id,),
        )
        cls.CREATE = (
            'posts:post_create',
            'posts/create_post.html',
            None,
        )
        cls.COMMENT = (
            'posts:add_comment',
            None,
            (cls.post.id,)
        )
        cls.urls_tuple_guest_status = [
            cls.INDEX,
            cls.GROUP,
            cls.DETAIL,
            cls.PROFILE,
        ]
        cls.urls_tuple_guest_redir = [
            cls.CREATE,
            cls.EDIT,
            cls.COMMENT
        ]
        cls.urls_tuple_tmp_auth = [
            cls.INDEX,
            cls.GROUP,
            cls.DETAIL,
            cls.PROFILE,
            cls.CREATE,
            cls.EDIT,
        ]
        cls.urls_tuple_auth_redir = [
            cls.EDIT,
            cls.COMMENT
        ]

    def setUp(self):
        """Test users Login."""
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Guest')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_author = Client()
        self.post_author.force_login(StaticURLTests.user)

    def test_author_posts_edit(self):
        """Testing author posts edit."""
        response = self.post_author.get(
            reverse_from_tuple_edit(self),
            follow=True
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            f'Ошибка доступа к странице {self.EDIT[0]}'
        )

    def test_authorized_posts_edit_and_comment(self):
        """Testing authorized posts edit redirect."""
        for reverse_name, template, args_tuple in self.urls_tuple_auth_redir:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse(
                    reverse_name,
                    args=args_tuple
                ))
        self.assertRedirects(
            response, reverse_from_tuple_detail(self))

    def test_guest_redirect(self):
        """Testing guest post create, edit, comment redirect."""
        for reverse_name, template, args_tuple in self.urls_tuple_guest_redir:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse(
                    reverse_name,
                    args=args_tuple
                ))
                self.assertRedirects(
                    response,
                    reverse('users:login') + '?next=' + reverse(
                        reverse_name,
                        args=args_tuple
                    ),
                )

    def test_unexisting_page_status_code(self):
        """Testing unexisting page status code"""
        clients = [
            self.post_author,
            self.guest_client
        ]
        for client in clients:
            response = client.get('/unexisting_page/')
            self.assertEqual(
                response.status_code,
                HTTPStatus.NOT_FOUND,
                'Ошибка доступа к странице /unexisting_page/'
            )

    def test_response_status_code_authorized(self):
        """Testing authorized response status code for posts app."""
        for reverse_name, template, args_tuple in self.urls_tuple_tmp_auth:
            with self.subTest(reverse_name=reverse_name):
                response = self.post_author.get(reverse(
                    reverse_name,
                    args=args_tuple
                ))
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Ошибка доступа к странице {reverse_name}'
                )

    def test_response_status_code_guest(self):
        """Testing guest response status code for posts app."""
        for reverse_name, template, args_tuple in self.urls_tuple_guest_status:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse(
                    reverse_name,
                    args=args_tuple
                ))
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    f'Ошибка доступа к странице {reverse_name}'
                )

    def test_urls_uses_correct_template(self):
        """Testing URL-adresses use the correct templates for posts app."""
        for reverse_name, template, args_tuple in self.urls_tuple_tmp_auth:
            with self.subTest(reverse_name=reverse_name):
                response = self.post_author.get(reverse(
                    reverse_name,
                    args=args_tuple
                ))
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Ошибка шаблона при вызове {reverse_name}'
                )
