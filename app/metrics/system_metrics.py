# app/metrics/system_metrics.py
import time
import psutil
import threading
from typing import Dict, Any
from prometheus_client import Counter, Gauge, Histogram, Info, start_http_server
import gc
import os


class SystemMetrics:
    def __init__(self):
        # CPU Metrics
        self.process_cpu_seconds_total = Counter(
            'process_cpu_seconds_total',
            'Total CPU time consumed by the process'
        )

        # Memory Metrics
        self.process_resident_memory_bytes = Gauge(
            'process_resident_memory_bytes',
            'Physical memory currently used by the process'
        )

        self.process_virtual_memory_bytes = Gauge(
            'process_virtual_memory_bytes',
            'Virtual memory allocated by the process'
        )

        # Process Info
        self.process_start_time_seconds = Gauge(
            'process_start_time_seconds',
            'Start time of the process since unix epoch'
        )

        self.process_uptime_seconds = Gauge(
            'process_uptime_seconds',
            'Process uptime in seconds'
        )

        # File Descriptors
        self.process_open_fds = Gauge(
            'process_open_fds',
            'Number of open file descriptors'
        )

        self.process_max_fds = Gauge(
            'process_max_fds',
            'Maximum number of open file descriptors'
        )

        # Garbage Collection
        self.python_gc_objects_collected_total = Counter(
            'python_gc_objects_collected_total',
            'Objects collected during gc',
            ['generation']
        )

        self.python_gc_collections_total = Counter(
            'python_gc_collections_total',
            'Number of times this generation was collected',
            ['generation']
        )

        # Thread Count
        self.python_threads = Gauge(
            'python_threads',
            'Number of Python threads'
        )

        # Application Info
        self.python_info = Info(
            'python_info',
            'Python platform information'
        )

        # Initialize
        self.process = psutil.Process()
        self.start_time = time.time()
        self.last_cpu_time = 0
        self.last_gc_stats = self._get_gc_stats()

        # Set static metrics
        self.process_start_time_seconds.set(self.start_time)
        self._set_python_info()

        # Start background collection
        self._start_metrics_collection()

    def _set_python_info(self):
        """Set Python platform information"""
        import sys
        import platform

        self.python_info.info({
            'version': sys.version,
            'implementation': platform.python_implementation(),
            'platform': platform.platform()
        })

    def _get_gc_stats(self) -> Dict[str, Any]:
        """Get garbage collection statistics"""
        stats = {}
        for generation in range(3):
            try:
                stat = gc.get_stats()[generation]
                stats[generation] = {
                    'collections': stat.get('collections', 0),
                    'collected': stat.get('collected', 0),
                    'uncollectable': stat.get('uncollectable', 0)
                }
            except (IndexError, AttributeError):
                stats[generation] = {'collections': 0, 'collected': 0, 'uncollectable': 0}
        return stats

    def _update_cpu_metrics(self):
        """Update CPU metrics"""
        try:
            # Get current CPU time
            cpu_time = self.process.cpu_times()
            total_cpu_time = cpu_time.user + cpu_time.system

            # Update total CPU time counter
            cpu_delta = total_cpu_time - self.last_cpu_time
            if cpu_delta > 0:
                self.process_cpu_seconds_total.inc(cpu_delta)
            self.last_cpu_time = total_cpu_time

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def _update_memory_metrics(self):
        """Update memory metrics"""
        try:
            memory_info = self.process.memory_info()
            self.process_resident_memory_bytes.set(memory_info.rss)
            self.process_virtual_memory_bytes.set(memory_info.vms)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    def _update_fd_metrics(self):
        """Update file descriptor metrics"""
        try:
            # Open file descriptors
            num_fds = self.process.num_fds()
            self.process_open_fds.set(num_fds)

            # Max file descriptors
            try:
                import resource
                max_fds = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
                self.process_max_fds.set(max_fds)
            except (ImportError, OSError):
                pass

        except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
            pass

    def _update_gc_metrics(self):
        """Update garbage collection metrics"""
        try:
            current_stats = self._get_gc_stats()

            for generation in range(3):
                gen_str = str(generation)
                current = current_stats.get(generation, {})
                last = self.last_gc_stats.get(generation, {})

                # Update counters with deltas
                collections_delta = current.get('collections', 0) - last.get('collections', 0)
                collected_delta = current.get('collected', 0) - last.get('collected', 0)

                if collections_delta > 0:
                    self.python_gc_collections_total.labels(generation=gen_str).inc(collections_delta)

                if collected_delta > 0:
                    self.python_gc_objects_collected_total.labels(generation=gen_str).inc(collected_delta)

            self.last_gc_stats = current_stats

        except Exception:
            pass

    def _update_thread_metrics(self):
        """Update thread count metrics"""
        try:
            thread_count = threading.active_count()
            self.python_threads.set(thread_count)
        except Exception:
            pass

    def _update_uptime_metrics(self):
        """Update uptime metrics"""
        uptime = time.time() - self.start_time
        self.process_uptime_seconds.set(uptime)

    def _collect_metrics(self):
        """Collect all system metrics"""
        self._update_cpu_metrics()
        self._update_memory_metrics()
        self._update_fd_metrics()
        self._update_gc_metrics()
        self._update_thread_metrics()
        self._update_uptime_metrics()

    def _start_metrics_collection(self):
        """Start background metrics collection"""

        def collect_loop():
            while True:
                try:
                    self._collect_metrics()
                    time.sleep(5)  # Collect every 5 seconds
                except Exception:
                    # Continue collecting even if there's an error
                    time.sleep(5)

        thread = threading.Thread(target=collect_loop, daemon=True)
        thread.start()


