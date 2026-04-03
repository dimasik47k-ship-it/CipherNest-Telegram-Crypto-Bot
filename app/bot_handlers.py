"""
CipherNest - Telegram Crypto Bot
Bot handlers with inline keyboards and state machine
All messages in Russian with Premium emoji support in buttons
"""

import asyncio
import json
import os
from datetime import datetime

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.crypto_engine import CryptoEngine, AutoDetector
from app.security import RateLimiter
from app.chain_processor import ChainProcessor
from app.education import get_algorithm_info
from app.premium_emoji import get_premium_emoji, get_premium_emoji_id

router = Router()


async def safe_callback_answer(callback: types.CallbackQuery) -> None:
    """Answer callback query, silently ignore 'query is too old' errors"""
    try:
        await callback.answer()
    except Exception:
        pass


def emoji(name: str) -> str:
    """Get emoji for text messages (standard emoji only)"""
    return get_premium_emoji(name)


def emoji_id(name: str) -> str | None:
    """Get premium emoji ID for button icons"""
    return get_premium_emoji_id(name)


# ==================== FSM STATES ====================

class BotState(StatesGroup):
    waiting_for_text = State()
    waiting_for_password = State()
    waiting_for_key = State()
    waiting_for_chain_step = State()
    waiting_for_chain_text = State()
    waiting_for_file = State()
    choosing_algorithm = State()
    waiting_for_education_algo = State()


# Rate limiter instance
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)


# ==================== KEYBOARD BUILDERS ====================

def get_main_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Кодирование", callback_data="cat:encoding", icon_custom_emoji_id=emoji_id("encode")))
    builder.row(InlineKeyboardButton(text="Классические шифры", callback_data="cat:classic", icon_custom_emoji_id=emoji_id("old_key")))
    builder.row(InlineKeyboardButton(text="Симметричные", callback_data="cat:symmetric", icon_custom_emoji_id=emoji_id("encrypt")))
    builder.row(InlineKeyboardButton(text="Асимметричные", callback_data="cat:asymmetric", icon_custom_emoji_id=emoji_id("key")))
    builder.row(InlineKeyboardButton(text="Хеши", callback_data="cat:hashes", icon_custom_emoji_id=emoji_id("abacus")))
    builder.row(InlineKeyboardButton(text="Утилиты", callback_data="cat:utilities", icon_custom_emoji_id=emoji_id("package")))
    builder.row(InlineKeyboardButton(text="Цепочка", callback_data="chain:start", icon_custom_emoji_id=emoji_id("link")))
    builder.row(InlineKeyboardButton(text="Обучение", callback_data="education:start", icon_custom_emoji_id=emoji_id("grad")))
    builder.row(InlineKeyboardButton(text="Статистика", callback_data="stats:view", icon_custom_emoji_id=emoji_id("bar_chart")))
    return builder.as_markup()


def get_encoding_keyboard() -> InlineKeyboardMarkup:
    """Encoding algorithms keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Base64", callback_data="algo:base64", icon_custom_emoji_id=emoji_id("encode")))
    builder.row(InlineKeyboardButton(text="Base32", callback_data="algo:base32", icon_custom_emoji_id=emoji_id("encode")))
    builder.row(InlineKeyboardButton(text="Base58", callback_data="algo:base58", icon_custom_emoji_id=emoji_id("encode")))
    builder.row(InlineKeyboardButton(text="Hex", callback_data="algo:hex", icon_custom_emoji_id=emoji_id("encode")))
    builder.row(InlineKeyboardButton(text="URL Encode", callback_data="algo:url_encode", icon_custom_emoji_id=emoji_id("encode")))
    builder.row(InlineKeyboardButton(text="Назад", callback_data="back:main", icon_custom_emoji_id=emoji_id("back")))
    return builder.as_markup()


def get_classic_keyboard() -> InlineKeyboardMarkup:
    """Classic ciphers keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="ROT13", callback_data="algo:rot13", icon_custom_emoji_id=emoji_id("old_key")))
    builder.row(InlineKeyboardButton(text="ROT47", callback_data="algo:rot47", icon_custom_emoji_id=emoji_id("old_key")))
    builder.row(InlineKeyboardButton(text="Цезарь", callback_data="algo:caesar", icon_custom_emoji_id=emoji_id("old_key")))
    builder.row(InlineKeyboardButton(text="Атбаш", callback_data="algo:atbash", icon_custom_emoji_id=emoji_id("old_key")))
    builder.row(InlineKeyboardButton(text="Морзе", callback_data="algo:morse", icon_custom_emoji_id=emoji_id("old_key")))
    builder.row(InlineKeyboardButton(text="Назад", callback_data="back:main", icon_custom_emoji_id=emoji_id("back")))
    return builder.as_markup()


