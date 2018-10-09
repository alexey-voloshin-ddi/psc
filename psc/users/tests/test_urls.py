from django.core.urlresolvers import reverse, resolve

from test_plus.test import TestCase


class TestUserURLs(TestCase):
    """Test URL patterns for users app."""

    def setUp(self):
        self.user = self.make_user()

    def test_list_reverse(self):
        """users:user-list should reverse to /users/."""
        self.assertEqual(reverse('users:user-list'), '/users/')

    def test_list_resolve(self):
        """/users/ should resolve to users:user-list."""
        self.assertEqual(resolve('/users/').view_name, 'users:user-list')
