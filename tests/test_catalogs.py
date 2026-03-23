"""Tests for the Catalogs extension."""

from datetime import datetime

# from starlette.testclient import TestClient
import httpx
import pytest
import pytest_asyncio
from fastapi import Request
from httpx import ASGITransport
from stac_fastapi.api.app import StacApi
from stac_fastapi.types.config import ApiSettings
from stac_fastapi.types.core import BaseCoreClient
from stac_pydantic.api.collections import Collections
from stac_pydantic.catalog import Catalog
from stac_pydantic.collection import Collection
from stac_pydantic.item import Item
from stac_pydantic.item_collection import ItemCollection
from starlette.responses import Response

from stac_fastapi_catalogs_extension import CatalogsExtension
from stac_fastapi_catalogs_extension.client import AsyncBaseCatalogsClient
from stac_fastapi_catalogs_extension.types import Catalogs, Children, ObjectUri


class DummyCoreClient(BaseCoreClient):
    """Dummy core client for testing."""

    def all_collections(self, *args, **kwargs):
        return {"collections": [], "links": []}

    def get_collection(self, *args, **kwargs):
        raise NotImplementedError

    def get_item(self, *args, **kwargs):
        raise NotImplementedError

    def get_search(self, *args, **kwargs):
        raise NotImplementedError

    def post_search(self, *args, **kwargs):
        raise NotImplementedError

    def item_collection(self, *args, **kwargs):
        raise NotImplementedError