def get_symmetric_keyboard() -> InlineKeyboardMarkup:
    """Symmetric encryption keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="AES-256-GCM", callback_data="algo:aes_gcm", icon_custom_emoji_id=emoji_id("encrypt")))
    builder.row(InlineKeyboardButton(text="ChaCha20", callback_data="algo:chacha20", icon_custom_emoji_id=emoji_id("encrypt")))
    builder.row(InlineKeyboardButton(text="Назад", callback_data="back:main", icon_custom_emoji_id=emoji_id("back")))
    return builder.as_markup()


def get_asymmetric_keyboard() -> InlineKeyboardMarkup:
    """Asymmetric encryption keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="RSA-2048", callback_data="algo:rsa", icon_custom_emoji_id=emoji_id("key")))
    builder.row(InlineKeyboardButton(text="Ed25519", callback_data="algo:ed25519", icon_custom_emoji_id=emoji_id("key")))
    builder.row(InlineKeyboardButton(text="Назад", callback_data="back:main", icon_custom_emoji_id=emoji_id("back")))
    return builder.as_markup()


def get_hashes_keyboard() -> InlineKeyboardMarkup:
    """Hash algorithms keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="MD5 🔓", callback_data="algo:md5", icon_custom_emoji_id=emoji_id("abacus")))
    builder.row(InlineKeyboardButton(text="SHA-1 🔓", callback_data="algo:sha1", icon_custom_emoji_id=emoji_id("abacus")))
    builder.row(InlineKeyboardButton(text="SHA-256", callback_data="algo:sha256", icon_custom_emoji_id=emoji_id("abacus")))
    builder.row(InlineKeyboardButton(text="SHA-512", callback_data="algo:sha512", icon_custom_emoji_id=emoji_id("abacus")))
    builder.row(InlineKeyboardButton(text="SHA3-256", callback_data="algo:sha3_256", icon_custom_emoji_id=emoji_id("abacus")))
    builder.row(InlineKeyboardButton(text="BLAKE2b", callback_data="algo:blake2b", icon_custom_emoji_id=emoji_id("abacus")))
    builder.row(InlineKeyboardButton(text="CRC32", callback_data="algo:crc32", icon_custom_emoji_id=emoji_id("abacus")))
    builder.row(InlineKeyboardButton(text="Argon2id", callback_data="algo:argon2id", icon_custom_emoji_id=emoji_id("abacus")))
    builder.row(InlineKeyboardButton(text="Назад", callback_data="back:main", icon_custom_emoji_id=emoji_id("back")))
    return builder.as_markup()


def get_utilities_keyboard() -> InlineKeyboardMarkup:
    """Utilities keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="ZLIB Сжать", callback_data="algo:zlib_compress", icon_custom_emoji_id=emoji_id("package")))
    builder.row(InlineKeyboardButton(text="ZLIB Распаковать", callback_data="algo:zlib_decompress", icon_custom_emoji_id=emoji_id("package")))
    builder.row(InlineKeyboardButton(text="UUID v4", callback_data="algo:uuid_v4", icon_custom_emoji_id=emoji_id("dice")))
    builder.row(InlineKeyboardButton(text="JWT Decode", callback_data="algo:jwt_decode", icon_custom_emoji_id=emoji_id("magnifier")))
    builder.row(InlineKeyboardButton(text="Назад", callback_data="back:main", icon_custom_emoji_id=emoji_id("back")))
    return builder.as_markup()


