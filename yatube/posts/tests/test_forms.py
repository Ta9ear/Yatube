import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post
from ..utils import check_is_exist_form_comment, check_is_exist_form_post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
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
        cls.gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.post_author = Client()
        self.post_author.force_login(self.user)

    def test_create_post_form(self):
        """Valid form creates new post in DB."""
        post_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='create.gif',
            content=self.gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тест текст',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.post_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        ))
        self.assertEqual(Post.objects.count(), post_count + 1)
        first_object = response.context['page_obj'].object_list[0]
        check_is_exist_form_post(self, first_object, form_data)

    def test_post_edit_form(self):
        """Testing post edit form changes."""
        uploaded = SimpleUploadedFile(
            name='edit.gif',
            content=self.gif,
            content_type='image/gif'
        )
        another_group = Group.objects.create(
            title='Еще один заголовок',
            slug='other-slug',
            description='Еще одно описание',
        )
        form_data = {
            'text': 'Измененный текст',
            'group': another_group.id,
            'image': uploaded
        }
        response = self.post_author.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostCreateFormTests.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}
        ))
        first_object = Post.objects.get(id=self.post.id)
        check_is_exist_form_post(self, first_object, form_data)

    def test_cant_post_create_without_text(self):
        """Testing post can't be created without text."""
        posts_count = Post.objects.count()
        form_data = {
            'text': ''
        }
        response = self.post_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_cant_post_edit_without_text(self):
        """Testing post can't be edited without text."""
        posts_count = Post.objects.count()
        form_date = {
            'text': ''
        }
        response = self.post_author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_date,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class CommentCreateFormTests(TestCase):
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
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Random comment'
        )

    def setUp(self):
        self.post_author = Client()
        self.post_author.force_login(self.user)

    def test_comment_form(self):
        """Valid form creates new comment in DB."""
        comment_count = self.post.comments.count()
        form_data = {
            'post': self.post,
            'text': 'Another random comment'
        }
        response = self.post_author.post(
            reverse('posts:add_comment', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            args=(self.post.id,)
        ))
        self.assertEqual(self.post.comments.count(), comment_count + 1)
        first_object = response.context['comments'][0]
        check_is_exist_form_comment(self, first_object, form_data)


