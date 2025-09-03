#!/usr/bin/env python3
"""
🗑️ БЫСТРЫЙ СБРОС БД
==================

Удобный скрипт для сброса БД из корня backend.
Автор: Ириска 💖
"""

import sys
from pathlib import Path

# Добавляем путь к скриптам
sys.path.append(str(Path(__file__).parent / "scripts"))

from scripts.reset_database import reset_database

if __name__ == "__main__":
    print("🗑️ Быстрый сброс БД RM Agent...")
    reset_database()