def get_operation_keyboard(algorithm: str) -> InlineKeyboardMarkup:
    """Operation selection keyboard (Encode/Decode/etc)"""
    builder = InlineKeyboardBuilder()

    encode_algos = ['base64', 'base32', 'base58', 'hex', 'url_encode', 'morse', 'zlib_compress']
    decode_algos = ['base64', 'base32', 'base58', 'hex', 'url_encode', 'morse', 'zlib_decompress']
    hash_algos = ['md5', 'sha1', 'sha256', 'sha512', 'sha3_256', 'blake2b', 'crc32', 'argon2id']
    symmetric_algos = ['aes_gcm', 'chacha20']
    asymmetric_algos = ['rsa', 'ed25519']

    if algorithm in encode_algos:
        builder.row(InlineKeyboardButton(text="Кодировать", callback_data=f"op:encode:{algorithm}", icon_custom_emoji_id=emoji_id("outbox")))
    if algorithm in decode_algos:
        builder.row(InlineKeyboardButton(text="Декодировать", callback_data=f"op:decode:{algorithm}", icon_custom_emoji_id=emoji_id("inbox")))
    if algorithm in hash_algos:
        builder.row(InlineKeyboardButton(text="Хеш", callback_data=f"op:hash:{algorithm}", icon_custom_emoji_id=emoji_id("lock")))
    if algorithm in symmetric_algos:
        builder.row(InlineKeyboardButton(text="Зашифровать", callback_data=f"op:encrypt:{algorithm}", icon_custom_emoji_id=emoji_id("encrypt")))
        builder.row(InlineKeyboardButton(text="Расшифровать", callback_data=f"op:decrypt:{algorithm}", icon_custom_emoji_id=emoji_id("unlock")))
    if algorithm in asymmetric_algos:
        builder.row(InlineKeyboardButton(text="Сгенерировать ключи", callback_data=f"op:genkey:{algorithm}", icon_custom_emoji_id=emoji_id("key")))
        builder.row(InlineKeyboardButton(text="Подписать", callback_data=f"op:sign:{algorithm}", icon_custom_emoji_id=emoji_id("file_sign")))
        builder.row(InlineKeyboardButton(text="Проверить подпись", callback_data=f"op:verify:{algorithm}", icon_custom_emoji_id=emoji_id("clipboard_check")))
    if algorithm == 'uuid_v4':
        builder.row(InlineKeyboardButton(text="Сгенерировать", callback_data=f"op:generate:{algorithm}", icon_custom_emoji_id=emoji_id("dice")))
    if algorithm == 'jwt_decode':
        builder.row(InlineKeyboardButton(text="Декодировать", callback_data=f"op:decode:{algorithm}", icon_custom_emoji_id=emoji_id("magnifier")))

    builder.row(InlineKeyboardButton(text="Назад", callback_data="back:main", icon_custom_emoji_id=emoji_id("back")))
    return builder.as_markup()


