"""Enhanced logging system for Atom with metrics tracking and structured logging.

Features:
- Standard logging with console and file handlers
- Performance metrics tracking
- Structured JSON logging option
- Log rotation with size limits
- Debug mode support
- Session tracking
"""

import logging
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON formatted log string
        """
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'session_id'):
            log_data['session_id'] = record.session_id
        if hasattr(record, 'confidence'):
            log_data['confidence'] = record.confidence
        if hasattr(record, 'intent'):
            log_data['intent'] = record.intent
        if hasattr(record, 'response_time'):
            log_data['response_time'] = record.response_time
        
        return json.dumps(log_data)


class MetricsLogger:
    """Performance metrics tracking for Atom.
    
    Tracks:
    - Response times
    - Confidence scores
    - Intent distribution
    - Error rates
    - Session statistics
    
    Attributes:
        metrics_file (Path): Path to metrics JSON file
        metrics (Dict): Current metrics data
    """
    
    def __init__(self, metrics_file: str = "logs/metrics.json"):
        """Initialize metrics logger.
        
        Args:
            metrics_file: Path to metrics file
        """
        self.metrics_file = Path(metrics_file)
        self.metrics: Dict[str, Any] = self._load_metrics()
        self.session_start = datetime.now()
        self.current_session = {
            'start_time': self.session_start.isoformat(),
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'avg_confidence': 0.0,
            'avg_response_time': 0.0,
            'intents': {}
        }
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Load existing metrics from file.
        
        Returns:
            Dictionary of metrics data
        """
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {'sessions': [], 'total_queries': 0}
        return {'sessions': [], 'total_queries': 0}
    
    def _save_metrics(self):
        """Save metrics to file."""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except IOError as e:
            logging.error(f"Failed to save metrics: {e}")
    
    def record_query(self, intent: str, confidence: float, 
                     response_time: float, success: bool = True):
        """Record a query metric.
        
        Args:
            intent: Intent tag
            confidence: Confidence score (0-1)
            response_time: Response time in seconds
            success: Whether query was successful
        """
        self.current_session['total_queries'] += 1
        
        if success:
            self.current_session['successful_queries'] += 1
        else:
            self.current_session['failed_queries'] += 1
        
        # Update intent distribution
        if intent not in self.current_session['intents']:
            self.current_session['intents'][intent] = 0
        self.current_session['intents'][intent] += 1
        
        # Update averages
        total = self.current_session['total_queries']
        
        # Running average for confidence
        old_avg_conf = self.current_session['avg_confidence']
        self.current_session['avg_confidence'] = (
            (old_avg_conf * (total - 1) + confidence) / total
        )
        
        # Running average for response time
        old_avg_time = self.current_session['avg_response_time']
        self.current_session['avg_response_time'] = (
            (old_avg_time * (total - 1) + response_time) / total
        )
    
    def finalize_session(self):
        """Finalize current session and save metrics."""
        self.current_session['end_time'] = datetime.now().isoformat()
        self.current_session['duration_seconds'] = (
            datetime.now() - self.session_start
        ).total_seconds()
        
        self.metrics['sessions'].append(self.current_session)
        self.metrics['total_queries'] += self.current_session['total_queries']
        
        self._save_metrics()
    
    def get_session_summary(self) -> str:
        """Get summary of current session.
        
        Returns:
            String summary of session metrics
        """
        session = self.current_session
        return (
            f"Session Summary:\n"
            f"  Total Queries: {session['total_queries']}\n"
            f"  Success Rate: {session['successful_queries']}/{session['total_queries']}\n"
            f"  Avg Confidence: {session['avg_confidence']:.2f}\n"
            f"  Avg Response Time: {session['avg_response_time']:.3f}s\n"
            f"  Top Intents: {sorted(session['intents'].items(), key=lambda x: x[1], reverse=True)[:3]}"
        )


def setup_logger(name: str, log_file: Optional[str] = None, 
                level: int = logging.INFO, 
                structured: bool = False,
                enable_rotation: bool = True,
                max_bytes: int = 10 * 1024 * 1024,  # 10MB
                backup_count: int = 5) -> logging.Logger:
    """Setup logger with console and file handlers.
    
    Args:
        name: Logger name (usually __name__)
        log_file: Optional log file name
        level: Logging level (default: INFO)
        structured: Use structured JSON logging
        enable_rotation: Enable log rotation
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatters
    if structured:
        detailed_formatter = StructuredFormatter()
        simple_formatter = StructuredFormatter()
    else:
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler (DEBUG and above)
    if log_file:
        if enable_rotation:
            file_handler = RotatingFileHandler(
                LOG_DIR / log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
        else:
            file_handler = logging.FileHandler(LOG_DIR / log_file)
        
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    # Error-only file handler
    if log_file:
        error_file = log_file.replace('.log', '_errors.log')
        error_handler = logging.FileHandler(LOG_DIR / error_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)
    
    return logger


def setup_debug_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """Setup logger with DEBUG level for development.
    
    Args:
        name: Logger name
        log_file: Optional log file name
        
    Returns:
        Logger configured for debug mode
    """
    return setup_logger(name, log_file, level=logging.DEBUG, structured=False)


# Global metrics logger instance
_metrics_logger: Optional[MetricsLogger] = None


def get_metrics_logger() -> MetricsLogger:
    """Get global metrics logger instance.
    
    Returns:
        MetricsLogger instance
    """
    global _metrics_logger
    if _metrics_logger is None:
        _metrics_logger = MetricsLogger()
    return _metrics_logger


# Example usage
if __name__ == "__main__":
    # Demo the enhanced logging
    print("Enhanced Logging Demo")
    print("=" * 50)
    
    # Standard logging
    logger = setup_logger(__name__, 'demo.log', level=logging.DEBUG)
    logger.info("This is an info message")
    logger.warning("This is a warning")
    logger.error("This is an error")
    logger.debug("This is a debug message")
    
    # Structured logging
    struct_logger = setup_logger('structured', 'demo_structured.log', 
                                 level=logging.DEBUG, structured=True)
    struct_logger.info("Structured log message", 
                      extra={'session_id': 'demo_123', 'confidence': 0.95})
    
    # Metrics logging
    metrics = get_metrics_logger()
    metrics.record_query('greeting', 0.95, 0.123, success=True)
    metrics.record_query('time', 0.88, 0.045, success=True)
    metrics.record_query('unknown', 0.45, 0.078, success=False)
    
    print("\n" + metrics.get_session_summary())
    
    metrics.finalize_session()
    print("\nMetrics saved to logs/metrics.json")
    print("Demo complete!")

