"""Multi-Tenant Catalogs Extensions."""

from typing import Type

import attr
from fastapi import APIRouter, Body, FastAPI, Path
from fastapi.responses import JSONResponse
from stac_fastapi.api.routes import create_async_endpoint
from stac_fastapi.types.extension import ApiExtension
from stac_fastapi.types.search import APIRequest
from stac_pydantic.api.collections import Collections
from stac_pydantic.catalog import Catalog
from stac_pydantic.collection import Collection
from stac_pydantic.item import Item
from stac_pydantic.item_collection import ItemCollection
from starlette.responses import Response
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from typing_extensions import Annotated

from .client import AsyncBaseCatalogsClient, AsyncCatalogsSearchClient
from .types import (
    CatalogChildrenRequest,
    CatalogCollectionItemsRequest,
    CatalogCollectionItemUri,
    CatalogCollectionsRequest,
    CatalogCollectionUri,
    Catalogs,
    CatalogsGetRequest,
    CatalogsUri,
    Children,
    CreateCatalogCollectionRequest,
    CreateCatalogRequest,
    CreateSubCatalogRequest,
    SubCatalogsRequest,
    UnlinkSubCatalogRequest,
    UpdateCatalogCollectionRequest,
    UpdateCatalogRequest,
)

# Conformance Classes
CATALOGS_CORE_CONFORMANCE = [
    "https://api.stacspec.org/v1.0.0/core",
    "https://api.stacspec.org/v1.0.0-rc.2/multi-tenant-catalogs",
    "https://api.stacspec.org/v1.0.0-rc.2/children",
    "https://api.stacspec.org/v1.0.0-rc.2/children#type-filter",
]

CATALOGS_TRANSACTION_CONFORMANCE = [
    "https://api.stacspec.org/v1.0.0-rc.2/multi-tenant-catalogs/transaction"
]

CATALOGS_SEARCH_CONFORMANCE = [
    "https://api.stacspec.org/v1.0.0/item-search",
    "https://api.stacspec.org/v1.0.0-rc.2/multi-tenant-catalogs/search",
]


