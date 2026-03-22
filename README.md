<!-- markdownlint-disable MD033 MD041 -->


<p align="left">
  <img src="https://raw.githubusercontent.com/stac-utils/stac-fastapi-elasticsearch-opensearch/refs/heads/main/assets/sfeos.png" width=1000>
</p>

**Jump to:** | [Table of Contents](#table-of-contents) |

  [![Downloads](https://static.pepy.tech/badge/stac-fastapi-catalogs-extension?color=blue)](https://pepy.tech/project/stac-fastapi-catalogs-extension)
   [![PyPI version](https://img.shields.io/pypi/v/stac-fastapi-catalogs-extension.svg?color=blue)](https://pypi.org/project/stac-fastapi-catalogs-extension/)
  [![STAC](https://img.shields.io/badge/STAC-1.1.0-blue.svg)](https://github.com/radiantearth/stac-spec/tree/v1.1.0)


# stac-fastapi multi-tenant virtual catalogs extension

STAC FastAPI extension for multi-tenant, recursive catalog hierarchies.

This package adds a dedicated /catalogs registry and scoped catalog routes so a
single STAC API deployment can serve multiple logical catalog trees. It is
designed for use cases where one API needs tenant-style isolation, curated
views, provider-specific trees, or thematic navigation across shared datasets.

The extension supports poly-hierarchy (multi-parenting), where a collection or
catalog can be linked under multiple catalog paths without duplicating data.
It also supports contextual navigation for scoped routes, preserving UI
breadcrumb behavior while still exposing alternative parents through related
links.

## Table of contents

- [Specification reference](#specification-reference)
- [Conformance class guidance](#conformance-class-guidance)
- [What this package provides](#what-this-package-provides)
- [Supported projects](#supported-projects)
- [Install](#install)
- [Integrate in a STAC FastAPI deployment](#integrate-in-a-stac-fastapi-deployment)
- [Backend client requirements](#backend-client-requirements)
- [Notes for common deployment repos](#notes-for-common-deployment-repos)
- [Endpoints added by this extension](#endpoints-added-by-this-extension)

## Specification reference

This implementation is aligned with the Multi-Tenant Catalogs extension work in
StacLabs:

- https://github.com/StacLabs/multi-tenant-catalogs

Notable concepts adopted here include:

- Recursive /catalogs endpoint structure
- Optional transaction management plane
- Safety-first unlink semantics (organizational operations are non-destructive)
- Runtime link generation for parent/child/related relationships

## Conformance class guidance

When enabling this extension in your deployment, advertise conformance classes
according to your enabled capabilities:

- Required:
	- https://api.stacspec.org/v1.0.0/core
	- https://api.stacspec.org/v1.0.0-beta.4/multi-tenant-catalogs
- Recommended:
	- https://api.stacspec.org/v1.0.0-rc.2/children
- Optional (only if transaction endpoints are enabled):
	- https://api.stacspec.org/v1.0.0-beta.4/multi-tenant-catalogs/transaction

Operational guidance:

- Read-only/public APIs should not expose POST/PUT/DELETE catalog endpoints and
	should not advertise the transaction conformance class.
- If transactions are enabled, expose and document the management endpoints and
	include the transaction conformance class in conformance responses.

## Supported projects

This extension is designed for STAC FastAPI deployment applications and is
currently supported in:

- SFEOS: https://github.com/stac-utils/stac-fastapi-elasticsearch-opensearch
- stac-fastapi-pgstac style deployments:
	https://github.com/stac-utils/stac-fastapi-pgstac

It can also be integrated into custom STAC FastAPI deployments that implement
the AsyncBaseCatalogsClient contract.

## What this package provides

- A STAC FastAPI extension class: CatalogsExtension
- Request/response models for catalogs and children APIs
- An abstract client contract: AsyncBaseCatalogsClient

This package wires routes and validation into your API. Your deployment app is
responsible for providing a concrete client implementation backed by your
database/search stack.

## Install

```bash
pip install stac-fastapi-catalogs-extension
```

## Integrate in a STAC FastAPI deployment

In your deployment app.py (for example in stac-fastapi-elasticsearch-opensearch
or stac-fastapi-pgstac style apps), instantiate StacApi with CatalogsExtension
and pass an implementation of AsyncBaseCatalogsClient.

```python
from stac_fastapi.api.app import StacApi
from stac_fastapi.types.config import ApiSettings

from multi_tenant_catalogs import CatalogsExtension
from my_project.catalogs_client import CatalogsClient
from my_project.core_client import CoreClient


settings = ApiSettings()

core_client = CoreClient(...)
catalogs_client = CatalogsClient(...)

api = StacApi(
    settings=settings,
    client=core_client,
    extensions=[
        CatalogsExtension(
            client=catalogs_client,
            enable_transactions=True,
            settings=settings.model_dump(),
        )
    ],
)

app = api.app
```

## Backend client requirements

Your CatalogsClient should subclass AsyncBaseCatalogsClient and implement the
required async methods, including:

- get_catalogs
- get_catalog
- create_catalog
- update_catalog
- delete_catalog
- get_catalog_collections
- create_catalog_collection
- get_sub_catalogs
- create_sub_catalog
- unlink_sub_catalog
- get_catalog_children
- get_catalog_conformance
- get_catalog_queryables

## Notes for common deployment repos

### stac-fastapi-elasticsearch-opensearch style deployment

- Build a catalogs client that reads/writes catalog links and hierarchy metadata
  from your OpenSearch/Elasticsearch index strategy.
- Reuse your existing core client for global /collections and /search routes.
- Add CatalogsExtension to the extensions list in app.py as shown above.

### stac-fastapi-pgstac style deployment

- Build a catalogs client that maps these methods to SQL functions or pgstac
  tables/views that represent catalog hierarchy and scoped membership.
- Keep link generation contextual for scoped routes
  (/catalogs/{id}/collections/{collection_id}) so UI breadcrumb navigation stays
  correct.
- Add CatalogsExtension to the extensions list in app.py as shown above.

## Endpoints added by this extension

- GET /catalogs
- GET /catalogs/{catalog_id}
- GET /catalogs/{catalog_id}/collections
- GET /catalogs/{catalog_id}/collections/{collection_id}
- GET /catalogs/{catalog_id}/collections/{collection_id}/items
- GET /catalogs/{catalog_id}/collections/{collection_id}/items/{item_id}
- GET /catalogs/{catalog_id}/catalogs
- GET /catalogs/{catalog_id}/children
- GET /catalogs/{catalog_id}/conformance
- GET /catalogs/{catalog_id}/queryables

When enable_transactions=True:

- POST /catalogs
- PUT /catalogs/{catalog_id}
- DELETE /catalogs/{catalog_id}
- POST /catalogs/{catalog_id}/collections
- DELETE /catalogs/{catalog_id}/collections/{collection_id}
- POST /catalogs/{catalog_id}/catalogs
- DELETE /catalogs/{catalog_id}/catalogs/{sub_catalog_id}

