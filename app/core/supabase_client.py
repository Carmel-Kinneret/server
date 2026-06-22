from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from app.core.config import settings

# Initialize the Supabase Client using the service role key for full admin access
if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
    # We define a dummy client or placeholder for testing/graceful import
    supabase: Optional[Client] = None
else:
    supabase: Optional[Client] = create_client(
        settings.SUPABASE_URL, 
        settings.SUPABASE_SERVICE_ROLE_KEY
    )

# =====================================================================
# S3 Storage Helper
# =====================================================================

def upload_post_image(file_name: str, file_data: bytes, content_type: str = "image/jpeg") -> str:
    """
    Uploads a post image binary to the public 'post-images' bucket 
    and returns its public URL.
    """
    if not supabase:
        raise ValueError("Supabase client is not initialized. Check your environment variables.")
        
    options = {"content-type": content_type, "x-upsert": "true"}
    
    # Upload binary file using supabase storage
    supabase.storage.from_("post-images").upload(
        path=file_name,
        file=file_data,
        file_options=options
    )
    
    # Retrieve and return the public URL
    return supabase.storage.from_("post-images").get_public_url(file_name)

# =====================================================================
# User CRUD operations (Table: "User")
# =====================================================================

def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a new User row."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("User").insert(user_data).execute()
    return response.data[0] if response.data else {}

def get_user_by_id(user_id: str) -> Dict[str, Any]:
    """Retrieves a User by primary key ID."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("User").select("*").eq("id", user_id).execute()
    return response.data[0] if response.data else {}

def get_user_by_clerk_id(clerk_id: str) -> Dict[str, Any]:
    """Retrieves a User by their Clerk authenticated ID."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("User").select("*").eq("clerkId", clerk_id).execute()
    return response.data[0] if response.data else {}

def update_user(user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates an existing User by ID."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("User").update(user_data).eq("id", user_id).execute()
    return response.data[0] if response.data else {}

def delete_user(user_id: str) -> Dict[str, Any]:
    """Deletes a User by ID."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("User").delete().eq("id", user_id).execute()
    return response.data[0] if response.data else {}

# =====================================================================
# Post CRUD operations (Table: "Post")
# =====================================================================

def create_post(post_data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a new user Post row."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("Post").insert(post_data).execute()
    return response.data[0] if response.data else {}

def get_post_by_id(post_id: str) -> Dict[str, Any]:
    """Retrieves a Post by ID."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("Post").select("*").eq("id", post_id).execute()
    return response.data[0] if response.data else {}

def list_posts(limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """Lists all active Posts with ordering and range limits."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = (
        supabase.table("Post")
        .select("*")
        .eq("isActive", True)
        .order("createdAt", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return response.data or []

def update_post(post_id: str, post_data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates an existing Post by ID (e.g. for soft-delete isActive change)."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("Post").update(post_data).eq("id", post_id).execute()
    return response.data[0] if response.data else {}

def delete_post(post_id: str) -> Dict[str, Any]:
    """Deletes a Post by ID."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("Post").delete().eq("id", post_id).execute()
    return response.data[0] if response.data else {}

# =====================================================================
# PointOfInterest CRUD operations (Table: "PointOfInterest")
# =====================================================================

def create_poi(poi_data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a new Point of Interest row."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("PointOfInterest").insert(poi_data).execute()
    return response.data[0] if response.data else {}

def get_poi_by_id(poi_id: str) -> Dict[str, Any]:
    """Retrieves a Point of Interest by ID."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("PointOfInterest").select("*").eq("id", poi_id).execute()
    return response.data[0] if response.data else {}

def list_pois(poi_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lists active Points of Interest, optionally filtered by type (MAIN or EVENT)."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    query = supabase.table("PointOfInterest").select("*").eq("isActive", True)
    if poi_type:
        query = query.eq("type", poi_type)
    response = query.execute()
    return response.data or []

def update_poi(poi_id: str, poi_data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates an existing Point of Interest by ID."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("PointOfInterest").update(poi_data).eq("id", poi_id).execute()
    return response.data[0] if response.data else {}

def delete_poi(poi_id: str) -> Dict[str, Any]:
    """Deletes a Point of Interest row by ID."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("PointOfInterest").delete().eq("id", poi_id).execute()
    return response.data[0] if response.data else {}

# =====================================================================
# TrailSection CRUD operations (Table: "TrailSection")
# =====================================================================

def create_trail_section(trail_data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a new Trail Section row."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("TrailSection").insert(trail_data).execute()
    return response.data[0] if response.data else {}

def get_trail_section_by_id(trail_id: int) -> Dict[str, Any]:
    """Retrieves a Trail Section by ID."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("TrailSection").select("*").eq("id", trail_id).execute()
    return response.data[0] if response.data else {}

def list_trail_sections() -> List[Dict[str, Any]]:
    """Lists all Trail Sections ordered by their sequence orderIndex."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("TrailSection").select("*").order("orderIndex").execute()
    return response.data or []

def update_trail_section(trail_id: int, trail_data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates an existing Trail Section by ID."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("TrailSection").update(trail_data).eq("id", trail_id).execute()
    return response.data[0] if response.data else {}

def delete_trail_section(trail_id: int) -> Dict[str, Any]:
    """Deletes a Trail Section by ID."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("TrailSection").delete().eq("id", trail_id).execute()
    return response.data[0] if response.data else {}

# =====================================================================
# PostLike CRUD operations (Table: "PostLike")
# =====================================================================

def create_like(like_data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a PostLike row linking a User and a Post."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("PostLike").insert(like_data).execute()
    return response.data[0] if response.data else {}

def get_like(user_id: str, post_id: str) -> Dict[str, Any]:
    """Retrieves a specific PostLike by userId and postId."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = (
        supabase.table("PostLike")
        .select("*")
        .eq("userId", user_id)
        .eq("postId", post_id)
        .execute()
    )
    return response.data[0] if response.data else {}

def delete_like(like_id: str) -> Dict[str, Any]:
    """Deletes a PostLike by primary key ID."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    response = supabase.table("PostLike").delete().eq("id", like_id).execute()
    return response.data[0] if response.data else {}

def count_post_likes(post_id: str) -> int:
    """Counts the total number of likes for a specific Post."""
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    # Performs a head query with count="exact" to retrieve the number of likes efficiently
    response = (
        supabase.table("PostLike")
        .select("id", count="exact")
        .eq("postId", post_id)
        .execute()
    )
    return response.count or 0
