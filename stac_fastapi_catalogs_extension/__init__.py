"""stac-fastapi-catalogs-extension: Multi-tenant catalog hierarchies for STAC FastAPI."""

from .catalogs import (
    CATALOGS_CORE_CONFORMANCE,
    CATALOGS_SEARCH_CONFORMANCE,
    CATALOGS_TRANSACTION_CONFORMANCE,
    CatalogsExtension,
    CatalogsSearchExtension,
    CatalogsTransactionExtension,
)
from .client import AsyncBaseCatalogsClient, BaseCatalogsClient
from .types import (
    CatalogChildrenRequest,
    CatalogCollectionItemsRequest,
    CatalogCollectionItemUri,
    CatalogCollectionUri,
    Catalogs,
    CatalogsGetRequest,
    CatalogsUri,
    Children,
    CreateCatalogCollectionRequest,
    CreateCatalogRequest,
    CreateSubCatalogRequest,
    ObjectUri,
    SubCatalogsRequest,
    UnlinkSubCatalogRequest,
    UpdateCatalogRequest,
)

__all__ = [
    "CatalogsExtension",
    "CatalogsTransactionExtension",
    "CatalogsSearchExtension",
    "AsyncBaseCatalogsClient",
    "BaseCatalogsClient",
    "Catalogs",
    "Children",
    "ObjectUri",
    "CATALOGS_CORE_CONFORMANCE",
    "CATALOGS_TRANSACTION_CONFORMANCE",
    "CATALOGS_SEARCH_CONFORMANCE",
    "CatalogsUri",
    "CatalogsGetRequest",
    "CatalogCollectionUri",
    "CatalogCollectionItemUri",
    "CatalogCollectionItemsRequest",
    "SubCatalogsRequest",
    "CatalogChildrenRequest",
    "CreateCatalogRequest",
    "UpdateCatalogRequest",
    "CreateCatalogCollectionRequest",
    "CreateSubCatalogRequest",
    "UnlinkSubCatalogRequest",
]