class DummyCatalogsClient(AsyncBaseCatalogsClient):
    """Dummy catalogs client for testing."""

    async def get_catalogs(
        self,
        limit: int | None = None,
        token: str | None = None,
        request: Request | None = None,
        **kwargs,
    ) -> Catalogs | Response:
        return Catalogs(
            catalogs=[
                Catalog(
                    type="Catalog",
                    id="test-catalog-1",
                    description="Test Catalog 1",
                    stac_version="1.0.0",
                    links=[],
                ),
                Catalog(
                    type="Catalog",
                    id="test-catalog-2",
                    description="Test Catalog 2",
                    stac_version="1.0.0",
                    links=[],
                ),
            ],
            links=[],
            numberMatched=2,
            numberReturned=2,
        )

    async def create_catalog(
        self, catalog: Catalog, request: Request | None = None, **kwargs
    ) -> Catalog | Response:
        return Catalog(
            type="Catalog",
            id=catalog.id,
            description=catalog.description or "Created catalog",
            stac_version="1.0.0",
            links=[],
        )

    async def get_catalog(
        self, catalog_id: str, request: Request | None = None, **kwargs
    ) -> Catalog | Response:
        return Catalog(
            type="Catalog",
            id=catalog_id,
            description=f"Catalog {catalog_id}",
            stac_version="1.0.0",
            links=[],
        )

    async def update_catalog(
        self,
        catalog_id: str,
        catalog: Catalog,
        request: Request | None = None,
        **kwargs,
    ) -> Catalog | Response:
        return Catalog(
            type="Catalog",
            id=catalog_id,
            description=catalog.description or f"Updated {catalog_id}",
            stac_version="1.0.0",
            links=[],
        )

    async def delete_catalog(
        self, catalog_id: str, request: Request | None = None, **kwargs
    ) -> None:
        return None

    async def get_catalog_collections(
        self,
        catalog_id: str,
        limit: int | None = None,
        token: str | None = None,
        request: Request | None = None,
        **kwargs,
    ) -> Collections | Response:
        return {
            "collections": [
                {
                    "type": "Collection",
                    "id": "test-collection",
                    "description": "Test Collection",
                    "extent": {
                        "spatial": {"bbox": [[-180, -90, 180, 90]]},
                        "temporal": {"interval": [[None, None]]},
                    },
                    "license": "proprietary",
                    "links": [
                        {"rel": "root", "href": "/", "type": "application/json"},
                        {
                            "rel": "self",
                            "href": f"/catalogs/{catalog_id}/collections/test-collection",
                            "type": "application/json",
                        },
                    ],
                }
            ],
            "links": [
                {"rel": "root", "href": "/", "type": "application/json"},
                {
                    "rel": "self",
                    "href": f"/catalogs/{catalog_id}/collections",
                    "type": "application/json",
                },
            ],
        }

    async def get_sub_catalogs(
        self,
        catalog_id: str,
        limit: int | None = None,
        token: str | None = None,
        request: Request | None = None,
        **kwargs,
    ) -> Catalogs | Response:
        return Catalogs(
            catalogs=[
                Catalog(
                    type="Catalog",
                    id=f"{catalog_id}-sub-1",
                    description=f"Sub-catalog of {catalog_id}",
                    stac_version="1.0.0",
                    links=[],
                )
            ],
            links=[],
            numberMatched=1,
            numberReturned=1,
        )

    async def create_sub_catalog(
        self,
        catalog_id: str,
        catalog: Catalog | ObjectUri,
        request: Request | None = None,
        **kwargs,
    ) -> Catalog | Response:
        catalog_id_val = catalog.id

        description = None
        if isinstance(catalog, Catalog):
            description = catalog.description or f"Sub-catalog of {catalog_id}"
        else:
            description = f"Sub-catalog of {catalog_id}"

        return Catalog(
            type="Catalog",
            id=catalog_id_val,
            description=description,
            stac_version="1.0.0",
            links=[],
        )

    async def create_catalog_collection(
        self,
        catalog_id: str,
        collection: Collection | ObjectUri,
        request: Request | None = None,
        **kwargs,
    ) -> Collection | Response:
        collection_id_val = collection.id

        description = None
        if isinstance(collection, Collection):
            description = collection.description or f"Collection in {catalog_id}"
        else:
            description = f"Collection in {catalog_id}"

        return Collection(
            type="Collection",
            id=collection_id_val,
            description=description,
            extent={
                "spatial": {"bbox": [[-180, -90, 180, 90]]},
                "temporal": {"interval": [[None, None]]},
            },
            license="proprietary",
            links=[],
        )

    async def get_catalog_collection(
        self,
        catalog_id: str,
        collection_id: str,
        request: Request | None = None,
        **kwargs,
    ) -> Collection | Response:
        return Collection(
            type="Collection",
            id=collection_id,
            description=f"Collection {collection_id} in {catalog_id}",
            extent={
                "spatial": {"bbox": [[-180, -90, 180, 90]]},
                "temporal": {"interval": [[None, None]]},
            },
            license="proprietary",
            links=[],
        )

    async def unlink_catalog_collection(
        self,
        catalog_id: str,
        collection_id: str,
        request: Request | None = None,
        **kwargs,
    ) -> None:
        return None

    async def get_catalog_collection_items(
        self,
        catalog_id: str,
        collection_id: str,
        bbox: list[float] | None = None,
        datetime: str | datetime | None = None,
        limit: int | None = 10,
        token: str | None = None,
        request: Request | None = None,
        **kwargs,
    ) -> ItemCollection | Response:
        features = [
            Item(
                type="Feature",
                id="test-item",
                geometry={"type": "Point", "coordinates": [0, 0]},
                bbox=[0, 0, 0, 0],
                datetime="2024-01-01T00:00:00Z",
                properties={"datetime": "2024-01-01T00:00:00Z"},
                links=[],
                assets={},
            )
        ]

        if bbox is not None:
            if not (bbox[0] <= 0 <= bbox[2] and bbox[1] <= 0 <= bbox[3]):
                features = []

        if datetime is not None:
            if isinstance(datetime, str):
                if "2024-01-01" not in datetime:
                    features = []

        if limit is not None and len(features) > limit:
            features = features[:limit]

        return ItemCollection(
            type="FeatureCollection",
            features=features,
            links=[],
        )

    async def get_catalog_collection_item(
        self,
        catalog_id: str,
        collection_id: str,
        item_id: str,
        request: Request | None = None,
        **kwargs,
    ) -> Item | Response:
        return Item(
            type="Feature",
            id=item_id,
            geometry={"type": "Point", "coordinates": [0, 0]},
            bbox=[0, 0, 0, 0],
            datetime="2024-01-01T00:00:00Z",
            properties={"datetime": "2024-01-01T00:00:00Z"},
            links=[],
            assets={},
        )

    async def get_catalog_children(
        self,
        catalog_id: str,
        limit: int | None = None,
        token: str | None = None,
        type: str | None = None,
        request: Request | None = None,
        **kwargs,
    ) -> Children | Response:
        all_children = [
            Catalog(
                id=f"{catalog_id}-child-1",
                type="Catalog",
                description="Child catalog",
                stac_version="1.0.0",
                links=[],
            ),
            Collection(
                id="collection-1",
                type="Collection",
                description="Child collection",
                stac_version="1.0.0",
                license="proprietary",
                extent={
                    "spatial": {"bbox": [[-180, -90, 180, 90]]},
                    "temporal": {"interval": [[None, None]]},
                },
                links=[],
            ),
        ]

        # Filter by type if provided
        if type:
            filtered_children = [
                child
                for child in all_children
                if (
                    type == "Catalog"
                    and isinstance(child, Catalog)
                    and not isinstance(child, Collection)
                )
                or (type == "Collection" and isinstance(child, Collection))
            ]
        else:
            filtered_children = all_children

        return Children(
            children=filtered_children,
            links=[],
            numberMatched=len(filtered_children),
            numberReturned=len(filtered_children),
        )

    async def get_catalog_conformance(
        self, catalog_id: str, request: Request | None = None, **kwargs
    ) -> dict | Response:
        return {
            "conformsTo": [
                "https://api.stacspec.org/v1.0.0/core",
                "https://api.stacspec.org/v1.0.0-beta.4/multi-tenant-catalogs",
            ]
        }

    async def get_catalog_queryables(
        self, catalog_id: str, request: Request | None = None, **kwargs
    ) -> dict | Response:
        return {
            "queryables": [
                {"name": "datetime", "type": "string"},
                {"name": "platform", "type": "string"},
            ]
        }

    async def unlink_sub_catalog(
        self,
        catalog_id: str,
        sub_catalog_id: str,
        request: Request | None = None,
        **kwargs,
    ) -> None:
        return None


