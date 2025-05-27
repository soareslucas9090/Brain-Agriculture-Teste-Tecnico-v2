from unittest.mock import patch

from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.test import APIClient

from Core.Validations import validar_cpf_cnpj
from Usuarios.usuarios.models import Usuarios
from Usuarios.usuarios.serializers import Usuarios2AdminSerializer, UsuariosSerializer

cpf_valido = "66898615033"
cnpj_valido = "70423785000190"


class UsuariosModelTestCase(TestCase):
    def setUp(self):
        self.valid_cpf = cpf_valido
        self.valid_cnpj = cnpj_valido
        self.invalid_cpf = "11111111111"

        self.user_data = {
            "cpf_cnpj": self.valid_cpf,
            "nome": "fulano de tal",
            "password": "password123",
        }

        self.admin_data = {
            "cpf_cnpj": self.valid_cnpj,
            "nome": "admin user",
            "password": "superpassword123",
        }

    def test_1_create_user_success(self):
        user = Usuarios.objects.create_user(**self.user_data)

        self.assertEqual(user.cpf_cnpj, self.valid_cpf)
        self.assertEqual(user.nome, "Fulano de Tal")
        self.assertTrue(user.check_password("password123"))
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_2_create_superuser_success(self):
        admin_user = Usuarios.objects.create_superuser(**self.admin_data)

        self.assertEqual(admin_user.cpf_cnpj, self.valid_cnpj)
        self.assertEqual(admin_user.nome, "Admin User")
        self.assertTrue(admin_user.check_password("superpassword123"))
        self.assertTrue(admin_user.is_admin)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)

    def test_3_superuser_sets_is_admin_true(self):
        user = Usuarios(
            cpf_cnpj=self.valid_cpf, nome="Test User", is_superuser=True, is_admin=False
        )
        user.save()
        self.assertTrue(user.is_admin)

    @patch("Core.Validations.validar_cpf_cnpj")
    def test_4_cpf_cnpj_validation_on_save(self, mock_validar):
        mock_validar.side_effect = DjangoValidationError(
            "CPF inválido: todos os dígitos são iguais."
        )

        with self.assertRaises(DjangoValidationError):
            Usuarios.objects.create_user(
                cpf_cnpj=self.invalid_cpf,
                nome="Invalid CPF User",
                password="password123",
            )

    def test_5_username_field(self):
        self.assertEqual(Usuarios.USERNAME_FIELD, "cpf_cnpj")

    def test_6_required_fields(self):
        self.assertIn("nome", Usuarios.REQUIRED_FIELDS)


class UsuariosSerializerTestCase(TestCase):

    def setUp(self):
        self.user = Usuarios.objects.create_user(
            cpf_cnpj=cpf_valido, nome="Test User", password="password123"
        )

        self.admin_user = Usuarios.objects.create_superuser(
            cpf_cnpj=cnpj_valido, nome="Admin User", password="adminpassword123"
        )

    def test_7_usuarios_serializer_fields(self):
        serializer = UsuariosSerializer(instance=self.user)
        expected_fields = {"id", "nome", "cpf_cnpj", "is_active", "produtor_perfil"}
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_8_usuarios2admin_serializer_fields(self):
        serializer = Usuarios2AdminSerializer(instance=self.admin_user)
        data = serializer.data

        self.assertIn("is_admin", data)
        self.assertIn("is_superuser", data)
        self.assertIn("is_active", data)

    def test_9_usuarios2admin_serializer_password_validation(self):
        serializer = Usuarios2AdminSerializer()

        with self.assertRaises(DRFValidationError):
            serializer.validate_password("123")

        validated_password = serializer.validate_password("validpassword123")
        self.assertTrue(validated_password.startswith("pbkdf2_sha256"))


class UsuariosViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = Usuarios.objects.create_user(
            cpf_cnpj=cpf_valido, nome="Test User", password="testpassword"
        )

        self.admin_user = Usuarios.objects.create_superuser(
            cpf_cnpj=cnpj_valido, nome="Admin User", password="adminpassword"
        )

        self.other_user = Usuarios.objects.create_user(
            cpf_cnpj="48879148060", nome="Other User", password="otherpassword"
        )

        self.list_url = reverse("usuarios:usuarios-list")
        self.detail_url = lambda pk: reverse(
            "usuarios:usuarios-detail", kwargs={"pk": pk}
        )

    def test_10_list_usuarios_anonymous_user(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_11_list_usuarios_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_12_list_usuarios_admin_user(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_13_retrieve_own_data_as_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url(self.user.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["cpf_cnpj"], self.user.cpf_cnpj)
        self.assertNotIn("is_admin", response.data)

    def test_14_retrieve_other_data_as_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url(self.other_user.pk))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_15_retrieve_any_data_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.detail_url(self.user.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["cpf_cnpj"], self.user.cpf_cnpj)

    def test_16_update_data_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("usuarios:usuarios-detail", kwargs={"pk": self.user.pk})
        updated_data = {"nome": "Updated by Admin", "is_active": False}
        response = self.client.patch(url, updated_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.nome == "Updated By Admin"
        assert not self.user.is_active

    def test_17_delete_own_data_as_non_admin(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("usuarios:usuarios-detail", kwargs={"pk": self.user.pk})
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_18_delete_other_data_as_non_admin(self):
        other_user = Usuarios.objects.create_user(
            nome="User to Delete", cpf_cnpj="02845779011", password="deletepassword"
        )
        self.client.force_authenticate(user=self.user)
        url = reverse("usuarios:usuarios-detail", kwargs={"pk": other_user.pk})
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_19_delete_data_as_admin(self):
        user_to_delete = Usuarios.objects.create_user(
            nome="User to Delete by Admin",
            cpf_cnpj="58788497046",
            password="deletepassword",
        )
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("usuarios:usuarios-detail", kwargs={"pk": user_to_delete.pk})
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Usuarios.objects.filter(pk=user_to_delete.pk).exists()

    def test_20_invalid_cpf_cnpj_create_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("usuarios:usuarios-list")
        new_user_data = {
            "nome": "Invalid CPF User",
            "cpf_cnpj": "11111111111",  # Invalid
            "password": "newpassword",
            "is_active": True,
        }
        response = self.client.post(url, new_user_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "cpf_cnpj" in response.data


class UsuariosPermissionsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = Usuarios.objects.create_user(
            cpf_cnpj="34492326065", nome="User One", password="password123"
        )

        self.user2 = Usuarios.objects.create_user(
            cpf_cnpj="34573021035", nome="User Two", password="password123"
        )

        self.user3 = Usuarios.objects.create_user(
            cpf_cnpj="66331149074", nome="User Three", password="password123"
        )

        self.admin1 = Usuarios.objects.create_superuser(
            cpf_cnpj="49829339000194", nome="Admin One", password="adminpass123"
        )

        self.admin2 = Usuarios.objects.create_superuser(
            cpf_cnpj="87875513000124", nome="Admin Two", password="adminpass123"
        )

        self.list_url = reverse("usuarios:usuarios-list")
        self.detail_url = lambda pk: reverse(
            "usuarios:usuarios-detail", kwargs={"pk": pk}
        )

    def test_21_admin_can_access_general_user_list(self):
        self.client.force_authenticate(user=self.admin1)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 5)

    def test_22_admin_can_access_any_user_detail(self):
        self.client.force_authenticate(user=self.admin1)

        response1 = self.client.get(self.detail_url(self.user1.pk))
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data["cpf_cnpj"], self.user1.cpf_cnpj)
        self.assertIn("is_admin", response1.data)

        response2 = self.client.get(self.detail_url(self.user2.pk))
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data["cpf_cnpj"], self.user2.cpf_cnpj)

        response3 = self.client.get(self.detail_url(self.user3.pk))
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertEqual(response3.data["cpf_cnpj"], self.user3.cpf_cnpj)

    def test_23_admin_can_access_other_admin_data(self):
        self.client.force_authenticate(user=self.admin1)

        response = self.client.get(self.detail_url(self.admin2.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["cpf_cnpj"], self.admin2.cpf_cnpj)
        self.assertTrue(response.data["is_admin"])
        self.assertTrue(response.data["is_superuser"])

    def test_24_user_cannot_access_general_list(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_25_user_can_only_access_own_data(self):
        self.client.force_authenticate(user=self.user1)

        response_own = self.client.get(self.detail_url(self.user1.pk))
        self.assertEqual(response_own.status_code, status.HTTP_200_OK)
        self.assertEqual(response_own.data["cpf_cnpj"], self.user1.cpf_cnpj)
        self.assertNotIn("is_admin", response_own.data)

        response_other = self.client.get(self.detail_url(self.user2.pk))
        self.assertEqual(response_other.status_code, status.HTTP_403_FORBIDDEN)

        response_admin = self.client.get(self.detail_url(self.admin1.pk))
        self.assertEqual(response_admin.status_code, status.HTTP_403_FORBIDDEN)

    def test_26_admin_can_create_users(self):
        self.client.force_authenticate(user=self.admin1)

        new_user_data = {
            "nome": "new user created by admin",
            "cpf_cnpj": "99122080058",
            "password": "newuserpass123",
        }

        response = self.client.post(self.list_url, new_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_user = Usuarios.objects.get(cpf_cnpj="99122080058")
        self.assertEqual(created_user.nome, "New User Created By Admin")
        self.assertFalse(created_user.is_admin)
        self.assertFalse(created_user.is_superuser)

    def test_27_admin_can_create_other_admins(self):
        self.client.force_authenticate(user=self.admin1)

        new_admin_data = {
            "nome": "new admin created",
            "cpf_cnpj": "94187332006",
            "password": "newadminpass123",
            "is_admin": True,
        }

        response = self.client.post(self.list_url, new_admin_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_admin = Usuarios.objects.get(cpf_cnpj="94187332006")
        self.assertEqual(created_admin.nome, "New Admin Created")
        self.assertTrue(created_admin.is_admin)

    def test_28_user_cannot_create_users(self):
        self.client.force_authenticate(user=self.user1)

        new_user_data = {
            "nome": "Unauthorized User",
            "cpf_cnpj": "11122233344",
            "password": "unauthorizedpass123",
        }

        response = self.client.post(self.list_url, new_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_29_admin_can_update_any_user(self):
        self.client.force_authenticate(user=self.admin1)

        update_data = {"nome": "updated by admin", "is_active": False}

        response = self.client.patch(
            self.detail_url(self.user1.pk), update_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user1.refresh_from_db()
        self.assertEqual(self.user1.nome, "Updated By Admin")
        self.assertFalse(self.user1.is_active)

    def test_30_admin_can_update_other_admin(self):
        self.client.force_authenticate(user=self.admin1)

        update_data = {"nome": "admin updated by other admin", "is_active": False}

        response = self.client.patch(
            self.detail_url(self.admin2.pk), update_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.admin2.refresh_from_db()
        self.assertEqual(self.admin2.nome, "Admin Updated By Other Admin")
        self.assertFalse(self.admin2.is_active)

    def test_31_user_cannot_update_own_data(self):
        self.client.force_authenticate(user=self.user1)

        update_data = {"nome": "self updated name"}

        response = self.client.patch(
            self.detail_url(self.user1.pk), update_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_32_user_cannot_update_other_users(self):
        self.client.force_authenticate(user=self.user1)

        update_data = {"nome": "Unauthorized Update"}

        response = self.client.patch(
            self.detail_url(self.user2.pk), update_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
