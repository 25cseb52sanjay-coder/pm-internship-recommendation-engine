import re
import time
import os
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple

# Simple thread-safe in-memory sliding window rate limiter (PDF Section 7 Security Specification)
# Prevents DoS scraping & auth brute-force attacks
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 120, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.ip_store: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate-limiting for static uploads or openapi docs
        path = request.url.path
        if path.startswith("/uploads") or path.endswith("/openapi.json") or path.endswith("/docs"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()

        # Skip rate-limiting for local loopback test clients (Point 23 Specification)
        if client_ip in ("127.0.0.1", "localhost", "testclient"):
            return await call_next(request)

        # Clean old timestamps outside window
        timestamps = self.ip_store.get(client_ip, [])
        timestamps = [t for t in timestamps if now - t < self.window_seconds]

        # Auth endpoints stricter rate limit (15 requests / minute)
        limit = 15 if "/auth/" in path else self.max_requests

        if len(timestamps) >= limit:
            return Response(
                content='{"detail": "Rate limit exceeded. Too many requests. Please try again later."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={"Retry-After": str(self.window_seconds)}
            )

        timestamps.append(now)
        self.ip_store[client_ip] = timestamps

        response = await call_next(request)
        # Security HTTP Headers (Task 25 Production Security Specification)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

def sanitize_upload_filename(filename: str) -> str:
    """
    Sanitizes uploaded resume filename to prevent Path Traversal attacks (PDF Section 7 Security).
    Strips directory separators, null bytes, and non-alphanumeric special characters.
    """
    if not filename:
        return "uploaded_resume.pdf"
    
    # Remove path components
    filename = os.path.basename(filename)
    filename = filename.replace("\0", "").replace("..", "")
    
    # Keep extension intact
    name, ext = os.path.splitext(filename)
    sanitized_name = re.sub(r'[^\w\-]', '_', name)
    sanitized_ext = re.sub(r'[^\w]', '', ext.lower())
    
    return f"{sanitized_name[:50]}.{sanitized_ext}"

def validate_file_mime_type(file_bytes: bytes, filename: str) -> str:
    """
    Validates magic bytes / MIME headers for uploaded files (PDF Section 7 Security).
    """
    ext = os.path.splitext(filename)[1].lower()
    
    # Check PDF magic bytes (%PDF)
    if ext == ".pdf":
        if not file_bytes.startswith(b"%PDF"):
            raise HTTPException(status_code=400, detail="Invalid PDF file content. Magic header validation failed.")
    # Check PNG magic bytes (\x89PNG)
    elif ext == ".png":
        if not file_bytes.startswith(b"\x89PNG"):
            raise HTTPException(status_code=400, detail="Invalid PNG image file. Magic header validation failed.")
    # Check JPEG magic bytes (\xff\xd8\xff)
    elif ext in [".jpg", ".jpeg"]:
        if not file_bytes.startswith(b"\xff\xd8\xff"):
            raise HTTPException(status_code=400, detail="Invalid JPEG image file. Magic header validation failed.")
            
    return ext
