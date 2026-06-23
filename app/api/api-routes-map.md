# API Routes Map: Carmel Kinneret App

### **Authentication & Headers**
All routes (except public read routes for Guests) require the Clerk JWT to be passed in the headers.

* **Header:** `Authorization: Bearer <clerk_jwt_token>`
* FastAPI decodes this token via a dependency to extract the `clerkId` and role (`Guest`, `User`, `Admin`).

---

### **1. Map & Core Domain Routes**
*These routes serve the foundational map data. Guests can access these without authentication.*

| Method | Endpoint | Query Params | Request Body | Response | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GET** | `/api/trails` | None | None | `Array<TrailSection>` | Returns the 8 main trail sections, including their geojson LineStrings and `orderIndex`. |
| **GET** | `/api/pois` | `type` (optional: 'MAIN', 'EVENT') | None | `Array<POI>` | Returns active POIs. Includes `imageUrl`, discriminated `metadata` JSONB object, and geojson Point. |

---

### **2. Feed & User Posts**
*These routes handle user-generated content. Fetching posts is public, but creating requires a `User` role.*

| Method | Endpoint | Query Params | Request Body | Response | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GET** | `/api/posts` | `sort_by`, `limit`, `offset`, `location` | None | `{ posts: Array<Post>, next_offset: Int }` | Returns active posts sorted by the provided sort option (`recent` default, `popular`, `distance`). When `sort_by=distance` a GeoJSON point must be supplied via the `location` query parameter. Appends `hasLiked: boolean` if Auth header is present. |
| **POST** | `/api/posts` | None | `{ imageUrl: string, caption: string?, geojson: { "type": "Point", "coordinates": [lon, lat] } }` | `Post` (Created) | Creates a new post; validates that the location is within 1 km of the nearest active POI, otherwise returns a 400 error with message "Post location exceeds 1 km from the nearest point of interest". |
| **GET** | `/api/users/{userId}/posts` | `limit`, `offset` | None | `Array<Post>` | Fetches the post history for a specific user's profile tab. |

---

### **3. Interactivity (Likes)**
*Requires a `User` role. The URLs identify the target resource.*

| Method | Endpoint | Query Params | Request Body | Response | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **POST** | `/api/posts/{postId}/like` | None | None | `{ success: boolean, totalLikes: Int }` | Creates a `PostLike` record linking the authenticated user to the post. |
| **DELETE** | `/api/posts/{postId}/like` | None | None | `{ success: boolean, totalLikes: Int }` | Removes the authenticated user's `PostLike` record. |

---

### **4. Admin & Moderation**
*Strictly enforces an `Admin` role check in the FastAPI dependency layer. Uses `DELETE` for hard removals and `PATCH` for soft‑delete toggles where appropriate.*

| Method | Endpoint | Query Params | Request Body | Response | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DELETE** | `/api/admin/posts/{postId}` | None | None | `Post` (Deleted) | Deletes a post (hard delete). |
| **PATCH** | `/api/admin/pois/{poiId}` | None | `{ isActive: boolean }` | `POI` (Updated) | Soft deletes or restores a POI (e.g., if a trail section closes). |
| **POST** | `/api/admin/poi` | None | `{ title: string, type: 'EVENT', imageUrl: string?, geojson: { "type": "Point", "coordinates": [lon, lat] }, metadata: JSON }` | `POI` (Created) | Creates a dynamic event marker on the map. |
| **DELETE** | `/api/admin/pois/{poiId}` | None | None | `POI` (Deleted) | Soft deletes a POI. |

---

### **Standardized Error Response**
All 400/500 errors must be wrapped in this exact JSON format so the client can handle them predictably:

```json
{
  "error": true,
  "code": 404,
  "message": "Resource not found or has been removed."
}