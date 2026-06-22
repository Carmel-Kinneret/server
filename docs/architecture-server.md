---
id: architecture-server
title: Server Architecture
sidebar_label: Server Architecture
---

# Carmel Kinneret Server Architecture

This document describes the foundational architecture of the backend for the Carmel Kinneret application.

## Overview

The backend is built using **FastAPI** to take advantage of its async capabilities and automatic OpenAPI generation. It connects to a **NeonDB PostgreSQL** database using the `asyncpg` driver and `SQLAlchemy 2.0`.

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (NeonDB)
- **ORM**: SQLAlchemy (async)
- **Data Validation**: Pydantic v2
- **Authentication**: Clerk (JWT Verification)

## Directory Structure

- `app/api/`: API Routers and endpoints.
- `app/core/`: Configuration, exceptions, and authentication dependencies.
- `app/db/`: Database connection and session management.
- `app/models/`: SQLAlchemy declarative models.
- `app/schemas/`: Pydantic models for request/response validation.

## Database Design

The database schema heavily relies on PostgreSQL's `JSONB` data type to support flexible data storage, specifically:

- **GeoJSON**: `TrailSection`, `PointOfInterest`, and `Post` use `JSONB` columns to store `geoJson` geometry points and lines. This keeps the schema simple without requiring `PostGIS` initially, while still allowing the client to consume standard GeoJSON.
- **Metadata**: `PointOfInterest` uses a `metadata` `JSONB` column to store type-specific properties (e.g., whether a spring has potable water, or the date of an event), simulating a lightweight Single Table Inheritance pattern.

## Authentication Flow

We use **Clerk** for user authentication.

1. The client sends a request with an `Authorization: Bearer <token>` header.
2. The `verify_token` dependency in `app/core/auth.py` intercepts the request.
3. It fetches Clerk's JWKS (JSON Web Key Set) using `python-jose` to find the corresponding RSA public key.
4. The token is decoded and validated against the `CLERK_ISSUER` and `CLERK_FRONTEND_API` environment variables.
5. If valid, the `get_current_user` dependency looks up the user in the database based on the token's `sub` (Clerk ID) claim.

> [!NOTE]
> Ensure the `.env` file contains `CLERK_ISSUER` and `CLERK_FRONTEND_API` for authentication to succeed.
