"""
Logging utilities for Ethos AI
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Setup logging configuration"""
    
    # Create logs directory
    if not log_file:
        log_dir = Path.home() / "EthosAIData" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"ethos_ai_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
        ]
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    
    # Create logger for Ethos AI
    logger = logging.getLogger("ethos_ai")
    logger.info("Logging initialized")
    
    return logger 