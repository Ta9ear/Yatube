from django.test import TestCase


class ViewTestClass(TestCase):
    def test_error_page(self):
        """Testing 404 page"""
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
