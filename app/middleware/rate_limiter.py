from fastapi import Request, Response
from collections import defaultdict, deque
import time

class RateLimiter:
    def __init__(self, max_req: int = 100, window: int = 60):
        self.max_req, self.window, self.store = max_req, window, defaultdict(deque)
    def is_allowed(self, key: str) -> bool:
        now = time.time()
        q = self.store[key]
        while q and q[0] < now - self.window: q.popleft()
        if len(q) >= self.max_req: return False
        q.append(now); return True

rate_limiter = RateLimiter(max_req=60, window=60)

async def rate_limit_middleware(request: Request, call_next) -> Response:
    if request.url.path in ["/api/health", "/", "/api/docs", "/openapi.json", "/favicon.ico"]:
        return await call_next(request)
    key = request.client.host
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "): key = f"user:{auth[7:30]}"
    if not rate_limiter.is_allowed(key):
        return Response(content='{"error":{"code":"RATE_LIMIT","message":"Too many requests"}}', 
                        status_code=429, media_type="application/json", headers={"Retry-After": "60"})
    return await call_next(request)