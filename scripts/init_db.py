#!/usr/bin/env python3
"""Initialize database with demo data."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, init_db
from app.models.models import ItemType
from app.schemas import ItemCreate, PageCreate
from app.crud import create_item, get_items

# Demo data
DEMO_INCIDENTS = [
    {
        "title": "Потекла рубашка",
        "pages": [
            {
                "title": "Диагностика проблемы",
                "time": "5 минут",
                "image": "https://placehold.co/600x400/e74c3c/white?text=Диагностика",
                "actions": [
                    "Остановить линию розлива",
                    "Определить место утечки визуально",
                    "Проверить давление в системе",
                    "Оценить объём утечки"
                ]
            },
            {
                "title": "Устранение утечки",
                "time": "15 минут",
                "image": "https://placehold.co/600x400/e67e22/white?text=Ремонт",
                "actions": [
                    "Перекрыть подачу воды",
                    "Слить остатки из рубашки",
                    "Проверить уплотнители",
                    "Заменить повреждённые прокладки",
                    "Закрутить крепёжные болты"
                ]
            },
            {
                "title": "Проверка и запуск",
                "time": "10 минут",
                "image": "https://placehold.co/600x400/27ae60/white?text=Запуск",
                "actions": [
                    "Открыть подачу воды",
                    "Проверить герметичность под давлением",
                    "Запустить тестовый цикл",
                    "Убедиться в отсутствии утечек",
                    "Возобновить производство"
                ]
            }
        ]
    },
    {
        "title": "Застряла этикетка",
        "pages": [
            {
                "title": "Остановка и доступ",
                "time": "3 минуты",
                "image": "https://placehold.co/600x400/e74c3c/white?text=СТОП",
                "actions": [
                    "Нажать кнопку остановки этикетировщика",
                    "Дождаться полной остановки",
                    "Открыть защитный кожух",
                    "Надеть защитные перчатки"
                ]
            },
            {
                "title": "Устранение замятия",
                "time": "7 минут",
                "image": "https://placehold.co/600x400/9b59b6/white?text=Очистка",
                "actions": [
                    "Аккуратно удалить застрявшую этикетку",
                    "Проверить ролики на наличие остатков клея",
                    "Очистить направляющие",
                    "Проверить натяжение ленты"
                ]
            },
            {
                "title": "Запуск оборудования",
                "time": "5 минут",
                "image": "https://placehold.co/600x400/27ae60/white?text=Запуск",
                "actions": [
                    "Закрыть защитный кожух",
                    "Выполнить пробную этикетировку",
                    "Проверить качество наклейки",
                    "Запустить в рабочем режиме"
                ]
            }
        ]
    },
    {
        "title": "Сбой конвейера",
        "pages": [
            {
                "title": "Аварийная остановка",
                "time": "2 минуты",
                "image": "https://placehold.co/600x400/c0392b/white?text=АВАРИЯ",
                "actions": [
                    "Нажать аварийную кнопку СТОП",
                    "Убедиться в безопасности персонала",
                    "Отключить питание конвейера",
                    "Включить аварийное освещение"
                ]
            },
            {
                "title": "Диагностика неисправности",
                "time": "15 минут",
                "image": "https://placehold.co/600x400/3498db/white?text=Диагностика",
                "actions": [
                    "Проверить датчики движения",
                    "Осмотреть приводной ремень",
                    "Проверить натяжение цепи",
                    "Проверить состояние подшипников",
                    "Проверить электрические соединения"
                ]
            },
            {
                "title": "Ремонт и обслуживание",
                "time": "20 минут",
                "image": "https://placehold.co/600x400/e67e22/white?text=Ремонт",
                "actions": [
                    "Заменить неисправные компоненты",
                    "Смазать подшипники",
                    "Отрегулировать натяжение",
                    "Очистить датчики"
                ]
            },
            {
                "title": "Тестирование и запуск",
                "time": "8 минут",
                "image": "https://placehold.co/600x400/27ae60/white?text=Тест",
                "actions": [
                    "Включить питание",
                    "Выполнить тестовый запуск на малой скорости",
                    "Проверить работу всех датчиков",
                    "Запустить на рабочей скорости",
                    "Записать в журнал инцидентов"
                ]
            }
        ]
    }
]

DEMO_INSTRUCTIONS = [
    {
        "title": "Запуск линии розлива",
        "pages": [
            {
                "title": "Подготовка к запуску",
                "time": "3 минуты",
                "image": "https://placehold.co/600x400/3498db/white?text=Подготовка",
                "actions": [
                    "Проверить наличие тары на складе",
                    "Убедиться в чистоте линии",
                    "Проверить уровень продукта в резервуаре",
                    "Включить общее питание линии"
                ]
            },
            {
                "title": "Запуск оборудования",
                "time": "5 минут",
                "image": "https://placehold.co/600x400/2980b9/white?text=Запуск",
                "actions": [
                    "Включить подачу воды",
                    "Активировать конвейер на малой скорости",
                    "Запустить дозаторы",
                    "Включить этикетировщик"
                ]
            },
            {
                "title": "Контроль качества",
                "time": "2 минуты",
                "image": "https://placehold.co/600x400/27ae60/white?text=Контроль",
                "actions": [
                    "Проверить первые 3 образца",
                    "Измерить объём розлива",
                    "Проверить качество этикетки",
                    "Начать серийное производство"
                ]
            }
        ]
    },
    {
        "title": "Ежедневное ТО конвейера",
        "pages": [
            {
                "title": "Визуальный осмотр",
                "time": "5 минут",
                "image": "https://placehold.co/600x400/9b59b6/white?text=Осмотр",
                "actions": [
                    "Осмотреть ленту на предмет повреждений",
                    "Проверить состояние роликов",
                    "Осмотреть натяжные механизмы",
                    "Проверить защитные кожухи"
                ]
            },
            {
                "title": "Очистка и смазка",
                "time": "15 минут",
                "image": "https://placehold.co/600x400/1abc9c/white?text=Смазка",
                "actions": [
                    "Очистить ленту от загрязнений",
                    "Протереть датчики",
                    "Смазать подшипники",
                    "Очистить фотоэлементы"
                ]
            },
            {
                "title": "Проверка и документация",
                "time": "10 минут",
                "image": "https://placehold.co/600x400/34495e/white?text=Журнал",
                "actions": [
                    "Проверить натяжение ленты",
                    "Протестировать работу датчиков",
                    "Выполнить пробный запуск",
                    "Записать результаты в журнал ТО"
                ]
            }
        ]
    },
    {
        "title": "Санитарная обработка линии",
        "pages": [
            {
                "title": "Подготовка к обработке",
                "time": "5 минут",
                "image": "https://placehold.co/600x400/16a085/white?text=Подготовка",
                "actions": [
                    "Остановить производство",
                    "Слить остатки продукции",
                    "Подготовить дезраствор по инструкции",
                    "Надеть защитную одежду и перчатки"
                ]
            },
            {
                "title": "Промывка системы",
                "time": "20 минут",
                "image": "https://placehold.co/600x400/3498db/white?text=Промывка",
                "actions": [
                    "Промыть систему чистой водой (5 мин)",
                    "Залить дезраствор в систему",
                    "Включить циркуляцию на 15 минут",
                    "Слить дезраствор"
                ]
            },
            {
                "title": "Финальная промывка",
                "time": "15 минут",
                "image": "https://placehold.co/600x400/2ecc71/white?text=Финал",
                "actions": [
                    "Промыть чистой водой (10 мин)",
                    "Взять пробу воды на анализ",
                    "Проверить pH (норма 6.5-7.5)",
                    "При необходимости повторить промывку"
                ]
            },
            {
                "title": "Документирование",
                "time": "5 минут",
                "image": "https://placehold.co/600x400/34495e/white?text=Документы",
                "actions": [
                    "Записать время обработки",
                    "Указать использованный раствор",
                    "Записать результаты pH-теста",
                    "Подписать журнал санобработки"
                ]
            }
        ]
    }
]


def init_demo_data():
    """Initialize database with demo data."""
    print("Initializing database...")
    init_db()

    db = SessionLocal()
    try:
        # Check if data already exists
        existing = get_items(db, limit=1)
        if existing:
            print("Database already contains data. Skipping demo data insertion.")
            return

        print("Adding demo incidents...")
        for incident_data in DEMO_INCIDENTS:
            item = ItemCreate(
                title=incident_data["title"],
                item_type=ItemType.INCIDENT,
                pages=[
                    PageCreate(
                        title=p["title"],
                        time=p["time"],
                        image=p["image"],
                        actions=p["actions"]
                    )
                    for p in incident_data["pages"]
                ]
            )
            create_item(db, item)
            print(f"  + {incident_data['title']}")

        print("Adding demo instructions...")
        for instruction_data in DEMO_INSTRUCTIONS:
            item = ItemCreate(
                title=instruction_data["title"],
                item_type=ItemType.INSTRUCTION,
                pages=[
                    PageCreate(
                        title=p["title"],
                        time=p["time"],
                        image=p["image"],
                        actions=p["actions"]
                    )
                    for p in instruction_data["pages"]
                ]
            )
            create_item(db, item)
            print(f"  + {instruction_data['title']}")

        print("\nDemo data initialized successfully!")
        print(f"  - {len(DEMO_INCIDENTS)} incidents")
        print(f"  - {len(DEMO_INSTRUCTIONS)} instructions")

    finally:
        db.close()


if __name__ == "__main__":
    init_demo_data()
