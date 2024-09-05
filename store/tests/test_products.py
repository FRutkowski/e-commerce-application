from decimal import Decimal
from django.contrib.auth.models import User
from store.models import Collection, Product
from rest_framework import status
import pytest
from model_bakery import baker


@pytest.fixture
def create_product(api_client):
    def do_create_product(product):
        return api_client.post("/store/products/", product)

    return do_create_product


def create_product_object():
    collection = baker.make(Collection)
    product = {
        "title": "a",
        "description": "aa",
        "slug": "-",
        "unit_price": 2.0,
        "inventory": 1,
        "collection": collection.id,
    }

    return product


@pytest.fixture
def update_product(api_client):
    def do_update_product(product_id, product, method="PUT"):
        return (
            api_client.patch(f"/store/products/{product_id}/", product)
            if method == "PATCH"
            else api_client.put(f"/store/products/{product_id}/", product)
        )

    return do_update_product


@pytest.fixture
def delete_product(api_client):
    def do_delete_product(product_id):
        return api_client.delete(f"/store/products/{product_id}/")

    return do_delete_product


@pytest.mark.django_db
class TestCreateProduct:
    def test_if_user_is_anonymous_returns_401(self, create_product):
        response = create_product({})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_401(self, authenticate, create_product):
        authenticate()
        response = create_product({})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, authenticate, create_product):
        authenticate(is_staff=True)
        response = create_product({"title": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_data_is_valid_returns_201(self, authenticate, create_product):
        authenticate(is_staff=True)

        product = create_product_object()
        response = create_product(product)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0


@pytest.mark.django_db
class TestRetrieveProduct:
    def test_if_product_exists_returns_200(self, api_client):
        # Arrange
        product = baker.make(Product)

        response = api_client.get(f"/store/products/{product.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": product.id,
            "title": product.title,
            "slug": product.slug,
            "description": product.description,
            "inventory": product.inventory,
            "unit_price": product.unit_price,
            "price_with_tax": product.unit_price * Decimal(1.1),
            "collection": product.collection_id,
            "images": [],
        }

    def test_if_products_exists_returns_200(self, api_client):
        baker.make(Product, _quantity=10)

        response = api_client.get(f"/store/products/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 10


@pytest.mark.django_db
class TestUpdateProduct:
    def test_if_user_is_anonymous_for_put_request_returns_401(self, update_product):
        response = update_product(1, {})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_for_put_request_returns_403(
        self, update_product, authenticate
    ):
        authenticate()
        response = update_product(1, {})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_for_put_request_returns_400(
        self, update_product, authenticate
    ):
        authenticate(is_staff=True)
        product = baker.make(Product)
        response = update_product(product.id, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_data_is_valid_for_put_request_returns_200(
        self, update_product, authenticate
    ):
        product_object = create_product_object()
        authenticate(is_staff=True)
        product = baker.make(Product)
        response = update_product(product.id, product_object)

        assert response.status_code == status.HTTP_200_OK

    def test_if_user_is_anonymous_for_patch_request_returns_401(self, update_product):
        response = update_product(1, {}, "PATCH")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_for_patch_request_returns_403(
        self, update_product, authenticate
    ):
        authenticate()
        response = update_product(1, {}, "PATCH")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_for_patch_request_returns_200(
        self, update_product, authenticate
    ):
        authenticate(is_staff=True)
        product = baker.make(Product)
        response = update_product(product.id, {"a": "a"}, "PATCH")

        assert response.status_code == status.HTTP_200_OK
        assert not "a" in response.data.keys()

    def test_if_data_is_valid_for_patch_request_returns_200(
        self, update_product, authenticate
    ):
        authenticate(is_staff=True)
        product = baker.make(Product)
        response = update_product(product.id, {"title": "a"}, "PATCH")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "a"


@pytest.mark.django_db
class TestDeleteProduct:
    def test_if_user_is_anonymous_returns_401(self, delete_product):
        response = delete_product(1)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, delete_product, authenticate):
        authenticate()
        response = delete_product(1)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_id_is_invalid_returns_400(self, delete_product, authenticate):
        authenticate(is_staff=True)
        response = delete_product(1)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_id_is_valid_returns_400(self, delete_product, authenticate):
        authenticate(is_staff=True)
        product = baker.make(Product)
        response = delete_product(product.id)

        assert response.status_code == status.HTTP_204_NO_CONTENT
