"""
Performance Monitoring Service

This module provides performance monitoring functionality for the application.
"""

import time
import logging
import threading
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import deque

@dataclass
class PerformanceMetric:
    """Data class for storing performance metrics."""
    name: str
    value: float
    timestamp: datetime
    endpoint: str
    context: Dict

class PerformanceMonitor:
    """Service for monitoring application performance."""
    
    def __init__(self, max_history: int = 1000):
        """Initialize the performance monitor."""
        self.logger = logging.getLogger(__name__)
        self.metrics: deque = deque(maxlen=max_history)
        self.slow_threshold: float = 0.5  # seconds
        self.lock = threading.Lock()
        
    def record_metric(self, name: str, value: float, endpoint: str = "", context: Dict = None) -> None:
        """Record a performance metric."""
        with self.lock:
            metric = PerformanceMetric(
                name=name,
                value=value,
                timestamp=datetime.now(),
                endpoint=endpoint,
                context=context or {}
            )
            self.metrics.append(metric)
            
            if name == "response_time" and value > self.slow_threshold:
                self.logger.warning(
                    f"Slow request detected: {endpoint} took {value:.2f}s",
                    extra={"metric": metric}
                )
                
    def get_metrics(self, 
                    metric_name: Optional[str] = None,
                    time_window: Optional[timedelta] = None) -> List[PerformanceMetric]:
        """Get recorded metrics, optionally filtered by name and time window."""
        with self.lock:
            now = datetime.now()
            metrics = list(self.metrics)
            
        if metric_name:
            metrics = [m for m in metrics if m.name == metric_name]
            
        if time_window:
            cutoff = now - time_window
            metrics = [m for m in metrics if m.timestamp >= cutoff]
            
        return metrics
        
    def get_performance_report(self) -> Dict:
        """Generate a performance report."""
        with self.lock:
            metrics = list(self.metrics)
            
        now = datetime.now()
        last_minute = now - timedelta(minutes=1)
        
        # Calculate statistics
        response_times = [
            m.value for m in metrics 
            if m.name == "response_time" and m.timestamp >= last_minute
        ]
        
        memory_metrics = [
            m.value for m in metrics
            if m.name == "memory_usage" and m.timestamp >= last_minute
        ]
        
        return {
            "last_minute": {
                "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "avg_memory_usage": sum(memory_metrics) / len(memory_metrics) if memory_metrics else 0,
                "request_count": len(response_times),
                "slow_requests": sum(1 for t in response_times if t > self.slow_threshold)
            },
            "total_metrics_recorded": len(metrics),
            "timestamp": now.isoformat()
        }
        
    def clear_old_metrics(self, max_age: timedelta) -> None:
        """Clear metrics older than max_age."""
        with self.lock:
            cutoff = datetime.now() - max_age
            self.metrics = deque(
                (m for m in self.metrics if m.timestamp >= cutoff),
                maxlen=self.metrics.maxlen
            )
            
    def set_slow_threshold(self, threshold: float) -> None:
        """Set the threshold for slow request detection."""
        self.slow_threshold = threshold
        
# Create a global instance
performance_monitor = PerformanceMonitor() 