from typing import Callable
import time

from fastapi import Request, Response
from starlette.types import ASGIApp
from starlette.middleware.base import BaseHTTPMiddleware

from app.metrics.http_metrics import HTTPMetrics


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, http_metrics: HTTPMetrics):
        super().__init__(app)
        self.http_metrics = http_metrics

    def _get_route_path(self, request: Request) -> str:
        """Extract the route path from the request"""
        # Try to get the matched route path
        if hasattr(request, 'url') and hasattr(request.url, 'path'):
            path = request.url.path

            # Try to get the route from FastAPI
            if hasattr(request, 'scope') and 'route' in request.scope:
                route = request.scope.get('route')
                if hasattr(route, 'path'):
                    return route.path

            # Fallback to actual path
            return path

        return "unknown"

    def _get_request_size(self, request: Request) -> int:
        """Get request content length"""
        content_length = request.headers.get('content-length')
        if content_length:
            try:
                return int(content_length)
            except ValueError:
                pass
        return 0

    def _get_response_size(self, response: Response) -> int:
        """Get response content length"""
        if hasattr(response, 'headers') and 'content-length' in response.headers:
            try:
                return int(response.headers['content-length'])
            except ValueError:
                pass

        # Try to get from body if available
        if hasattr(response, 'body'):
            return len(response.body) if response.body else 0

        return 0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        method = request.method
        endpoint = self._get_route_path(request)
        request_size = self._get_request_size(request)

        # Mark request start
        self.http_metrics.start_request(method, endpoint)

        try:
            response = await call_next(request)

            # Calculate metrics
            duration = time.time() - start_time
            status_code = response.status_code
            response_size = self._get_response_size(response)

            # Record metrics
            self.http_metrics.record_request(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration=duration,
                request_size=request_size,
                response_size=response_size
            )

            return response

        except Exception as exc:
            # Record exception
            exception_type = type(exc).__name__
            self.http_metrics.record_exception(method, endpoint, exception_type)

            # Calculate duration even for exceptions
            duration = time.time() - start_time

            # Record request with 500 status for exceptions
            self.http_metrics.record_request(
                method=method,
                endpoint=endpoint,
                status_code=500,
                duration=duration,
                request_size=request_size,
                response_size=0
            )

            raise exc

        finally:
            # Mark request end
            self.http_metrics.end_request(method, endpoint)