from django.contrib.auth.models import User
from store.models import Collection
from rest_framework import status
import pytest
from model_bakery import baker


@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post("/store/collections/", collection)

    return do_create_collection


@pytest.fixture
def update_collection(api_client):
    def do_update_collection(collection_id, collection, method="PUT"):
        return (
            api_client.patch(f"/store/collections/{collection_id}/", collection)
            if method == "PATCH"
            else api_client.put(f"/store/collections/{collection_id}/", collection)
        )

    return do_update_collection


@pytest.fixture
def delete_collection(api_client):
    def do_delete_collection(collection_id):
        return api_client.delete(f"/store/collections/{collection_id}/")

    return do_delete_collection


@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_anonymous_returns_401(self, create_collection):
        response = create_collection({"title": "a"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, create_collection, authenticate):
        authenticate()

        response = create_collection({"title": "a"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, create_collection, authenticate):
        authenticate(is_staff=True)

        response = create_collection({"title": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["title"] is not None

    def test_if_data_is_valid_returns_201(self, create_collection, authenticate):
        authenticate(is_staff=True)

        response = create_collection({"title": "a"})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0


@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_collection_exists_returns_200(self, api_client):
        # Arrange
        collection = baker.make(Collection)

        response = api_client.get(f"/store/collections/{collection.id}/")
        # tworzenie dziesiec rekordów z przypisaną kolekcją, gdybym jej nie przypisał to by powstało po prostu 10 rekordów z losowymi kolekcjami
        # baker.make(collection, collection=collection, _quantity=10)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": collection.id,
            "title": collection.title,
            "products_count": 0,
        }

    def test_if_collections_exists_returns_200(self, api_client):
        baker.make(Collection, _quantity=10)

        response = api_client.get("/store/collections/")

        assert response.status_code == status.HTTP_200_OK
        print(response.data)
        assert len(response.data["results"]) == 10


@pytest.mark.django_db
class TestUpdateCollection:
    def test_if_user_is_anonymous_for_put_request_returns_401(self, update_collection):
        response = update_collection(1, {})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_for_put_request_returns_403(
        self, update_collection, authenticate
    ):
        authenticate()
        response = update_collection(1, {})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_for_put_request_returns_400(
        self, update_collection, authenticate
    ):
        authenticate(is_staff=True)
        collection = baker.make(Collection)
        response = update_collection(collection.id, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_data_is_valid_for_put_request_returns_200(
        self, update_collection, authenticate
    ):
        authenticate(is_staff=True)
        collection = baker.make(Collection)

        response = update_collection(collection.id, {"title": "a"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "a"

    def test_if_user_is_anonymous_for_patch_request_returns_401(
        self, update_collection
    ):
        response = update_collection(1, {}, "PATCH")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_for_patch_request_returns_403(
        self, update_collection, authenticate
    ):
        authenticate()
        response = update_collection(1, {}, "PATCH")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_for_patch_request_returns_200(
        self, update_collection, authenticate
    ):
        authenticate(is_staff=True)
        collection = baker.make(Collection)
        response = update_collection(collection.id, {"a": "a"}, "PATCH")

        assert response.status_code == status.HTTP_200_OK
        assert not "a" in response.data.keys()

    def test_if_data_is_valid_for_patch_request_returns_200(
        self, update_collection, authenticate
    ):
        authenticate(is_staff=True)
        collection = baker.make(Collection)
        response = update_collection(collection.id, {"title": "a"}, "PATCH")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "a"


@pytest.mark.django_db
class TestDeletecollection:
    def test_if_user_is_anonymous_returns_401(self, delete_collection):
        response = delete_collection(1)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, delete_collection, authenticate):
        authenticate()
        response = delete_collection(1)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_id_is_invalid_returns_400(self, delete_collection, authenticate):
        authenticate(is_staff=True)
        response = delete_collection(1)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_id_is_valid_returns_400(self, delete_collection, authenticate):
        authenticate(is_staff=True)
        collection_id = baker.make(Collection).id
        response = delete_collection(collection_id)

        assert response.status_code == status.HTTP_204_NO_CONTENT
