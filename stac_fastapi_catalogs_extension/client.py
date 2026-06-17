"""Catalogs extension clients.

This module defines the abstract base classes for implementing the Multi-Tenant
Catalogs extension.

For normative rules regarding Poly-Hierarchy, Dynamic Link Generation (HATEOAS),
Contextual Navigation, and Transactional Safety, please refer to the official
Multi-Tenant Catalogs specification.
"""

import abc
from datetime import datetime
from typing import Literal

import attr
from fastapi import Request
from stac_fastapi.types.search import BaseSearchPostRequest
from stac_pydantic.api.collections import Collections
from stac_pydantic.catalog import Catalog
from stac_pydantic.collection import Collection
from stac_pydantic.item import Item
from stac_pydantic.item_collection import ItemCollection
from starlette.responses import Response

from .types import Catalogs, Children, ObjectUri


@attr.s
class AsyncBaseCatalogsClient(abc.ABC):
    """Defines an async pattern for implementing the STAC catalogs extension."""

    @abc.abstractmethod
    async def get_catalogs(
        self,
        limit: int | None = None,
        token: str | None = None,
        request: Request | None = None,
        **kwargs,
    ) -> Catalogs | Response:
        """Get all catalogs with pagination support.

        Args:
            limit: The maximum number of catalogs to return.
            token: Pagination token for the next page of results.
            request: Optional FastAPI request object.

        Returns:
            Catalogs object containing catalogs and pagination links.
        """
        ...

    @abc.abstractmethod
    async def create_catalog(
        self, catalog: Catalog, request: Request | None = None, **kwargs
    ) -> Catalog | Response:
        """Create a new catalog.

        Args:
            catalog: The catalog to create.
            request: Optional FastAPI request object.

        Returns:
            The created catalog.
        """
        ...

    @abc.abstractmethod
    async def get_catalog(
        self, catalog_id: str, request: Request | None = None, **kwargs
    ) -> Catalog | Response:
        """Get a specific catalog by ID.

        For normative rules regarding Link Strategy and HATEOAS relations
        (such as `rel="parent"`, `rel="related"`, and `rel="child"`), see
        the Multi-Tenant Catalogs specification.

        Args:
            catalog_id: The ID of the catalog to retrieve.
            request: Optional FastAPI request object.

        Returns:
            The requested catalog.
        """
        ...

    @abc.abstractmethod
    async def update_catalog(
        self,
        catalog_id: str,
        catalog: Catalog,
        request: Request | None = None,
        **kwargs,
    ) -> Catalog | Response:
        """Update an existing catalog.

        Args:
            catalog_id: The ID of the catalog to update.
            catalog: The updated catalog data.
            request: Optional FastAPI request object.

        Returns:
            The updated catalog.
        """
        ...

    @abc.abstractmethod
    async def delete_catalog(
        self,
        catalog_id: str,
        request: Request | None = None,
        **kwargs,
    ) -> None:
        """Delete a catalog.

        For normative rules regarding the Safety-First architecture and
        Adoption logic during deletion, see the Multi-Tenant Catalogs specification.

        Args:
            catalog_id: The ID of the catalog to delete.
            request: Optional FastAPI request object.
        """
        ...

    @abc.abstractmethod
    async def get_catalog_collections(
        self,
        catalog_id: str,
        limit: int | None = None,
        token: str | None = None,
        request: Request | None = None,
        **kwargs,
    ) -> Collections | Response:
        """Get collections linked from a specific catalog.

        Args:
            catalog_id: The ID of the catalog.
            limit: Maximum number of results to return.
            token: Pagination token for cursor-based pagination.
            request: Optional FastAPI request object.

        Returns:
            Collections object containing collections linked from the catalog.
        """
        ...

    @abc.abstractmethod
    async def get_sub_catalogs(
        self,
        catalog_id: str,
        limit: int | None = None,
        token: str | None = None,
        request: Request | None = None,
        **kwargs,
    ) -> Catalogs | Response:
        """Get all sub-catalogs of a specific catalog with pagination.

        Args:
            catalog_id: The ID of the parent catalog.
            limit: Maximum number of results to return.
            token: Pagination token for cursor-based pagination.
            request: Optional FastAPI request object.

        Returns:
            A Catalogs response containing sub-catalogs with pagination links.
        """
        ...

    @abc.abstractmethod
    async def create_sub_catalog(
        self,
        catalog_id: str,
        catalog: Catalog | ObjectUri,
        request: Request | None = None,
        **kwargs,
    ) -> Catalog | Response:
        """Create a new catalog or link an existing catalog as a sub-catalog.

        The behavior of this endpoint depends on the provided payload.
        For normative rules regarding Creation (Full Body) vs. Linking (Reference Only),
        see the Multi-Tenant Catalogs specification.

        Args:
            catalog_id: The ID of the parent catalog.
            catalog: The catalog to create (Full Catalog) or link (ObjectUri with id).
            request: Optional FastAPI request object.

        Returns:
            The created or linked catalog.
        """
        ...

    @abc.abstractmethod
    async def create_catalog_collection(
        self,
        catalog_id: str,
        collection: Collection | ObjectUri,
        request: Request | None = None,
        **kwargs,
    ) -> Collection | Response:
        """Create a new collection or link an existing one to this catalog.

        The behavior of this endpoint depends on the provided payload.
        For normative rules regarding Creation (Full Body) vs. Linking (Reference Only),
        see the Multi-Tenant Catalogs specification.

        Args:
            catalog_id: The ID of the catalog to link the collection to.
            collection: Create a (Full Collection) or link (ObjectUri with id).
            request: Optional FastAPI request object.

        Returns:
            The created or linked collection.
        """
        ...

    @abc.abstractmethod
    async def get_catalog_collection(
        self,
        catalog_id: str,
        collection_id: str,
        request: Request | None = None,
        **kwargs,
    ) -> Collection | Response:
        """Get a specific collection from a catalog (Scoped Route).

        For normative rules regarding scoped HATEOAS relations (e.g., `rel="canonical"`,
        `rel="duplicate"`, and strict single `rel="parent"` links), see the
        Multi-Tenant Catalogs specification.

        Args:
            catalog_id: The ID of the catalog.
            collection_id: The ID of the collection.
            request: Optional FastAPI request object.

        Returns:
            The requested collection.
        """
        ...

    @abc.abstractmethod
    async def unlink_catalog_collection(
        self,
        catalog_id: str,
        collection_id: str,
        request: Request | None = None,
        **kwargs,
    ) -> None:
        """Unlink a collection from a catalog.

        Removes the link between the catalog and collection.
        For normative rules regarding the Safety-First architecture and
        Adoption logic during unlinking, see the Multi-Tenant Catalogs specification.

        Args:
            catalog_id: The ID of the catalog.
            collection_id: The ID of the collection.
            request: Optional FastAPI request object.
        """
        ...

    @abc.abstractmethod
    async def update_catalog_collection(
        self,
        catalog_id: str,
        collection_id: str,
        collection: Collection,
        request: Request | None = None,
        **kwargs,
    ) -> Collection | Response:
        """Update a collection within a catalog context.

        Updates the metadata (Title, Description, etc.) of the collection
        within the scoped catalog context. This operation preserves the
        collection's structural links (parent_ids) to maintain the poly-hierarchy.

        For normative rules regarding Safety-First architecture during updates,
        see the Multi-Tenant Catalogs specification.

        Args:
            catalog_id: The ID of the catalog.
            collection_id: The ID of the collection.
            collection: The updated collection data.
            request: Optional FastAPI request object.

        Returns:
            The updated collection.
        """
        ...

    @abc.abstractmethod
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
        """Get items from a collection in a catalog with search support.

        Multiple filters are combined using AND logic. If both bbox and datetime
        are provided, only items matching both criteria are returned.

        Args:
            catalog_id: The ID of the catalog.
            collection_id: The ID of the collection.
            bbox: Bounding box to filter items [minx, miny, maxx, maxy].
            datetime: Datetime or datetime range to filter items.
            limit: Maximum number of items to return (default 10).
            token: Pagination token for cursor-based pagination.
            request: Optional FastAPI request object.

        Returns:
            ItemCollection containing items from the collection.
        """
        ...

    @abc.abstractmethod
    async def get_catalog_collection_item(
        self,
        catalog_id: str,
        collection_id: str,
        item_id: str,
        request: Request | None = None,
        **kwargs,
    ) -> Item | Response:
        """Get a specific item from a collection in a catalog.

        Args:
            catalog_id: The ID of the catalog.
            collection_id: The ID of the collection.
            item_id: The ID of the item.
            request: Optional FastAPI request object.

        Returns:
            The requested item.
        """
        ...

    @abc.abstractmethod
    async def get_catalog_children(
        self,
        catalog_id: str,
        limit: int | None = None,
        token: str | None = None,
        type: Literal["Catalog", "Collection"] | None = None,
        request: Request | None = None,
        **kwargs,
    ) -> Children | Response:
        """Get all children (Catalogs and Collections) of a specific catalog.

        Args:
            catalog_id: The ID of the catalog.
            limit: Maximum number of results to return.
            token: Pagination token.
            type: Filter by resource type (Catalog or Collection).
            request: Optional FastAPI request object.

        Returns:
            Children object containing children and pagination links.
        """
        ...

    @abc.abstractmethod
    async def get_catalog_conformance(
        self, catalog_id: str, request: Request | None = None, **kwargs
    ) -> dict | Response:
        """Get conformance classes specific to this sub-catalog.

        Args:
            catalog_id: The ID of the catalog.
            request: Optional FastAPI request object.

        Returns:
            Dictionary containing conformance classes.
        """
        ...

    @abc.abstractmethod
    async def get_catalog_queryables(
        self, catalog_id: str, request: Request | None = None, **kwargs
    ) -> dict | Response:
        """Get queryable fields available for filtering in this sub-catalog.

        Args:
            catalog_id: The ID of the catalog.
            request: Optional FastAPI request object.

        Returns:
            Dictionary containing queryable fields (Filter Extension).
        """
        ...

    @abc.abstractmethod
    async def unlink_sub_catalog(
        self,
        catalog_id: str,
        sub_catalog_id: str,
        request: Request | None = None,
        **kwargs,
    ) -> None:
        """Unlink a sub-catalog from its parent.

        For normative rules regarding the Safety-First architecture and
        Adoption logic during unlinking, see the Multi-Tenant Catalogs specification.

        Args:
            catalog_id: The ID of the parent catalog.
            sub_catalog_id: The ID of the sub-catalog to unlink.
            request: Optional FastAPI request object.
        """
        ...


