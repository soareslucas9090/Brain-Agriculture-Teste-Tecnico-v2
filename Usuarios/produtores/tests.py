from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.test import APIClient

from Usuarios.usuarios.models import Usuarios

from .models import Produtores
from .serializers import ProdutoresSerializer

# CPFs e CNPJs válidos para testes
cpf_valido_1 = "66898615033"
cpf_valido_2 = "48879148060"
cpf_valido_3 = "34492326065"
cnpj_valido = "70423785000190"


class ProdutoresModelTestCase(TestCase):
    def setUp(self):
        self.user = Usuarios.objects.create_user(
            cpf_cnpj=cpf_valido_1, nome="Produtor Test", password="password123"
        )

        self.admin_user = Usuarios.objects.create_superuser(
            cpf_cnpj=cnpj_valido, nome="Admin User", password="adminpassword123"
        )

    def test_1_create_produtor_success(self):
        produtor = Produtores.objects.create(usuario=self.user)

        self.assertEqual(produtor.usuario, self.user)
        self.assertEqual(str(produtor), self.user.nome)

    def test_2_produtor_str_method(self):
        produtor = Produtores.objects.create(usuario=self.user)
        self.assertEqual(str(produtor), "Produtor Test")

    def test_3_one_to_one_relationship(self):
        produtor = Produtores.objects.create(usuario=self.user)

        self.assertEqual(self.user.produtor_perfil, produtor)

        with self.assertRaises(Exception):
            Produtores.objects.create(usuario=self.user)

    def test_4_cascade_delete(self):
        produtor = Produtores.objects.create(usuario=self.user)
        produtor_id = produtor.id

        self.user.delete()

        self.assertFalse(Produtores.objects.filter(id=produtor_id).exists())


class ProdutoresSerializerTestCase(TestCase):
    def setUp(self):
        self.user1 = Usuarios.objects.create_user(
            cpf_cnpj=cpf_valido_1, nome="User One", password="password123"
        )

        self.user2 = Usuarios.objects.create_user(
            cpf_cnpj=cpf_valido_2, nome="User Two", password="password123"
        )

    def test_5_serializer_fields(self):
        produtor = Produtores.objects.create(usuario=self.user1)
        serializer = ProdutoresSerializer(instance=produtor)

        expected_fields = {"id", "usuario"}
        self.assertEqual(set(serializer.data.keys()), expected_fields)
        self.assertEqual(serializer.data["usuario"], self.user1.id)

    def test_6_serializer_validation_success(self):
        data = {"usuario": self.user1.id}
        serializer = ProdutoresSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_7_serializer_validation_duplicate_user(self):
        Produtores.objects.create(usuario=self.user1)

        data = {"usuario": self.user1.id}
        serializer = ProdutoresSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("usuario", serializer.errors)
        self.assertIn("Perfil de produtor já criado", str(serializer.errors["usuario"]))


class ProdutoresViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = Usuarios.objects.create_user(
            cpf_cnpj=cpf_valido_1, nome="User One", password="password123"
        )

        self.user2 = Usuarios.objects.create_user(
            cpf_cnpj=cpf_valido_2, nome="User Two", password="password123"
        )

        self.user3 = Usuarios.objects.create_user(
            cpf_cnpj=cpf_valido_3, nome="User Three", password="password123"
        )

        self.admin_user = Usuarios.objects.create_superuser(
            cpf_cnpj=cnpj_valido, nome="Admin User", password="adminpassword123"
        )

        self.produtor1 = Produtores.objects.create(usuario=self.user1)
        self.produtor2 = Produtores.objects.create(usuario=self.user2)

        self.list_url = reverse("usuarios:produtores-list")
        self.detail_url = lambda pk: reverse(
            "usuarios:produtores-detail", kwargs={"pk": pk}
        )

    def test_8_list_produtores_as_user_shows_only_own(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.produtor1.id)

    def test_9_list_produtores_as_admin_shows_all(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_10_retrieve_own_produtor_as_user(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.detail_url(self.produtor1.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.produtor1.id)
        self.assertEqual(response.data["usuario"], self.user1.id)

    def test_11_retrieve_any_produtor_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)

        response1 = self.client.get(self.detail_url(self.produtor1.pk))
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        response2 = self.client.get(self.detail_url(self.produtor2.pk))
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

    def test_12_create_produtor_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user3)
        data = {"usuario": self.user3.id}
        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_13_create_produtor_as_admin_success(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {"usuario": self.user3.id}
        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Produtores.objects.filter(usuario=self.user3).exists())

    def test_14_create_produtor_duplicate_user_validation(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {"usuario": self.user1.id}
        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("usuario", response.data)

    def test_15_update_produtor_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user1)
        data = {"usuario": self.user1.id}
        response = self.client.patch(
            self.detail_url(self.produtor1.pk), data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_16_update_produtor_as_admin_success(self):
        new_user = Usuarios.objects.create_user(
            cpf_cnpj="02845779011", nome="New User", password="password123"
        )

        self.client.force_authenticate(user=self.admin_user)
        data = {"usuario": new_user.id}
        response = self.client.patch(
            self.detail_url(self.produtor1.pk), data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.produtor1.refresh_from_db()
        self.assertEqual(self.produtor1.usuario, new_user)

    def test_17_delete_produtor_as_user_forbidden(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.detail_url(self.produtor1.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_18_delete_produtor_as_admin_success(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url(self.produtor2.pk))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Produtores.objects.filter(pk=self.produtor2.pk).exists())

    def test_19_filter_by_usuario_nome(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url, {"usuario__nome": "User One"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["usuario"], self.user1.id)

    def test_20_filter_by_usuario_cpf_cnpj(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url, {"usuario__cpf_cnpj": cpf_valido_2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["usuario"], self.user2.id)

    def test_21_filter_by_usuario_is_active(self):
        self.user2.is_active = False
        self.user2.save()

        self.client.force_authenticate(user=self.admin_user)

        response_active = self.client.get(self.list_url, {"usuario__is_active": "true"})
        self.assertEqual(response_active.status_code, status.HTTP_200_OK)
        self.assertEqual(response_active.data["count"], 1)

        response_inactive = self.client.get(
            self.list_url, {"usuario__is_active": "false"}
        )
        self.assertEqual(response_inactive.status_code, status.HTTP_200_OK)
        self.assertEqual(response_inactive.data["count"], 1)

    def test_22_user_without_produtor_gets_empty_list(self):
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_23_get_dono_do_registro_method(self):
        from .views import ProdutoresViewSet

        view = ProdutoresViewSet()
        view.request = type("Request", (), {"user": self.user1})()
        view.kwargs = {"pk": self.produtor1.pk}

        self.assertTrue(view.get_dono_do_registro(None))

        view.request.user = self.user2
        self.assertFalse(view.get_dono_do_registro(None))

        view.kwargs = {"pk": 99999}
        self.assertFalse(view.get_dono_do_registro(None))
