import httpx
from app.core.config import settings

STORAGE_BASE = f"{settings.SUPABASE_URL}/storage/v1"
BUCKET = settings.SUPABASE_BUCKET
HEADERS = {
    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
    "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
}


class StorageUploadError(Exception):
    def __init__(self, status_code: int, response_text: str):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(f"Supabase upload failed: {response_text}")


async def upload_file(
    file_bytes: bytes,
    file_name: str,
    content_type: str = "application/pdf",
    upsert: bool = False,
) -> str:
    """Upload resume file to Supabase Storage. Returns the storage path."""
    url = f"{STORAGE_BASE}/object/{BUCKET}/{file_name}"
    headers = {**HEADERS, "Content-Type": content_type}
    if upsert:
        headers["x-upsert"] = "true"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            headers=headers,
            content=file_bytes,
        )
    if response.status_code not in (200, 201):
        raise StorageUploadError(response.status_code, response.text)
    return file_name  # storage path


async def get_signed_url(file_name: str, expires_in: int = 3600) -> str:
    """Generate a signed URL valid for `expires_in` seconds."""
    url = f"{STORAGE_BASE}/object/sign/{BUCKET}/{file_name}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            headers=HEADERS,
            json={"expiresIn": expires_in},
        )
    if response.status_code != 200:
        raise Exception(f"Supabase sign failed: {response.text}")
    signed_path = response.json()["signedURL"]
    if signed_path.startswith("http"):
        return signed_path
    return f"{settings.SUPABASE_URL}/storage/v1{signed_path}"


async def delete_file(file_name: str) -> None:
    """Delete a file from Supabase Storage."""
    url = f"{STORAGE_BASE}/object/{BUCKET}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.delete(
            url,
            headers=HEADERS,
            json={"prefixes": [file_name]},
        )
    if response.status_code not in (200, 204):
        raise Exception(f"Supabase delete failed: {response.text}")