@attr.s
class BaseCatalogsClient(abc.ABC):
    """Defines a synchronous pattern for implementing the STAC catalogs extension.

    This is the base class for synchronous catalog client implementations.
    For async implementations, use AsyncBaseCatalogsClient instead.
    """

    pass


@attr.s
class AsyncCatalogsSearchClient(abc.ABC):
    """Defines an async pattern for implementing the Scoped Search extension.

    This is an optional interface for backends that support scoped search.
    Implement this interface alongside AsyncBaseCatalogsClient to enable
    the CatalogsSearchExtension.

    This separation respects the Interface Segregation Principle: backends
    that only need basic discovery endpoints don't need to implement search.
    """

    @abc.abstractmethod
    async def get_all_descendant_collections(
        self,
        catalog_id: str,
        request: Request | None = None,
        **kwargs,
    ) -> list[str]:
        """Return all descendant collection IDs for a catalog recursively.

        This method performs a depth-first traversal of the catalog's descendant
        tree to collect all collection IDs. It is used by scoped search to determine
        which collections should be included in the search.

        Args:
            catalog_id: The ID of the catalog to traverse.
            request: Optional FastAPI request object.

        Returns:
            List of all descendant collection IDs.
        """
        ...

    @abc.abstractmethod
    async def catalog_search_get(
        self,
        catalog_id: str,
        collections: list[str] | None = None,
        ids: list[str] | None = None,
        bbox: list[float] | None = None,
        intersects: str | None = None,
        datetime: str | None = None,
        limit: int | None = None,
        token: str | None = None,
        request: Request | None = None,
        **kwargs,
    ) -> ItemCollection | Response:
        """Search items in a catalog's descendant tree using query parameters.

        This endpoint performs a scoped search bounded to the specified catalog
        and its descendants, supporting recursive tree traversal.

        Args:
            catalog_id: The ID of the catalog to search within.
            collections: Array of collection IDs to search.
            ids: Array of item IDs to search for.
            bbox: Bounding box to filter items [minx, miny, maxx, maxy].
            intersects: GeoJSON geometry for spatial filtering.
            datetime: Datetime to filter items.
            limit: Maximum number of items to return.
            token: Pagination token.
            request: Optional FastAPI request object.

        Returns:
            ItemCollection containing matching items.
        """
        ...

    @abc.abstractmethod
    async def catalog_search_post(
        self,
        catalog_id: str,
        search_request: BaseSearchPostRequest,
        request: Request | None = None,
        **kwargs,
    ) -> ItemCollection | Response:
        """Search items in a catalog's descendant tree using a JSON payload.

        This endpoint performs a scoped search bounded to the specified catalog
        and its descendants, supporting recursive tree traversal.

        Args:
            catalog_id: The ID of the catalog to search within.
            search_request: Search request body (BaseSearchPostRequest).
            request: Optional FastAPI request object.

        Returns:
            ItemCollection containing matching items.
        """
        ...


@attr.s
class BaseCatalogsSearchClient(abc.ABC):
    """Defines a synchronous pattern for implementing the Scoped Search extension.

    This is the base class for synchronous catalog search client implementations.
    For async implementations, use AsyncCatalogsSearchClient instead.
    """

    pass