@attr.s
class CatalogsExtension(ApiExtension):
    """Catalogs Extension (Core / Read-Only).

    The Catalogs extension provides discovery endpoints for a Multi-Tenant STAC
    architecture. It introduces a `/catalogs` registry to support recursive
    catalog hierarchies and poly-hierarchy (where collections or catalogs can
    have multiple parents).

    This class strictly implements the read-only discovery operations. For
    creating, updating, or managing the hierarchy, see `CatalogsTransactionExtension`.

    For normative rules regarding Link Strategy, Contextual Navigation, and
    HATEOAS link generation (e.g., `rel="parent"`, `rel="canonical"`), please
    refer to the Multi-Tenant Catalogs specification.

    Attributes:
        client: A client implementing the catalogs extension pattern.
        settings: Extension settings.
        conformance_classes: List of conformance classes for this extension.
        router: FastAPI router for the extension endpoints.
        response_class: Response class for the extension.
        hide_alternate_parents: If True, do not advertise rel="related" links to
            alternative parents in poly-hierarchy. Useful for multi-tenant deployments
            to prevent information leakage about other tenants.
    """

    client: AsyncBaseCatalogsClient = attr.ib(kw_only=True)
    settings: dict = attr.ib(default=attr.Factory(dict), kw_only=True)
    conformance_classes: list[str] = attr.ib(
        default=attr.Factory(lambda: CATALOGS_CORE_CONFORMANCE.copy()), kw_only=True
    )
    router: APIRouter = attr.ib(factory=APIRouter, kw_only=True)
    response_class: Type[Response] = attr.ib(default=JSONResponse, kw_only=True)
    hide_alternate_parents: bool = attr.ib(default=False, kw_only=True)

    def register(self, app: FastAPI) -> None:
        """Register the extension with a FastAPI application.

        Args:
            app: target FastAPI application.
        """
        self.router.prefix = app.state.router_prefix

        # Share conformance classes via app.state registry
        if not hasattr(app.state, "catalogs_conformance_classes"):
            app.state.catalogs_conformance_classes = set()
        app.state.catalogs_conformance_classes.update(self.conformance_classes)

        # Store hide_alternate_parents flag for client access
        app.state.catalogs_hide_alternate_parents = self.hide_alternate_parents

        # GET /catalogs
        self.router.add_api_route(
            name="Get All Catalogs",
            path="/catalogs",
            methods=["GET"],
            endpoint=create_async_endpoint(
                self.client.get_catalogs, CatalogsGetRequest
            ),
            response_model=Catalogs
            if self.settings.get("enable_response_models", True)
            else None,
            response_class=self.response_class,
            summary="Get All Catalogs",
            description="Returns a list of all catalogs in the database.",
            tags=["Catalogs"],
        )

        # GET /catalogs/{catalog_id}
        self.router.add_api_route(
            name="Get Catalog",
            path="/catalogs/{catalog_id}",
            methods=["GET"],
            endpoint=create_async_endpoint(self.client.get_catalog, CatalogsUri),
            response_model=Catalog
            if self.settings.get("enable_response_models", True)
            else None,
            response_class=self.response_class,
            summary="Get Catalog",
            description="Get a specific STAC catalog by ID.",
            tags=["Catalogs"],
        )

        # GET /catalogs/{catalog_id}/collections
        self.router.add_api_route(
            name="Get Catalog Collections",
            path="/catalogs/{catalog_id}/collections",
            methods=["GET"],
            endpoint=create_async_endpoint(
                self.client.get_catalog_collections, CatalogCollectionsRequest
            ),
            response_model=Collections
            if self.settings.get("enable_response_models", True)
            else None,
            response_class=self.response_class,
            summary="Get Catalog Collections",
            description="Get collections linked from a specific catalog.",
            tags=["Catalogs"],
        )

        # GET /catalogs/{catalog_id}/collections/{collection_id}
        self.router.add_api_route(
            name="Get Catalog Collection",
            path="/catalogs/{catalog_id}/collections/{collection_id}",
            methods=["GET"],
            endpoint=create_async_endpoint(
                self.client.get_catalog_collection, CatalogCollectionUri
            ),
            response_model=Collection
            if self.settings.get("enable_response_models", True)
            else None,
            response_class=self.response_class,
            summary="Get Catalog Collection",
            description="Get a specific collection from a catalog.",
            tags=["Catalogs"],
        )

        # GET /catalogs/{catalog_id}/collections/{collection_id}/items
        self.router.add_api_route(
            name="Get Catalog Collection Items",
            path="/catalogs/{catalog_id}/collections/{collection_id}/items",
            methods=["GET"],
            endpoint=create_async_endpoint(
                self.client.get_catalog_collection_items, CatalogCollectionItemsRequest
            ),
            response_model=ItemCollection
            if self.settings.get("enable_response_models", True)
            else None,
            response_class=self.response_class,
            summary="Get Catalog Collection Items",
            description="Get items from a collection in a catalog.",
            tags=["Catalogs"],
        )

        # GET /catalogs/{catalog_id}/collections/{collection_id}/items/{item_id}
        self.router.add_api_route(
            name="Get Catalog Collection Item",
            path="/catalogs/{catalog_id}/collections/{collection_id}/items/{item_id}",
            methods=["GET"],
            endpoint=create_async_endpoint(
                self.client.get_catalog_collection_item, CatalogCollectionItemUri
            ),
            response_model=Item
            if self.settings.get("enable_response_models", True)
            else None,
            response_class=self.response_class,
            summary="Get Catalog Collection Item",
            description="Get a specific item from a collection in a catalog.",
            tags=["Catalogs"],
        )

        # GET /catalogs/{catalog_id}/catalogs
        self.router.add_api_route(
            name="Get Catalog Sub-Catalogs",
            path="/catalogs/{catalog_id}/catalogs",
            methods=["GET"],
            endpoint=create_async_endpoint(
                self.client.get_sub_catalogs, SubCatalogsRequest
            ),
            response_model=Catalogs
            if self.settings.get("enable_response_models", True)
            else None,
            response_class=self.response_class,
            summary="Get Catalog Sub-Catalogs",
            description="Get sub-catalogs linked from a specific catalog.",
            tags=["Catalogs"],
        )

        # GET /catalogs/{catalog_id}/children
        self.router.add_api_route(
            name="Get Catalog Children",
            path="/catalogs/{catalog_id}/children",
            methods=["GET"],
            endpoint=create_async_endpoint(
                self.client.get_catalog_children, CatalogChildrenRequest
            ),
            response_model=Children
            if self.settings.get("enable_response_models", True)
            else None,
            response_class=self.response_class,
            summary="Get Catalog Children",
            description=(
                "Retrieve all children (Catalogs and Collections) of this catalog."
            ),
            tags=["Catalogs"],
        )

        # GET /catalogs/{catalog_id}/conformance
        self.router.add_api_route(
            name="Get Catalog Conformance",
            path="/catalogs/{catalog_id}/conformance",
            methods=["GET"],
            endpoint=create_async_endpoint(self._get_catalog_conformance, CatalogsUri),
            response_class=self.response_class,
            summary="Get Catalog Conformance",
            description="Get conformance classes specific to this sub-catalog.",
            tags=["Catalogs"],
            responses={
                HTTP_200_OK: {"description": "Conformance classes for the catalog"}
            },
        )

        # GET /catalogs/{catalog_id}/queryables
        self.router.add_api_route(
            name="Get Catalog Queryables",
            path="/catalogs/{catalog_id}/queryables",
            methods=["GET"],
            endpoint=create_async_endpoint(
                self.client.get_catalog_queryables, CatalogsUri
            ),
            response_class=self.response_class,
            summary="Get Catalog Queryables",
            description=(
                "Get queryable fields available for filtering "
                "in this sub-catalog (Filter Extension)."
            ),
            tags=["Catalogs"],
            responses={
                HTTP_200_OK: {"description": "Queryable fields for the catalog"}
            },
        )

        app.include_router(self.router, tags=["Catalogs"])

    async def _get_catalog_conformance(
        self, catalog_id: str, request=None, **kwargs
    ) -> dict | Response:
        """Merge client response with extension conformance classes.

        Args:
            catalog_id: ID of the catalog to fetch conformance for.
            request: The incoming FastAPI request.

        Returns:
            Dictionary containing merged conformance classes.
        """
        result = await self.client.get_catalog_conformance(
            catalog_id=catalog_id, request=request
        )
        if isinstance(result, dict):
            conforms = result.get("conformsTo", [])
            # Dynamically fetch ALL catalog conformance classes from app.state
            if request and hasattr(request.app.state, "catalogs_conformance_classes"):
                conforms.extend(request.app.state.catalogs_conformance_classes)
            else:
                conforms.extend(self.conformance_classes)
            result["conformsTo"] = list(set(conforms))
        return result


