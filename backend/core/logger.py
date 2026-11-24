"""
Módulo de Logging centralizado do Backup Utility CiD.
Configura gravação com rotação em logs/bot_backup.log e saída no console.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import re


class SensitiveDataFilter(logging.Filter):
    """Mascara credenciais, tokens e sessões antes da gravação em log (LGPD/Segurança)."""

    _PATTERNS = [
        (re.compile(r'(?i)(password|senha|token|session|secret)["\']?\s*[:=]\s*["\']?([^\s"\',;]+)'), r'\1=***'),
        (re.compile(r'(?i)(Bearer\s+)[A-Za-z0-9\-._~+/]+=*'), r'\1***'),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        for pattern, repl in self._PATTERNS:
            msg = pattern.sub(repl, msg)
        record.msg = msg
        record.args = ()
        return True

# Cria diretório de logs na raiz do projeto se não existir
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(parents=True, exist_ok=True)
MAIN_LOG_FILE = LOGS_DIR / "bot_backup.log"

logger = logging.getLogger("BackupUtilityCiD")
logger.setLevel(logging.DEBUG)
if not any(isinstance(f, SensitiveDataFilter) for f in logger.filters):
    logger.addFilter(SensitiveDataFilter())

if not logger.handlers:
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1. Rotating File Handler (máx 5MB por arquivo, até 5 backups)
    file_handler = RotatingFileHandler(
        str(MAIN_LOG_FILE),
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 2. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def add_backup_folder_logger(backup_folder: str):
    """Adiciona um handler de arquivo para gravar cópia do log dentro da pasta do backup específico."""
    folder = Path(backup_folder)
    if folder.exists():
        session_log_file = folder / "backup_restoration.log"
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler = logging.FileHandler(str(session_log_file), encoding="utf-8")
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