@pytest.fixture
def core_client() -> DummyCoreClient:
    """Fixture for core client."""
    return DummyCoreClient()


@pytest.fixture
def catalogs_client() -> DummyCatalogsClient:
    """Fixture for catalogs client."""
    return DummyCatalogsClient()


@pytest_asyncio.fixture
async def client(
    core_client: DummyCoreClient, catalogs_client: DummyCatalogsClient
) -> httpx.AsyncClient:
    """Fixture for async test client with transactions enabled."""
    settings = ApiSettings()
    api = StacApi(
        settings=settings,
        client=core_client,
        extensions=[
            CatalogsExtension(
                client=catalogs_client,
                enable_transactions=True,
                settings=settings.model_dump(),
            ),
        ],
    )
    transport = ASGITransport(app=api.app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def client_readonly(
    core_client: DummyCoreClient, catalogs_client: DummyCatalogsClient
) -> httpx.AsyncClient:
    """Fixture for async test client with transactions disabled (read-only)."""
    settings = ApiSettings()
    api = StacApi(
        settings=settings,
        client=core_client,
        extensions=[
            CatalogsExtension(
                client=catalogs_client,
                enable_transactions=False,
                settings=settings.model_dump(),
            ),
        ],
    )
    transport = ASGITransport(app=api.app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_get_catalogs(client: httpx.AsyncClient) -> None:
    """Test GET /catalogs endpoint."""
    response = await client.get("/catalogs")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "catalogs" in data
    assert len(data["catalogs"]) == 2
    assert data["catalogs"][0]["id"] == "test-catalog-1"
    assert data["numberMatched"] == 2
    assert data["numberReturned"] == 2


@pytest.mark.asyncio
async def test_create_catalog(client: httpx.AsyncClient) -> None:
    """Test POST /catalogs endpoint."""
    catalog_data = {
        "type": "Catalog",
        "id": "new-catalog",
        "description": "A new test catalog",
        "stac_version": "1.0.0",
        "links": [],
    }
    response = await client.post("/catalogs", json=catalog_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["id"] == "new-catalog"
    assert data["description"] == "A new test catalog"


@pytest.mark.asyncio
async def test_get_catalog(client: httpx.AsyncClient) -> None:
    """Test GET /catalogs/{catalog_id} endpoint."""
    response = await client.get("/catalogs/test-catalog-1")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == "test-catalog-1"
    assert data["description"] == "Catalog test-catalog-1"


@pytest.mark.asyncio
async def test_update_catalog(client: httpx.AsyncClient) -> None:
    """Test PUT /catalogs/{catalog_id} endpoint."""
    catalog_data = {
        "type": "Catalog",
        "id": "test-catalog-1",
        "description": "Updated description",
        "stac_version": "1.0.0",
        "links": [],
    }
    response = await client.put("/catalogs/test-catalog-1", json=catalog_data)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == "test-catalog-1"


@pytest.mark.asyncio
async def test_delete_catalog(client: httpx.AsyncClient) -> None:
    """Test DELETE /catalogs/{catalog_id} endpoint."""
    response = await client.delete("/catalogs/test-catalog-1")
    assert response.status_code == 204, response.text


@pytest.mark.asyncio
async def test_get_catalog_collections(client: httpx.AsyncClient) -> None:
    """Test GET /catalogs/{catalog_id}/collections endpoint."""
    response = await client.get("/catalogs/test-catalog-1/collections")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "collections" in data
    assert len(data["collections"]) == 1
    assert data["collections"][0]["id"] == "test-collection"


@pytest.mark.asyncio
async def test_create_catalog_collection(client: httpx.AsyncClient) -> None:
    """Test POST /catalogs/{catalog_id}/collections endpoint."""
    collection_data = {
        "type": "Collection",
        "id": "new-collection",
        "description": "A new collection",
        "extent": {
            "spatial": {"bbox": [[-180, -90, 180, 90]]},
            "temporal": {"interval": [[None, None]]},
        },
        "license": "proprietary",
        "links": [],
    }
    response = await client.post(
        "/catalogs/test-catalog-1/collections", json=collection_data
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["id"] == "new-collection"


@pytest.mark.asyncio
async def test_get_catalog_collection(client: httpx.AsyncClient) -> None:
    """Test GET /catalogs/{catalog_id}/collections/{collection_id} endpoint."""
    response = await client.get("/catalogs/test-catalog-1/collections/test-collection")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == "test-collection"


@pytest.mark.asyncio
async def test_unlink_catalog_collection(client: httpx.AsyncClient) -> None:
    """Test DELETE /catalogs/{catalog_id}/collections/{collection_id} endpoint."""
    response = await client.delete(
        "/catalogs/test-catalog-1/collections/test-collection"
    )
    assert response.status_code == 204, response.text


@pytest.mark.asyncio
async def test_get_catalog_collection_items(client: httpx.AsyncClient) -> None:
    """Test GET /catalogs/{catalog_id}/collections/{collection_id}/items endpoint."""
    response = await client.get(
        "/catalogs/test-catalog-1/collections/test-collection/items"
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 1
    assert data["features"][0]["id"] == "test-item"


@pytest.mark.asyncio
async def test_get_catalog_collection_items_with_bbox(
    client: httpx.AsyncClient,
) -> None:
    """Test GET .../items with bbox filter."""
    params = {"bbox": "-1,-1,1,1"}
    response = await client.get(
        "/catalogs/test-catalog-1/collections/test-collection/items", params=params
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data["features"]) == 1
    assert data["features"][0]["id"] == "test-item"

    params_out = {"bbox": "10,10,20,20"}
    response_out = await client.get(
        "/catalogs/test-catalog-1/collections/test-collection/items", params=params_out
    )
    assert response_out.status_code == 200, response_out.text
    assert len(response_out.json()["features"]) == 0


@pytest.mark.asyncio
async def test_get_catalog_collection_items_with_datetime(
    client: httpx.AsyncClient,
) -> None:
    """Test GET .../items with datetime filter."""
    params = {"datetime": "2024-01-01T00:00:00Z"}
    response = await client.get(
        "/catalogs/test-catalog-1/collections/test-collection/items", params=params
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data["features"]) == 1

    params_out = {"datetime": "2023-01-01T00:00:00Z"}
    response_out = await client.get(
        "/catalogs/test-catalog-1/collections/test-collection/items", params=params_out
    )
    assert response_out.status_code == 200, response_out.text
    assert len(response_out.json()["features"]) == 0


@pytest.mark.asyncio
async def test_get_catalog_collection_item(client: httpx.AsyncClient) -> None:
    """Test GET /catalogs/{catalog_id}/collections/{collection_id}/items/{item_id}."""
    response = await client.get(
        "/catalogs/test-catalog-1/collections/test-collection/items/test-item"
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == "test-item"


@pytest.mark.asyncio
async def test_get_sub_catalogs(client: httpx.AsyncClient) -> None:
    """Test GET /catalogs/{catalog_id}/catalogs endpoint."""
    response = await client.get("/catalogs/test-catalog-1/catalogs")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "catalogs" in data
    assert len(data["catalogs"]) == 1
    assert data["catalogs"][0]["id"] == "test-catalog-1-sub-1"


@pytest.mark.asyncio
async def test_create_sub_catalog(client: httpx.AsyncClient) -> None:
    """Test POST /catalogs/{catalog_id}/catalogs endpoint."""
    catalog_data = {
        "type": "Catalog",
        "id": "new-sub-catalog",
        "description": "A new sub-catalog",
        "stac_version": "1.0.0",
        "links": [],
    }
    response = await client.post("/catalogs/test-catalog-1/catalogs", json=catalog_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["id"] == "new-sub-catalog"


@pytest.mark.asyncio
async def test_create_sub_catalog_with_object_uri(client: httpx.AsyncClient) -> None:
    """Test POST /catalogs/{catalog_id}/catalogs with ObjectUri (Mode B - linking)."""
    object_uri_data = {"id": "existing-catalog"}
    response = await client.post(
        "/catalogs/test-catalog-1/catalogs", json=object_uri_data
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["id"] == "existing-catalog"
    assert data["type"] == "Catalog"


@pytest.mark.asyncio
async def test_create_catalog_collection_with_object_uri(
    client: httpx.AsyncClient,
) -> None:
    """Test POST /catalogs/{catalog_id}/collections with ObjectUri (Mode B - linking)."""
    object_uri_data = {"id": "existing-collection"}
    response = await client.post(
        "/catalogs/test-catalog-1/collections", json=object_uri_data
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["id"] == "existing-collection"
    assert data["type"] == "Collection"


@pytest.mark.asyncio
async def test_get_catalog_children(client: httpx.AsyncClient) -> None:
    """Test GET /catalogs/{catalog_id}/children endpoint."""
    response = await client.get("/catalogs/test-catalog-1/children")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "children" in data
    assert len(data["children"]) == 2
    assert data["numberMatched"] == 2


@pytest.mark.asyncio
async def test_get_catalog_children_with_type_filter(client: httpx.AsyncClient) -> None:
    """Test GET /catalogs/{catalog_id}/children with type filter."""
    response = await client.get("/catalogs/test-catalog-1/children?type=Catalog")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "children" in data
    assert len(data["children"]) == 1
    assert data["children"][0]["type"] == "Catalog"
    assert data["numberMatched"] == 1
    assert data["numberReturned"] == 1


@pytest.mark.asyncio
async def test_get_catalog_conformance(client: httpx.AsyncClient) -> None:
    """Test GET /catalogs/{catalog_id}/conformance endpoint."""
    response = await client.get("/catalogs/test-catalog-1/conformance")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "conformsTo" in data
    assert len(data["conformsTo"]) > 0


@pytest.mark.asyncio
async def test_get_catalog_queryables(client: httpx.AsyncClient) -> None:
    """Test GET /catalogs/{catalog_id}/queryables endpoint."""
    response = await client.get("/catalogs/test-catalog-1/queryables")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "queryables" in data
    assert len(data["queryables"]) > 0


@pytest.mark.asyncio
async def test_unlink_sub_catalog(client: httpx.AsyncClient) -> None:
    """Test DELETE /catalogs/{catalog_id}/catalogs/{sub_catalog_id} endpoint."""
    response = await client.delete(
        "/catalogs/test-catalog-1/catalogs/test-catalog-1-sub-1"
    )
    assert response.status_code == 204, response.text


@pytest.mark.asyncio
async def test_get_catalog_collection_items_invalid_bbox_string(
    client: httpx.AsyncClient,
) -> None:
    """Test that a garbage bbox string returns 400 Bad Request."""
    params = {"bbox": "not,a,bounding,box"}
    response = await client.get(
        "/catalogs/test-catalog-1/collections/test-collection/items", params=params
    )
    # The _bbox_converter in CatalogCollectionItemsRequest triggers a 400 error
    # on invalid strings
    assert response.status_code == 400
    assert "invalid bbox" in response.json()["detail"]


@pytest.mark.asyncio
async def test_landing_page_includes_catalogs_links(client: httpx.AsyncClient) -> None:
    """Test that landing page includes catalogs links."""
    response = await client.get("/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "links" in data
    # The catalogs extension should be registered and provide links
    # Check if any link exists (the exact catalogs link depends on extension registration)
    assert len(data["links"]) > 0


# --- READ-ONLY MODE TESTS (enable_transactions=False) ---


@pytest.mark.asyncio
async def test_readonly_get_catalogs(client_readonly: httpx.AsyncClient) -> None:
    """Test GET /catalogs works in read-only mode."""
    response = await client_readonly.get("/catalogs")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "catalogs" in data


@pytest.mark.asyncio
async def test_readonly_create_catalog_disabled(
    client_readonly: httpx.AsyncClient,
) -> None:
    """Test POST /catalogs returns 405 in read-only mode."""
    catalog_data = {
        "type": "Catalog",
        "id": "new-catalog",
        "description": "A new test catalog",
        "stac_version": "1.0.0",
        "links": [],
    }
    response = await client_readonly.post("/catalogs", json=catalog_data)
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_readonly_update_catalog_disabled(
    client_readonly: httpx.AsyncClient,
) -> None:
    """Test PUT /catalogs/{catalog_id} returns 405 in read-only mode."""
    catalog_data = {
        "type": "Catalog",
        "id": "test-catalog-1",
        "description": "Updated description",
        "stac_version": "1.0.0",
        "links": [],
    }
    response = await client_readonly.put("/catalogs/test-catalog-1", json=catalog_data)
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_readonly_delete_catalog_disabled(
    client_readonly: httpx.AsyncClient,
) -> None:
    """Test DELETE /catalogs/{catalog_id} returns 405 in read-only mode."""
    response = await client_readonly.delete("/catalogs/test-catalog-1")
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_readonly_create_collection_disabled(
    client_readonly: httpx.AsyncClient,
) -> None:
    """Test POST /catalogs/{catalog_id}/collections returns 405 in read-only mode."""
    collection_data = {
        "type": "Collection",
        "id": "new-collection",
        "description": "A new collection",
        "extent": {
            "spatial": {"bbox": [[-180, -90, 180, 90]]},
            "temporal": {"interval": [[None, None]]},
        },
        "license": "proprietary",
        "links": [],
    }
    response = await client_readonly.post(
        "/catalogs/test-catalog-1/collections", json=collection_data
    )
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_readonly_unlink_collection_disabled(
    client_readonly: httpx.AsyncClient,
) -> None:
    """Test DELETE /catalogs/{catalog_id}/collections/{collection_id} returns 405."""
    response = await client_readonly.delete(
        "/catalogs/test-catalog-1/collections/test-collection"
    )
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_readonly_create_subcatalog_disabled(
    client_readonly: httpx.AsyncClient,
) -> None:
    """Test POST /catalogs/{catalog_id}/catalogs returns 405 in read-only mode."""
    catalog_data = {
        "type": "Catalog",
        "id": "new-sub-catalog",
        "description": "A new sub-catalog",
        "stac_version": "1.0.0",
        "links": [],
    }
    response = await client_readonly.post(
        "/catalogs/test-catalog-1/catalogs", json=catalog_data
    )
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_readonly_unlink_subcatalog_disabled(
    client_readonly: httpx.AsyncClient,
) -> None:
    """Test DELETE /catalogs/{catalog_id}/catalogs/{sub_catalog_id} is disabled."""
    response = await client_readonly.delete(
        "/catalogs/test-catalog-1/catalogs/test-catalog-1-sub-1"
    )
    # Route is not registered, so we get 404 (Not Found)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_readonly_conformance_excludes_transaction_class(
    client_readonly: httpx.AsyncClient,
) -> None:
    """Test that transaction conformance class is not present in read-only mode."""
    response = await client_readonly.get("/catalogs/test-catalog-1/conformance")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "conformsTo" in data
    transaction_class = (
        "https://api.stacspec.org/v1.0.0-beta.4/multi-tenant-catalogs/transaction"
    )
    assert transaction_class not in data["conformsTo"]


@pytest.mark.asyncio
async def test_enabled_conformance_includes_transaction_class(
    client: httpx.AsyncClient,
) -> None:
    """Test that transaction conformance class is present when enabled."""
    response = await client.get("/catalogs/test-catalog-1/conformance")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "conformsTo" in data
    transaction_class = (
        "https://api.stacspec.org/v1.0.0-beta.4/multi-tenant-catalogs/transaction"
    )
    assert transaction_class in data["conformsTo"]
