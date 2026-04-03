"""
CipherNest - Premium Emoji Configuration

Все Premium emoji ID уже заполнены из предоставленных данных.
Для замены — просто обновите числа в PREMIUM_EMOJI_IDS.
"""

# ==================== PREMIUM EMOJI IDs ====================
# ID получены из кастомных emoji пользователя seraviellex

PREMIUM_EMOJI_IDS = {
    # Основные
    "shield": "5017108172138087141",       # 🛡️
    "lock": "5240148791641787029",        # 🔒
    "unlock": "5429405838345265327",      # 🔓
    "key": "5330115548900501467",         # 🔑
    "gear": "5370935802844946281",        # ⚙️
    "chart": "5321119495085899242",       # 📊

    # Навигация
    "back": "6039539366177541657",        # ⬅️
    "check": "5886277285035644362",       # ✅
    "cross": "5210952531676504517",       # ❌
    "hourglass": "5451732530048802485",   # ⏳
    "clipboard": "5298501982556791386",   # 📋
    "repeat": "5978846612087114958",      # 🔄

    # Категории
    "encode": None,                        # 🔤 (нет в списке)
    "old_key": "5330100898767054648",     # 🗝️
    "encrypt": "5350619413533958825",     # 🔐
    "abacus": "5190741648237161191",      # 🧮
    "package": "5255860701133552970",     # 📦
    "grad": "5375163339154399459",        # 🎓
    "link": "5251364879691962538",        # 🔗
    "bar_chart": "5366222531504128151",   # 📊

    # Действия
    "outbox": "5445355530111437729",      # 📤
    "inbox": "5348345288480269633",       # 📬
    "dice": "5350314303352223876",        # 🎲
    "magnifier": "5188311512791393083",   # 🔎
    "file_sign": None,                     # ✍️ (нет в списке)
    "clipboard_check": "5213468029597261187",  # ✔️

    # Информация
    "book": "5226512880362332956",        # 📖
    "warning": "5447644880824181073",     # ⚠️
    "crystal_ball": "5271810272640643747", # 🔮
    "eyes": "5424885441100782420",        # 👀

    # Дополнительные
    "zap": "5431449001532594346",         # ⚡️
    "star": "5366486221021264181",        # ⭐️
    "fire": "5463154755054349837",        # 🔥
    "brain": "5237799019329105246",       # 🧠
    "computer": "5819127949558812112",    # ⌨️
    "phone": "5467539229468793355",       # 📞
    "rocket": "5922270584149908874",      # 🚀
    "target": "5350460637182993292",      # 🎯
    "trophy": "5890953718441970824",      # 🏆
    "gem": "5924856579663863746",         # 💎
    "crown": "5433758796289685818",       # 👑
    "sparkles": "5451636889717062286",    # ✨
    "dna": "5215662478712645753",         # 🧬
    "atom": "5888605518087326713",        # ⚛️
    "infinity": "5220198428033695755",    # ♾️
    "recycle": "5393399053033704955",     # ♻️
    "chart_up": "5319027450875753272",    # 📈
    "chart_down": "5318795574181377820",  # 📉
}


# Стандартные emoji для текстовых сообщений (fallback)
STANDARD_EMOJI = {
    "shield": "🛡️",
    "lock": "🔒",
    "unlock": "🔓",
    "key": "🔑",
    "gear": "⚙️",
    "chart": "📊",
    "back": "🔙",
    "check": "✅",
    "cross": "❌",
    "hourglass": "⏳",
    "clipboard": "📋",
    "repeat": "🔄",
    "encode": "🔤",
    "old_key": "🗝️",
    "encrypt": "🔐",
    "abacus": "🧮",
    "package": "📦",
    "grad": "🎓",
    "link": "🔗",
    "bar_chart": "📊",
    "outbox": "📤",
    "inbox": "📥",
    "dice": "🎲",
    "magnifier": "🔍",
    "file_sign": "✍️",
    "clipboard_check": "✅",
    "book": "📖",
    "warning": "⚠️",
    "crystal_ball": "🔮",
    "eyes": "👀",
    "zap": "⚡",
    "star": "⭐",
    "fire": "🔥",
    "brain": "🧠",
    "computer": "💻",
    "phone": "📱",
    "rocket": "🚀",
    "target": "🎯",
    "trophy": "🏆",
    "gem": "💎",
    "crown": "👑",
    "sparkles": "✨",
    "dna": "🧬",
    "atom": "⚛️",
    "infinity": "♾️",
    "recycle": "♻️",
    "chart_up": "📈",
    "chart_down": "📉",
}


def get_premium_emoji(name: str) -> str:
    """
    Получить emoji для текстовых сообщений.
    Всегда возвращает стандартный emoji (кастомные не работают в тексте).
    """
    return STANDARD_EMOJI.get(name, "")


def get_premium_emoji_id(name: str) -> str | None:
    """
    Получить ID кастомного emoji для использования в кнопках.
    Возвращает None если кастомный emoji не настроен.

    Использование:
        InlineKeyboardButton(
            text="Текст",
            callback_data="...",
            icon_custom_emoji_id=get_premium_emoji_id("shield")
        )
    """
    return PREMIUM_EMOJI_IDS.get(name)
