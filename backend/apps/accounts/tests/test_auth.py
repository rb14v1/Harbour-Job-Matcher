from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.common.test_utils import auth_client, create_user


class AuthTests(APITestCase):
    def test_register_and_login(self):
        url = reverse("auth-register")
        response = self.client.post(url, {
            "email": "new@example.com",
            "password": "StrongPass123!",
            "first_name": "New",
            "last_name": "User",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        login_url = reverse("auth-login")
        response = self.client.post(login_url, {"email": "new@example.com", "password": "StrongPass123!"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_me_requires_auth(self):
        url = reverse("auth-me")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user(self):
        user = create_user(email="me@example.com")
        client = auth_client(user)
        response = client.get(reverse("auth-me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "me@example.com")

    def test_logout_blacklists_refresh_token(self):
        user = create_user(email="logout@example.com", password="StrongPass123!")
        login_response = self.client.post(
            reverse("auth-login"), {"email": "logout@example.com", "password": "StrongPass123!"}
        )
        refresh = login_response.data["refresh"]

        client = auth_client(user)
        response = client.post(reverse("auth-logout"), {"refresh": refresh})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

        refresh_response = self.client.post(reverse("auth-refresh"), {"refresh": refresh})
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