@attr.s
class CatalogsTransactionExtension(ApiExtension):
    """Catalogs Transaction Extension (Management / Write).

    The Catalogs Transaction extension provides the `POST`, `PUT`, and `DELETE`
    endpoints required to manage a Multi-Tenant STAC catalog registry and its
    hierarchical relationships.

    This extension follows a "Safety-First" policy: deletions via these endpoints
    typically unlink resources (preserving data) rather than destroying them.

    For normative rules regarding Adoption logic, Cycle Prevention, and structural
    validation, please refer to the Multi-Tenant Catalogs specification.

    Attributes:
        client: An `AsyncBaseCatalogsClient` instance implementing the
        transactional endpoints.
        settings: Application settings dictionary.
        conformance_classes: List of transactional conformance classes for this extension.
        router: FastAPI router for the extension endpoints.
        response_class: Response class for the extension (defaults to JSONResponse).
    """

    client: AsyncBaseCatalogsClient = attr.ib(kw_only=True)
    settings: dict = attr.ib(default=attr.Factory(dict), kw_only=True)
    conformance_classes: list[str] = attr.ib(
        default=attr.Factory(lambda: CATALOGS_TRANSACTION_CONFORMANCE.copy()),
        kw_only=True,
    )
    router: APIRouter = attr.ib(factory=APIRouter, kw_only=True)
    response_class: Type[Response] = attr.ib(default=JSONResponse, kw_only=True)

    def register(self, app: FastAPI) -> None:
        """Register the transactional extension with a FastAPI application.

        Args:
            app: target FastAPI application.
        """
        self.router.prefix = app.state.router_prefix

        # Inject transaction conformance into the shared catalog state
        if not hasattr(app.state, "catalogs_conformance_classes"):
            app.state.catalogs_conformance_classes = set()
        app.state.catalogs_conformance_classes.update(self.conformance_classes)

        # POST /catalogs
        self.router.add_api_route(
            name="Create Catalog",
            path="/catalogs",
            methods=["POST"],
            status_code=HTTP_201_CREATED,
            endpoint=create_async_endpoint(
                self.client.create_catalog, CreateCatalogRequest
            ),
            response_model=Catalog
            if self.settings.get("enable_response_models", True)
            else None,
            response_class=self.response_class,
            summary="Create Catalog",
            description="Create a new STAC catalog.",
            tags=["Catalogs"],
        )

        # PUT /catalogs/{catalog_id}
        self.router.add_api_route(
            name="Update Catalog",
            path="/catalogs/{catalog_id}",
            methods=["PUT"],
            endpoint=create_async_endpoint(
                self.client.update_catalog, UpdateCatalogRequest
            ),
            response_model=Catalog
            if self.settings.get("enable_response_models", True)
            else None,
            response_class=self.response_class,
            summary="Update Catalog",
            description="Update an existing STAC catalog.",
            tags=["Catalogs"],
        )

        # DELETE /catalogs/{catalog_id}
        self.router.add_api_route(
            name="Delete Catalog",
            path="/catalogs/{catalog_id}",
            methods=["DELETE"],
            status_code=HTTP_204_NO_CONTENT,
            endpoint=create_async_endpoint(self.client.delete_catalog, CatalogsUri),
            response_class=self.response_class,
            summary="Delete Catalog",
            description="Delete a catalog (Unlinks children and preserves data).",
            tags=["Catalogs"],
        )

        # POST /catalogs/{catalog_id}/collections
        self.router.add_api_route(
            name="Create Catalog Collection",
            path="/catalogs/{catalog_id}/collections",
            methods=["POST"],
            status_code=HTTP_201_CREATED,
            endpoint=create_async_endpoint(
                self.client.create_catalog_collection, CreateCatalogCollectionRequest
            ),
            response_model=Collection
            if self.settings.get("enable_response_models", True)
            else None,
            response_class=self.response_class,
            summary="Create Catalog Collection",
            description=(
                "Create a new collection or link an existing one to this catalog."
            ),
            tags=["Catalogs"],
        )

        # PUT /catalogs/{catalog_id}/collections/{collection_id}
        self.router.add_api_route(
            name="Update Catalog Collection",
            path="/catalogs/{catalog_id}/collections/{collection_id}",
            methods=["PUT"],
            status_code=HTTP_200_OK,
            endpoint=create_async_endpoint(
                self.client.update_catalog_collection, UpdateCatalogCollectionRequest
            ),
            response_model=Collection
            if self.settings.get("enable_response_models", True)
            else None,
            response_class=self.response_class,
            summary="Update Catalog Collection",
            description=(
                "Update collection metadata within a catalog context. "
                "Preserves structural links to maintain poly-hierarchy."
            ),
            tags=["Catalogs"],
        )

        # DELETE /catalogs/{catalog_id}/collections/{collection_id}
        self.router.add_api_route(
            name="Unlink Collection from Catalog",
            path="/catalogs/{catalog_id}/collections/{collection_id}",
            methods=["DELETE"],
            status_code=HTTP_204_NO_CONTENT,
            endpoint=create_async_endpoint(
                self.client.unlink_catalog_collection, CatalogCollectionUri
            ),
            response_class=self.response_class,
            summary="Unlink Collection from Catalog",
            description=(
                "Removes the link between catalog and collection. Data is NOT deleted."
            ),
            tags=["Catalogs"],
        )

        # POST /catalogs/{catalog_id}/catalogs
        self.router.add_api_route(
            name="Create Catalog Sub-Catalog",
            path="/catalogs/{catalog_id}/catalogs",
            methods=["POST"],
            status_code=HTTP_201_CREATED,
            endpoint=create_async_endpoint(
                self.client.create_sub_catalog, CreateSubCatalogRequest
            ),
            response_model=Catalog
            if self.settings.get("enable_response_models", True)
            else None,
            response_class=self.response_class,
            summary="Create Catalog Sub-Catalog",
            description=(
                "Create a new sub-catalog or link an existing catalog to this parent."
            ),
            tags=["Catalogs"],
        )

        # DELETE /catalogs/{catalog_id}/catalogs/{sub_catalog_id}
        self.router.add_api_route(
            name="Unlink Sub-Catalog",
            path="/catalogs/{catalog_id}/catalogs/{sub_catalog_id}",
            methods=["DELETE"],
            status_code=HTTP_204_NO_CONTENT,
            endpoint=create_async_endpoint(
                self.client.unlink_sub_catalog, UnlinkSubCatalogRequest
            ),
            response_class=self.response_class,
            summary="Unlink Sub-Catalog",
            description=(
                "Unlink a sub-catalog from its parent. Does not delete the catalog."
            ),
            tags=["Catalogs"],
        )

        app.include_router(self.router, tags=["Catalogs"])


