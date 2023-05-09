from django.contrib.auth import get_user_model
from django.test import TestCase, SimpleTestCase
from django.urls import reverse, resolve
# from .views import SignUpView


class CustomUserTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="will", email="will@email.com", password="testpass123"
        )
        self.assertEqual(user.username, "will")
        self.assertEqual(user.email, "will@email.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username="superadmin", email="superadmin@email.com", password="testpass123"
        )
        self.assertEqual(admin_user.username, "superadmin")
        self.assertEqual(admin_user.email, "superadmin@email.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        
class HomepageTests(SimpleTestCase):
    
    def setUp(self):
        url = reverse('home')
        self.response = self.client.get(url)
        
    def test_homepage_status_code(self):
        self.assertEqual(self.response.status_code, 200)
        
    def test_homepage_url_name(self):
        self.assertEqual(self.response.status_code, 200)
    
    def test_homepage_template(self):
        # response = self.client.get('/')
        self.assertTemplateUsed(self.response, 'home.html')
        
    def test_homepage_contains_correct_html(self): 
        # response = self.client.get('/')
        self.assertContains(self.response, 'home page')
        
    def test_homepage_does_not_contain_incorrect_html(self): 
        # response = self.client.get('/')
        self.assertNotContains(
        self.response, 'Hi there! I should not be on the page.')

    '''test to make sure a given url is being directed to a given view'''
    # def test_homepage_url_resolves_homepageview(self): # new
    #     view = resolve('/accounts/signup/')
    #     self.assertEqual(
    #         view.func.__name__,
    #         SignUpView.as_view().__name__
    #         )
