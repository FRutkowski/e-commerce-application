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

        # tworzenie dziesiec rekordów z przypisaną kolekcją, gdybym jej nie przypisał to by powstało po prostu 10 rekordów z losowymi kolekcjami
        # baker.make(Product, collection=collection, _quantity=10)

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

        # tworzenie dziesiec rekordów z przypisaną kolekcją, gdybym jej nie przypisał to by powstało po prostu 10 rekordów z losowymi kolekcjami
        # baker.make(Product, collection=collection, _quantity=10)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 10
