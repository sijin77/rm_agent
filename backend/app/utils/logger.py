"""
Утилита для тихого логирования в скриптах
"""
import sys
from typing import Optional


class QuietLogger:
    """Тихий логгер - выводит только ошибки и важную информацию"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def info(self, message: str):
        """Информационные сообщения - только в verbose режиме"""
        if self.verbose:
            print(f"ℹ️  {message}")
    
    def success(self, message: str):
        """Успешные операции - всегда выводим"""
        print(f"✅ {message}")
    
    def warning(self, message: str):
        """Предупреждения - всегда выводим"""
        print(f"⚠️  {message}")
    
    def error(self, message: str):
        """Ошибки - всегда выводим в stderr"""
        print(f"❌ {message}", file=sys.stderr)
    
    def progress(self, current: int, total: int, message: str = ""):
        """Прогресс - только в verbose режиме"""
        if self.verbose:
            percent = (current / total) * 100 if total > 0 else 0
            print(f"📊 {message} {current}/{total} ({percent:.1f}%)")
    
    def step(self, step: str, message: str = ""):
        """Шаги процесса - только в verbose режиме"""
        if self.verbose:
            print(f"🔄 {step}: {message}")
    
    def section(self, title: str):
        """Заголовки секций - всегда выводим"""
        print(f"\n📋 {title}")
        print("-" * 50)


# Глобальный экземпляр логгера
logger = QuietLogger(verbose=False)


def set_verbose(verbose: bool = True):
    """Включить/выключить подробный вывод"""
    global logger
    logger.verbose = verbose
