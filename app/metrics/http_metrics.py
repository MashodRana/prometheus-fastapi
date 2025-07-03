from prometheus_client import Counter, Histogram, Gauge


class HTTPMetrics:
    def __init__(self):
        # Request counters
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code']
        )

        # Request duration histogram
        self.http_request_duration_seconds = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
        )

        # Request size histogram
        self.http_request_size_bytes = Histogram(
            'http_request_size_bytes',
            'HTTP request size in bytes',
            ['method', 'endpoint'],
            buckets=[64, 256, 1024, 4096, 16384, 65536, 262144, 1048576, 4194304]
        )

        # Response size histogram
        self.http_response_size_bytes = Histogram(
            'http_response_size_bytes',
            'HTTP response size in bytes',
            ['method', 'endpoint'],
            buckets=[64, 256, 1024, 4096, 16384, 65536, 262144, 1048576, 4194304]
        )

        # Active requests gauge
        self.http_requests_active = Gauge(
            'http_requests_active',
            'Number of active HTTP requests',
            ['method', 'endpoint']
        )

        # Application info
        self.http_requests_exceptions_total = Counter(
            'http_requests_exceptions_total',
            'Total HTTP requests that resulted in exceptions',
            ['method', 'endpoint', 'exception_type']
        )

    def record_request(
            self,
            method: str,
            endpoint: str,
            status_code: int,
            duration: float,
            request_size: int = 0,
            response_size: int = 0
    ):
        """Record metrics for a completed HTTP request"""
        # Convert status code to string
        status_str = str(status_code)

        # Record request count
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_str
        ).inc()

        # Record duration
        self.http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

        # Record request size
        if request_size > 0:
            self.http_request_size_bytes.labels(
                method=method,
                endpoint=endpoint
            ).observe(request_size)

        # Record response size
        if response_size > 0:
            self.http_response_size_bytes.labels(
                method=method,
                endpoint=endpoint
            ).observe(response_size)

    def record_exception(self, method: str, endpoint: str, exception_type: str):
        """Record an exception for a request"""
        self.http_requests_exceptions_total.labels(
            method=method,
            endpoint=endpoint,
            exception_type=exception_type
        ).inc()

    def start_request(self, method: str, endpoint: str):
        """Mark the start of a request"""
        self.http_requests_active.labels(
            method=method,
            endpoint=endpoint
        ).inc()

    def end_request(self, method: str, endpoint: str):
        """Mark the end of a request"""
        self.http_requests_active.labels(
            method=method,
            endpoint=endpoint
        ).dec()