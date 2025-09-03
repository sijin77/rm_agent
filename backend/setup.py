#!/usr/bin/env python3
"""
🚀 БЫСТРЫЙ ЗАПУСК RM AGENT DATABASE SETUP
========================================

Удобный скрипт для запуска полного заполнения БД из корня backend.
Автор: Ириска 💖
"""

import sys
import asyncio
from pathlib import Path

# Добавляем путь к скриптам
sys.path.append(str(Path(__file__).parent / "scripts"))

from scripts.setup_database import setup_complete_database

if __name__ == "__main__":
    print("🎯 Быстрый запуск заполнения БД RM Agent...")
    asyncio.run(setup_complete_database())
