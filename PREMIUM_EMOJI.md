# 🎨 Настройка Premium Emoji

## Как это работает

Telegram Bot API поддерживает кастомные emoji **только в кнопках** InlineKeyboardButton через поле `icon_custom_emoji_id`. В текстовых сообщениях кастомные emoji **не работают** через стандартный HTML parse mode.

### Текущее поведение

- **Текстовые сообщения**: всегда используют стандартные emoji (🛡️🔒🔑 и т.д.)
- **Кнопки**: можно добавить кастомные emoji перед текстом

---

## Как получить ID кастомного emoji

### Способ 1: Через @RawDataBot

1. Откройте бота [@RawDataBot](https://t.me/RawDataBot)
2. Отправьте нужный emoji
3. Бот вернёт Json файл, найдите там "custom_emoji_id" и скопируйте ID

### Способ 2: Через API

1. Отправьте сообщение с кастомным emoji через Bot API
2. Получите update и найдите `custom_emoji_id` в entities

### Способ 3: Из собственного пака

1. Создайте пак кастомных emoji через @Stickers
2. ID можно получить через метод `getCustomEmojiStickers`

---

## Настройка

Откройте `app/premium_emoji.py` и замените `None` на ID:

```python
PREMIUM_EMOJI_IDS = {
    "shield": 53682538978389312,  # Ваш ID
    "lock": 53682538978389313,
    "key": 53682538978389314,
    # ... остальные
}
```

---

## Использование в кнопках

Чтобы добавить кастомный emoji в кнопку, используйте `icon_custom_emoji_id`:

```python
from aiogram.types import InlineKeyboardButton
from app.premium_emoji import get_premium_emoji_id

button = InlineKeyboardButton(
    text="Кодирование",
    callback_data="cat:encoding",
    icon_custom_emoji_id=get_premium_emoji_id("encode")  # Вернёт ID или None
)
```

Если `get_premium_emoji_id()` вернёт `None`, кнопка будет без иконки.

---

## Доступные категории

| Категория | Emoji | Где используется |
|-----------|-------|------------------|
| `shield` | 🛡️ | Главное меню, защита |
| `encode` | 🔤 | Кодирование |
| `old_key` | 🗝️ | Классические шифры |
| `encrypt` | 🔐 | Симметричное шифрование |
| `key` | 🔑 | Асимметричное шифрование |
| `abacus` | 🧮 | Хеши |
| `package` | 📦 | Утилиты |
| `grad` | 🎓 | Обучение |
| `link` | 🔗 | Цепочка |
| `bar_chart` | 📊 | Статистика |
| `back` | 🔙 | Кнопка назад |
| `check` | ✅ | Успех |
| `cross` | ❌ | Ошибка |
| `hourglass` | ⏳ | Обработка |
| `clipboard` | 📋 | Копирование |
| `repeat` | 🔄 | Новая операция |
| `outbox` | 📤 | Кодировать |
| `inbox` | 📥 | Декодировать |
| `dice` | 🎲 | Генерация |
| `magnifier` | 🔍 | Поиск/декодирование |
| `file_sign` | ✍️ | Подписать |
| `clipboard_check` | ✅ | Проверить подпись |
| `book` | 📖 | Помощь |
| `warning` | ⚠️ | Предупреждение |
| `crystal_ball` | 🔮 | Автодетект |

---

## Требования

Для использования кастомных emoji в кнопках:

- У владельца бота должна быть **Telegram Premium** подписка
- Или бот должен купить **дополнительные username** на Fragment

Без этого `icon_custom_emoji_id` будет проигнорирован Telegram.

---

## Быстрый старт (без Premium)

Ничего не меняйте — бот будет работать со стандартными emoji. Они отлично выглядят и работают всегда!