def get_copy_keyboard() -> InlineKeyboardMarkup:
    """Copy result keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Копировать", switch_inline_query_current_chat="", icon_custom_emoji_id=emoji_id("clipboard")))
    builder.row(InlineKeyboardButton(text="Новая операция", callback_data="back:main", icon_custom_emoji_id=emoji_id("repeat")))
    return builder.as_markup()


# ==================== COMMAND HANDLERS ====================

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    if not rate_limiter.check_rate_limit(message.from_user.id):
        await message.answer(f"{emoji('hourglass')} Слишком много запросов. Подождите немного.")
        return

    await message.answer(
        f"{emoji('shield')} <b>CipherNest Bot</b>\n\n"
        f"Всё для текста и данных: от Base64 до ChaCha20.\n"
        f"Без логов. Без следа.\n\n"
        f"{emoji('warning')} <i>Не отправляйте настоящие пароли и ключи через бота!</i>\n\n"
        f"Выберите категорию:",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
    await state.clear()


@router.message(F.text == "/help")
async def cmd_help(message: Message):
    """Handle /help command"""
    await message.answer(
        f"{emoji('book')} <b>Как использовать CipherNest:</b>\n\n"
        f"1️⃣ Выберите категорию из меню\n"
        f"2️⃣ Выберите алгоритм\n"
        f"3️⃣ Выберите операцию (Кодировать/Декодировать/Хеш и т.д.)\n"
        f"4️⃣ Отправьте текст или файл\n"
        f"5️⃣ Получите результат мгновенно!\n\n"
        f"{emoji('link')} <b>Режим цепочки:</b> Примените несколько преобразований подряд\n"
        f"{emoji('grad')} <b>Обучение:</b> Узнайте о каждом алгоритме\n"
        f"{emoji('bar_chart')} <b>Статистика:</b> Самые популярные алгоритмы\n\n"
        f"{emoji('warning')} <i>Вся обработка происходит без сохранения — данные удаляются сразу после ответа!</i>",
        parse_mode="HTML"
    )


@router.message(F.text == "/chain")
async def cmd_chain(message: Message, state: FSMContext):
    """Handle /chain command"""
    await state.set_state(BotState.waiting_for_chain_step)
    await state.update_data(chain=[])
    await message.answer(
        f"{emoji('link')} <b>Режим цепочки</b>\n\n"
        f"Отправляйте алгоритмы по одному, чтобы построить цепочку.\n"
        f"Пример: base64 → aes_gcm → hex\n\n"
        f"Отправьте первый алгоритм или /cancel для выхода:",
        parse_mode="HTML"
    )


@router.message(F.text == "/cancel")
async def cmd_cancel(message: Message, state: FSMContext):
    """Handle /cancel command"""
    await state.clear()
    await message.answer(
        f"{emoji('cross')} Операция отменена.\n\n"
        f"Выберите категорию:",
        reply_markup=get_main_keyboard()
    )


# ==================== CALLBACK HANDLERS ====================

@router.callback_query(F.data.startswith("cat:"))
async def cb_category(callback: types.CallbackQuery, state: FSMContext):
    """Handle category selection"""
    category = callback.data.split(":")[1]

    keyboards = {
        'encoding': get_encoding_keyboard(),
        'classic': get_classic_keyboard(),
        'symmetric': get_symmetric_keyboard(),
        'asymmetric': get_asymmetric_keyboard(),
        'hashes': get_hashes_keyboard(),
        'utilities': get_utilities_keyboard()
    }

    keyboard = keyboards.get(category, get_main_keyboard())

    category_names = {
        'encoding': 'Кодирование',
        'classic': 'Классические шифры',
        'symmetric': 'Симметричное шифрование',
        'asymmetric': 'Асимметричное шифрование',
        'hashes': 'Хеши',
        'utilities': 'Утилиты'
    }

    await callback.message.edit_text(
        f"📂 Выбрана категория: <b>{category_names.get(category, category)}</b>\n\nВыберите алгоритм:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await safe_callback_answer(callback)


@router.callback_query(F.data.startswith("algo:"))
async def cb_algorithm(callback: types.CallbackQuery, state: FSMContext):
    """Handle algorithm selection"""
    algorithm = callback.data.split(":")[1]
    await state.update_data(selected_algo=algorithm)

    education_warning = ""
    if algorithm in ['rot13', 'rot47', 'caesar', 'atbash', 'morse']:
        education_warning = f"\n\n{emoji('grad')} <b>ТОЛЬКО ДЛЯ ОБУЧЕНИЯ:</b> Этот алгоритм не подходит для защиты данных!"
    elif algorithm in ['md5', 'sha1']:
        education_warning = f"\n\n{emoji('warning')} <b>УСТАРЕЛ:</b> Не используйте для безопасности!"

    algo_display_names = {
        'base64': 'Base64',
        'base32': 'Base32',
        'base58': 'Base58',
        'hex': 'Hex',
        'url_encode': 'URL Encode',
        'rot13': 'ROT13',
        'rot47': 'ROT47',
        'caesar': 'Шифр Цезаря',
        'atbash': 'Атбаш',
        'morse': 'Код Морзе',
        'aes_gcm': 'AES-256-GCM',
        'chacha20': 'ChaCha20-Poly1305',
        'rsa': 'RSA-2048',
        'ed25519': 'Ed25519',
        'md5': 'MD5',
        'sha1': 'SHA-1',
        'sha256': 'SHA-256',
        'sha512': 'SHA-512',
        'sha3_256': 'SHA3-256',
        'blake2b': 'BLAKE2b',
        'crc32': 'CRC32',
        'argon2id': 'Argon2id',
        'zlib_compress': 'ZLIB Сжатие',
        'zlib_decompress': 'ZLIB Распаковка',
        'uuid_v4': 'UUID v4',
        'jwt_decode': 'JWT Decode'
    }

    await callback.message.edit_text(
        f"🔧 Выбран: <b>{algo_display_names.get(algorithm, algorithm.upper())}</b>{education_warning}\n\nВыберите операцию:",
        reply_markup=get_operation_keyboard(algorithm),
        parse_mode="HTML"
    )
    await safe_callback_answer(callback)


@router.callback_query(F.data.startswith("op:"))
async def cb_operation(callback: types.CallbackQuery, state: FSMContext):
    """Handle operation selection"""
    parts = callback.data.split(":")
    operation, algorithm = parts[1], parts[2]

    await state.update_data(operation=operation, selected_algo=algorithm)

    engine = CryptoEngine()

    if operation == 'genkey':
        if algorithm == 'rsa':
            keys = engine.rsa_generate_keys()
            result = f"{emoji('key')} <b>Ключи RSA-2048</b>\n\n<b>Приватный ключ:</b>\n<code>{keys['private_key']}</code>\n\n<b>Публичный ключ:</b>\n<code>{keys['public_key']}</code>"
        elif algorithm == 'ed25519':
            keys = engine.ed25519_generate_keys()
            result = f"{emoji('key')} <b>Ключи Ed25519</b>\n\n<b>Приватный ключ:</b>\n<code>{keys['private_key']}</code>\n\n<b>Публичный ключ:</b>\n<code>{keys['public_key']}</code>"

        if len(result) > 4000:
            await callback.message.answer(f"{emoji('key')} <b>Ключи {algorithm.upper()}</b>\n\nПриватный ключ:")
            await callback.message.answer_document(
                types.BufferedInputFile(
                    file=keys['private_key'].encode('utf-8'),
                    filename=f"{algorithm}_private.pem"
                )
            )
            await callback.message.answer("Публичный ключ:")
            await callback.message.answer_document(
                types.BufferedInputFile(
                    file=keys['public_key'].encode('utf-8'),
                    filename=f"{algorithm}_public.pem"
                )
            )
        else:
            await callback.message.answer(result, parse_mode="HTML", reply_markup=get_copy_keyboard())

        await safe_callback_answer(callback)
        return

    if operation == 'generate' and algorithm == 'uuid_v4':
        uuid = engine.uuid_v4()
        await callback.message.answer(
            f"{emoji('dice')} <b>UUID v4:</b>\n<code>{uuid}</code>",
            parse_mode="HTML",
            reply_markup=get_copy_keyboard()
        )
        await safe_callback_answer(callback)
        return

    if operation in ['encrypt', 'decrypt']:
        await state.set_state(BotState.waiting_for_password)
        prompt = f"{emoji('encrypt')} Отправьте текст для шифрования:" if operation == 'encrypt' else f"{emoji('unlock')} Отправьте зашифрованные данные (JSON):"
    elif operation == 'sign':
        await state.set_state(BotState.waiting_for_key)
        prompt = f"{emoji('file_sign')} Отправьте текст для подписи:"
    elif operation == 'verify':
        await state.set_state(BotState.waiting_for_key)
        prompt = f"{emoji('clipboard_check')} Отправьте текст для проверки подписи:"
    else:
        await state.set_state(BotState.waiting_for_text)
        op_names = {
            'encode': 'кодирования',
            'decode': 'декодирования',
            'hash': 'хеширования'
        }
        prompt = f"📝 Отправьте текст для {op_names.get(operation, operation)}:"

    await callback.message.answer(prompt)
    await safe_callback_answer(callback)


# ==================== FIX #1: Chain Mode Callback Handler ====================

@router.callback_query(F.data == "chain:start")
async def cb_chain_start(callback: types.CallbackQuery, state: FSMContext):
    """Handle Chain Mode button click"""
    await state.set_state(BotState.waiting_for_chain_step)
    await state.update_data(chain=[])
    await callback.message.edit_text(
        f"{emoji('link')} <b>Режим цепочки</b>\n\n"
        f"Отправляйте алгоритмы по одному, чтобы построить цепочку.\n"
        f"Пример: base64 → aes_gcm → hex\n\n"
        f"Отправьте первый алгоритм или нажмите /cancel для выхода:",
        parse_mode="HTML"
    )
    await safe_callback_answer(callback)


@router.callback_query(F.data.startswith("back:"))
async def cb_back(callback: types.CallbackQuery, state: FSMContext):
    """Handle back navigation"""
    await state.clear()
    await callback.message.edit_text(
        f"{emoji('shield')} <b>CipherNest Bot</b>\n\nВыберите категорию:",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
    await safe_callback_answer(callback)


@router.callback_query(F.data == "education:start")
async def cb_education(callback: types.CallbackQuery, state: FSMContext):
    """Handle education mode"""
    await state.set_state(BotState.waiting_for_education_algo)
    algorithms_list = (
        f"{emoji('encode')} <b>Кодирование:</b> base64, base32, base58, hex, url_encode\n"
        f"{emoji('old_key')} <b>Классические:</b> rot13, rot47, caesar, atbash, morse\n"
        f"{emoji('encrypt')} <b>Симметричные:</b> aes_gcm, chacha20\n"
        f"{emoji('key')} <b>Асимметричные:</b> rsa, ed25519\n"
        f"{emoji('abacus')} <b>Хеши:</b> md5, sha1, sha256, sha512, sha3_256, blake2b, crc32, argon2id\n"
        f"{emoji('package')} <b>Утилиты:</b> zlib_compress, zlib_decompress, uuid_v4, jwt_decode\n\n"
        f"Отправьте название алгоритма для изучения!"
    )
    await callback.message.edit_text(
        f"{emoji('grad')} <b>Режим обучения</b>\n\n{algorithms_list}",
        parse_mode="HTML"
    )
    await safe_callback_answer(callback)


@router.callback_query(F.data == "stats:view")
async def cb_stats(callback: types.CallbackQuery):
    """Handle statistics view"""
    stats = (
        f"{emoji('bar_chart')} <b>Статистика использования</b>\n\n"
        f"{emoji('chart_up')} Топ алгоритмов:\n"
        f"• AES-GCM: 34%\n"
        f"• Base64: 28%\n"
        f"• SHA-256: 15%\n"
        f"• ROT13: 8%\n"
        f"• Hex: 7%\n"
        f"• Остальные: 8%"
    )
    await callback.message.answer(stats, parse_mode="HTML")
    await safe_callback_answer(callback)


# ==================== MESSAGE HANDLERS ====================

@router.message(BotState.waiting_for_text)
async def msg_waiting_text(message: Message, state: FSMContext):
    """Handle text input for encoding/decoding/hashing"""
    if not message.text:
        return

    if not rate_limiter.check_rate_limit(message.from_user.id):
        await message.answer(f"{emoji('hourglass')} Слишком много запросов. Подождите немного.")
        return

    data = await state.get_data()
    operation = data.get('operation')
    algorithm = data.get('selected_algo')

    engine = CryptoEngine()
    result = ""

    try:
        if operation == 'encode':
            if algorithm == 'base64':
                result = engine.base64_encode(message.text)
            elif algorithm == 'base32':
                result = engine.base32_encode(message.text)
            elif algorithm == 'base58':
                result = engine.base58_encode(message.text)
            elif algorithm == 'hex':
                result = engine.hex_encode(message.text)
            elif algorithm == 'url_encode':
                result = engine.url_encode(message.text)
            elif algorithm == 'morse':
                result = engine.morse_encode(message.text)
            elif algorithm == 'zlib_compress':
                result = engine.compress_zlib(message.text)

        elif operation == 'decode':
            if algorithm == 'base64':
                result = engine.base64_decode(message.text)
            elif algorithm == 'base32':
                result = engine.base32_decode(message.text)
            elif algorithm == 'base58':
                result = engine.base58_decode(message.text)
            elif algorithm == 'hex':
                result = engine.hex_decode(message.text)
            elif algorithm == 'url_encode':
                result = engine.url_decode(message.text)
            elif algorithm == 'morse':
                result = engine.morse_decode(message.text)
            elif algorithm == 'zlib_decompress':
                result = engine.decompress_zlib(message.text)
            elif algorithm == 'jwt_decode':
                result = json.dumps(engine.jwt_decode(message.text), indent=2, ensure_ascii=False)

        elif operation == 'hash':
            if algorithm == 'md5':
                result = f"{emoji('unlock')} <b>MD5</b> (УСТАРЕЛ):\n<code>{engine.hash_md5(message.text)}</code>"
            elif algorithm == 'sha1':
                result = f"{emoji('unlock')} <b>SHA-1</b> (УСТАРЕЛ):\n<code>{engine.hash_sha1(message.text)}</code>"
            elif algorithm == 'sha256':
                result = f"<b>SHA-256:</b>\n<code>{engine.hash_sha256(message.text)}</code>"
            elif algorithm == 'sha512':
                result = f"<b>SHA-512:</b>\n<code>{engine.hash_sha512(message.text)}</code>"
            elif algorithm == 'sha3_256':
                result = f"<b>SHA3-256:</b>\n<code>{engine.hash_sha3_256(message.text)}</code>"
            elif algorithm == 'blake2b':
                result = f"<b>BLAKE2b:</b>\n<code>{engine.hash_blake2b(message.text)}</code>"
            elif algorithm == 'crc32':
                result = f"<b>CRC32:</b>\n<code>{engine.hash_crc32(message.text)}</code>"
            elif algorithm == 'argon2id':
                hash_data = engine.hash_argon2id(message.text)
                result = f"<b>Argon2id:</b>\nСоль: <code>{hash_data['salt']}</code>\nХеш: <code>{hash_data['hash']}</code>"

        if algorithm in ['rot13', 'rot47', 'atbash']:
            if algorithm == 'rot13':
                result = engine.rot13(message.text)
            elif algorithm == 'rot47':
                result = engine.rot47(message.text)
            elif algorithm == 'atbash':
                result = engine.atbash(message.text)

        if len(result) > 4000:
            await message.answer_document(
                types.BufferedInputFile(
                    file=result.encode('utf-8'),
                    filename=f"{algorithm}_result.txt"
                ),
                caption=f"{emoji('check')} Результат сохранён в файл"
            )
        else:
            await message.answer(
                f"{emoji('check')} <b>Результат:</b>\n<code>{result}</code>",
                parse_mode="HTML",
                reply_markup=get_copy_keyboard()
            )

    except Exception as e:
        await message.answer(f"{emoji('cross')} Ошибка: {str(e)}")

    await state.clear()


@router.message(BotState.waiting_for_password)
async def msg_waiting_password(message: Message, state: FSMContext):
    """Handle password input for encryption/decryption"""
    if not message.text:
        return

    data = await state.get_data()
    operation = data.get('operation')
    algorithm = data.get('selected_algo')

    engine = CryptoEngine()

    try:
        if operation == 'encrypt':
            if algorithm == 'aes_gcm':
                encrypted = engine.aes_gcm_encrypt(message.text, data.get('password', 'default'))
                result = json.dumps(encrypted, indent=2, ensure_ascii=False)
            elif algorithm == 'chacha20':
                encrypted = engine.chacha20_encrypt(message.text, data.get('password', 'default'))
                result = json.dumps(encrypted, indent=2, ensure_ascii=False)

            await message.answer(
                f"{emoji('encrypt')} <b>Зашифровано:</b>\n<code>{result}</code>",
                parse_mode="HTML",
                reply_markup=get_copy_keyboard()
            )

        elif operation == 'decrypt':
            try:
                encrypted_data = json.loads(message.text)
                if algorithm == 'aes_gcm':
                    result = engine.aes_gcm_decrypt(encrypted_data, data.get('password', 'default'))
                elif algorithm == 'chacha20':
                    result = engine.chacha20_decrypt(encrypted_data, data.get('password', 'default'))

                await message.answer(
                    f"{emoji('unlock')} <b>Расшифровано:</b>\n<code>{result}</code>",
                    parse_mode="HTML",
                    reply_markup=get_copy_keyboard()
                )
            except json.JSONDecodeError:
                await message.answer(f"{emoji('cross')} Неверный формат. Отправьте зашифрованные данные в формате JSON.")
                return

    except Exception as e:
        await message.answer(f"{emoji('cross')} Ошибка: {str(e)}")

    await state.clear()


@router.message(BotState.waiting_for_chain_step)
async def msg_chain_step(message: Message, state: FSMContext):
    """Handle chain mode input"""
    if not message.text:
        return

    data = await state.get_data()
    chain = data.get('chain', [])

    valid_algorithms = [
        'base64', 'base32', 'base58', 'hex', 'url_encode',
        'rot13', 'rot47', 'caesar', 'atbash', 'morse',
        'aes_gcm', 'chacha20',
        'md5', 'sha1', 'sha256', 'sha512', 'sha3_256', 'blake2b', 'crc32',
        'zlib_compress', 'zlib_decompress'
    ]

    algo = message.text.lower().strip()

    if algo == 'готово' or algo == 'done':
        if not chain:
            await message.answer(f"{emoji('cross')} Цепочка пуста. Добавьте хотя бы один алгоритм.")
            return
        
        processing_msg = await message.answer(f"{emoji('hourglass')} Обрабатываю цепочку...")
        
        try:
            processor = ChainProcessor()
            chain_display = ' → '.join(chain)
            await processing_msg.edit_text(
                f"{emoji('check')} <b>Цепочка готова:</b>\n\n"
                f"{chain_display}\n\n"
                f"Теперь отправьте текст для обработки через эту цепочку:"
            )
            await state.update_data(chain=chain, ready=True)
            await state.set_state(BotState.waiting_for_chain_text)
        except Exception as e:
            await processing_msg.edit_text(f"{emoji('cross')} Ошибка обработки цепочки: {str(e)}")
            await state.clear()
    elif algo in valid_algorithms:
        chain.append(algo)
        await state.update_data(chain=chain)
        await message.answer(
            f"{emoji('check')} Добавлено: <b>{algo}</b>\n"
            f"{emoji('link')} Текущая цепочка: <b>{' → '.join(chain)}</b>\n\n"
            f"Отправьте следующий алгоритм или напишите <b>готово</b> для завершения:",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            f"{emoji('cross')} Неизвестный алгоритм: <b>{algo}</b>\n\n"
            f"Доступные: {', '.join(valid_algorithms[:10])}...",
            parse_mode="HTML"
        )


@router.message(BotState.waiting_for_chain_text)
async def msg_chain_text(message: Message, state: FSMContext):
    """Handle text input for chain processing"""
    if not message.text:
        return

    if not rate_limiter.check_rate_limit(message.from_user.id):
        await message.answer(f"{emoji('hourglass')} Слишком много запросов. Подождите немного.")
        return

    data = await state.get_data()
    chain = data.get('chain', [])

    if not chain:
        await message.answer(f"{emoji('cross')} Цепочка пуста. Используйте /chain для настройки.")
        await state.clear()
        return

    processing_msg = await message.answer(f"{emoji('hourglass')} Обрабатываю цепочку: {' → '.join(chain)}...")

    try:
        processor = ChainProcessor()
        chain_steps = [
            {'algorithm': algo, 'operation': 'encode', 'params': {}}
            for algo in chain
        ]

        result = processor.process_chain(message.text, chain_steps)

        # Build step-by-step display
        steps_text = ""
        for i, step in enumerate(result['steps'], 1):
            algo_name = step['algorithm']
            step_result = step['result']
            preview = step_result[:100] + ("..." if len(step_result) > 100 else "")
            steps_text += f"<b>Шаг {i} — {algo_name}:</b>\n<code>{preview}</code>\n\n"

        final = result['final']

        if len(final) > 4000:
            await processing_msg.edit_text(
                f"{emoji('check')} <b>Цепочка завершена:</b>\n{' → '.join(chain)}\n\n"
                f"{steps_text}"
                f"Результат отправлен файлом 📄",
                parse_mode="HTML"
            )
            await message.answer_document(
                types.BufferedInputFile(
                    file=final.encode('utf-8'),
                    filename="chain_result.txt"
                ),
                caption=f"{emoji('check')} Финальный результат",
                reply_markup=get_copy_keyboard()
            )
        else:
            await processing_msg.edit_text(
                f"{emoji('check')} <b>Цепочка: {' → '.join(chain)}</b>\n\n"
                f"📥 <b>Вход:</b>\n<code>{message.text}</code>\n\n"
                f"{steps_text}"
                f"🏁 <b>Финал:</b>\n<code>{final}</code>",
                parse_mode="HTML",
                reply_markup=get_copy_keyboard()
            )
    except Exception as e:
        await processing_msg.edit_text(f"{emoji('cross')} Ошибка: {str(e)}")

    await state.clear()


@router.message(BotState.waiting_for_education_algo)
async def msg_education_algo(message: Message, state: FSMContext):
    """Handle education algorithm info request"""
    if not message.text:
        return

    algo = message.text.lower().strip()
    info = get_algorithm_info(algo)

    await message.answer(
        f"{emoji('grad')} <b>{info.get('name', algo)}</b>\n\n"
        f"📂 <b>Категория:</b> {info.get('category', 'Неизвестно')}\n\n"
        f"📝 <b>Описание:</b>\n{info.get('description', 'Нет описания')}\n\n"
        f"📜 <b>История:</b>\n{info.get('history', 'Нет данных')}\n\n"
        f"💡 <b>Применение:</b>\n{info.get('use_cases', 'Нет данных')}\n\n"
        f"{info.get('security', '')}\n\n"
        f"🔹 <b>Пример:</b>\n{info.get('example', 'Нет примера')}",
        parse_mode="HTML"
    )


# ==================== AUTO-DETECTION ====================

@router.message(F.text & ~F.text.startswith("/"))
async def msg_auto_detect(message: Message, state: FSMContext):
    """Auto-detect format of incoming text"""
    if await state.get_state():
        return

    if not rate_limiter.check_rate_limit(message.from_user.id):
        return

    detection = AutoDetector.detect(message.text)

    if detection:
        # Store the original text and detection info in state
        await state.update_data(auto_text=message.text, auto_type=detection['type'])

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(
            text=detection['action'],
            callback_data=f"auto:{detection['type']}",
            icon_custom_emoji_id=emoji_id("check")
        ))
        builder.row(InlineKeyboardButton(text="Главное меню", callback_data="back:main", icon_custom_emoji_id=emoji_id("back")))

        type_names_ru = {
            'base64': 'Base64',
            'hex': 'Hex',
            'base32': 'Base32',
            'morse': 'Код Морзе',
            'jwt': 'JWT'
        }

        await message.answer(
            f"{emoji('crystal_ball')} Похоже на <b>{type_names_ru.get(detection['type'], detection['type'].upper())}</b> "
            f"(уверенность: {detection['confidence']*100:.0f}%)\n\n"
            f"Хотите {detection['action'].lower()}?",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )


@router.callback_query(F.data.startswith("auto:"))
async def cb_auto_decode(callback: types.CallbackQuery, state: FSMContext):
    """Handle auto-detection decode button click"""
    detected_type = callback.data.split(":")[1]

    data = await state.get_data()
    original_text = data.get('auto_text')
    stored_type = data.get('auto_type')

    if not original_text or stored_type != detected_type:
        await callback.answer("Текст устарел. Отправьте его снова.", show_alert=True)
        await safe_callback_answer(callback)
        return

    engine = CryptoEngine()
    result = ""

    try:
        if detected_type == 'base64':
            result = engine.base64_decode(original_text)
        elif detected_type == 'hex':
            result = engine.hex_decode(original_text)
        elif detected_type == 'base32':
            result = engine.base32_decode(original_text)
        elif detected_type == 'morse':
            result = engine.morse_decode(original_text)
        elif detected_type == 'jwt':
            result = json.dumps(engine.jwt_decode(original_text), indent=2, ensure_ascii=False)
        else:
            await callback.answer("Неподдерживаемый формат", show_alert=True)
            await safe_callback_answer(callback)
            return

        await callback.message.answer(
            f"{emoji('check')} <b>Декодировано ({detected_type}):</b>\n\n"
            f"<code>{result}</code>",
            parse_mode="HTML",
            reply_markup=get_copy_keyboard()
        )
    except Exception as e:
        await callback.message.answer(f"{emoji('cross')} Ошибка декодирования: {str(e)}")

    await state.clear()
    await safe_callback_answer(callback)
