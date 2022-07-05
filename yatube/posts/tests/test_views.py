import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post
from ..utils import check_is_exist_view, reverse_from_tuple_detail

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.small_jpg = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='post.jpg',
            content=cls.small_jpg,
            content_type='image/jpg'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )
        cls.INDEX = (
            'posts:index',
            'posts/index.html',
            None
        )
        cls.GROUP = (
            'posts:group_list',
            'posts/group_list.html',
            (cls.post.group.slug,)
        )
        cls.PROFILE = (
            'posts:profile',
            'posts/profile.html',
            (cls.post.author.username,)
        )
        cls.DETAIL = (
            'posts:post_detail',
            'posts/post_detail.html',
            (cls.post.id,)
        )
        cls.EDIT = (
            'posts:post_edit',
            'posts/create_post.html',
            (cls.post.id,)
        )
        cls.CREATE = (
            'posts:post_create',
            'posts/create_post.html',
            None
        )
        cls.urls_tuple_template = [
            cls.INDEX,
            cls.GROUP,
            cls.PROFILE,
            cls.DETAIL,
            cls.EDIT,
            cls.CREATE,
        ]
        cls.urls_tuple_context = [
            cls.INDEX,
            cls.GROUP,
            cls.PROFILE,
        ]
        cls.urls_tuple_context_1 = [
            cls.EDIT,
            cls.CREATE
        ]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Test users Login."""
        self.post_author = Client()
        self.post_author.force_login(self.user)

    def test_pages_uses_correct_template_post_author(self):
        """Testing pages uses correct template for post author."""
        cache.clear()
        for reverse_name, template, args_tuple in self.urls_tuple_template:
            with self.subTest(reverse_name=reverse_name):
                response = self.post_author.get(reverse(
                    reverse_name,
                    args=args_tuple
                ))
                self.assertTemplateUsed(response, template)

    def test_index_group_profile_correct_context(self):
        """Testing index, group list, profile pages showing correct context."""
        cache.clear()
        for reverse_name, template, args_tuple in self.urls_tuple_context:
            with self.subTest(reverse_name=reverse_name):
                response = self.post_author.get(reverse(
                    reverse_name,
                    args=args_tuple
                ))
                self.assertEqual(
                    response.context['page_obj'].object_list,
                    [self.post]
                )
                first_object = response.context['page_obj'].object_list[0]
                check_is_exist_view(self, first_object)

    def test_post_detail_correct_context(self):
        """Testing post_detail page showing correct context."""
        response = self.post_author.get(reverse_from_tuple_detail(self))
        self.assertEqual(
            response.context['post_object'],
            self.post
        )
        first_object = response.context['post_object']
        check_is_exist_view(self, first_object)

    def test_post_edit_and_create_correct_context(self):
        """Testing post_create and edit pages showing correct context."""
        for reverse_name, template, args_tuple in self.urls_tuple_context_1:
            with self.subTest(reverse_name=reverse_name):
                response = self.post_author.get(reverse(
                    reverse_name,
                    args=args_tuple
                ))
                form_fields = {
                    'text': forms.fields.CharField,
                    'group': forms.fields.ChoiceField,
                    'image': forms.fields.ImageField,
                }
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = (response.context.
                                      get('form').fields.get(value))
                        self.assertIsInstance(form_field, expected)

    def test_not_in_wrong_group(self):
        """Testing post object not in wrong group."""
        other_group = Group.objects.create(
            title='Еще один заголовок',
            slug='other-slug',
            description='Еще одно описание',
        )
        response = self.post_author.get(reverse(
            'posts:group_list',
            kwargs={'slug': other_group.slug}
        ))
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_cache(self):
        new_post = Post.objects.create(
            text='Новый пост для кеша',
            author=self.user,
            group=self.group,
        )
        content_before_delete = self.post_author.get(
            reverse('posts:index')).content
        new_post.delete()
        content_after_delete = self.post_author.get(
            reverse('posts:index')).content
        cache.clear()
        content_after_cache_clear = self.post_author.get(
            reverse('posts:index')).content
        self.assertEqual(
            content_before_delete, content_after_delete
        )
        self.assertNotEqual(
            content_after_delete, content_after_cache_clear
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.UNITS_ON_PAGE_1 = 10
        cls.UNITS_ON_PAGE_2 = 3
        cls.user_writer = User.objects.create_user(username='WriteLover')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.INDEX = (
            'posts:index',
            None
        )
        cls.GROUP = (
            'posts:group_list',
            (cls.group.slug,)
        )
        cls.PROFILE = (
            'posts:profile',
            (cls.user_writer.username,)
        )
        for i in range(13):
            Post.objects.create(
                text=f'Тестовый пост {i}',
                author=cls.user_writer,
                group=cls.group,
            )
        cls.urls_tuple_paginator = [
            cls.INDEX,
            cls.GROUP,
            cls.PROFILE
        ]

    def setUp(self):
        """Test users Login."""
        cache.clear()
        self.post_writer = Client()
        self.post_writer.force_login(self.user_writer)

    def test_first_page_contains_ten_records(self):
        """Testing the first page has the right amount of units"""
        for reverse_name, args_tuple in self.urls_tuple_paginator:
            with self.subTest(reverse_name=reverse_name):
                response = self.post_writer.get(reverse(
                    reverse_name,
                    args=args_tuple
                ))
                self.assertEqual(
                    len(response.context['page_obj']),
                    self.UNITS_ON_PAGE_1
                )

    def test_second_page_contains_three_records(self):
        """Testing the second page has the right amount of units"""
        for reverse_name, args_tuple in self.urls_tuple_paginator:
            with self.subTest(reverse_name=reverse_name):
                response = self.post_writer.get(reverse(
                    reverse_name,
                    args=args_tuple
                ) + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    self.UNITS_ON_PAGE_2
                )