@attr.s
class CatalogsSearchExtension(ApiExtension):
    """Catalogs Search Extension (Recursive Scoped Search).

    This extension provides the `GET` and `POST` search endpoints for performing
    STAC item searches strictly bounded to a catalog's descendant tree.

    By injecting the dynamic core search request models, this extension automatically
    inherits any features added to the global `/search` endpoint (CQL2, sorting,
    field projection, etc.), ensuring scoped searches are always feature-complete.

    Attributes:
        client: An `AsyncCatalogsSearchClient` instance implementing the search endpoints.
        search_get_request_model: The dynamic GET request model from core stac-fastapi.
        search_post_request_model: The dynamic POST request model from core stac-fastapi.
        settings: Application settings dictionary.
        conformance_classes: List of search conformance classes for this extension.
        router: FastAPI router for the extension endpoints.
        response_class: Response class for the extension.
    """

    client: AsyncCatalogsSearchClient = attr.ib(kw_only=True)
    search_get_request_model: Type[APIRequest] = attr.ib(kw_only=True)
    search_post_request_model: Type[APIRequest] = attr.ib(kw_only=True)
    settings: dict = attr.ib(default=attr.Factory(dict), kw_only=True)
    conformance_classes: list[str] = attr.ib(
        default=attr.Factory(lambda: CATALOGS_SEARCH_CONFORMANCE.copy()), kw_only=True
    )
    router: APIRouter = attr.ib(factory=APIRouter, kw_only=True)
    response_class: Type[Response] = attr.ib(default=JSONResponse, kw_only=True)

    def register(self, app: FastAPI) -> None:
        """Register the search extension with a FastAPI application."""
        self.router.prefix = app.state.router_prefix

        # Inject search conformance into the shared catalog state
        if not hasattr(app.state, "catalogs_conformance_classes"):
            app.state.catalogs_conformance_classes = set()
        app.state.catalogs_conformance_classes.update(self.conformance_classes)

        # Dynamically create request models that inherit both the core STAC search
        # parameters AND the catalog_id path parameter. This ensures scoped searches
        # automatically inherit any features added to the global /search endpoint.
        get_request_model: Type[APIRequest] = self.search_get_request_model
        post_request_model: Type[APIRequest] = self.search_post_request_model

        @attr.s
        class CatalogSearchGetRequest(get_request_model):  # type: ignore
            catalog_id: Annotated[str, Path(description="Catalog ID")] = attr.ib(
                kw_only=True
            )

        @attr.s
        class CatalogSearchPostRequest(APIRequest):
            catalog_id: Annotated[str, Path(description="Catalog ID")] = attr.ib(
                kw_only=True
            )
            search_request: Annotated[post_request_model, Body()] = attr.ib(  # type: ignore
                default=None, kw_only=True
            )

        # GET /catalogs/{catalog_id}/search
        self.router.add_api_route(
            name="Catalog Scoped Search (GET)",
            path="/catalogs/{catalog_id}/search",
            methods=["GET"],
            endpoint=create_async_endpoint(
                self.client.catalog_search_get, CatalogSearchGetRequest
            ),
            response_model=ItemCollection
            if self.settings.get("enable_response_models", True)
            else None,
            response_class=self.response_class,
            summary="Catalog Scoped Search",
            description="Search items in a catalog's descendant tree using query parameters.",
            tags=["Catalogs Search"],
        )

        # POST /catalogs/{catalog_id}/search
        self.router.add_api_route(
            name="Catalog Scoped Search (POST)",
            path="/catalogs/{catalog_id}/search",
            methods=["POST"],
            endpoint=create_async_endpoint(
                self.client.catalog_search_post, CatalogSearchPostRequest
            ),
            response_model=ItemCollection
            if self.settings.get("enable_response_models", True)
            else None,
            response_class=self.response_class,
            summary="Catalog Scoped Search",
            description="Search items in a catalog's descendant tree using a JSON payload.",
            tags=["Catalogs Search"],
        )

        app.include_router(self.router, tags=["Catalogs Search"])
