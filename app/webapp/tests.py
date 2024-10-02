from django.test import TestCase
from django.urls import reverse


class IndexPageTests(TestCase):
    def test_index_page_status_code(self):
        # Use reverse to get the URL of the index page
        response = self.client.get(reverse('index'))

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
