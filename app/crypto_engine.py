"""
CipherNest - Telegram Crypto Bot
Core cryptographic operations engine
"""

import base64
import hashlib
import hmac
import os
import re
import struct
import zlib
from typing import Optional, Tuple, Dict, Any
from datetime import datetime

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, PublicFormat,
    NoEncryption, BestAvailableEncryption,
    load_pem_private_key, load_pem_public_key
)


class CryptoEngine:
    """Main cryptographic operations engine"""
    
    # ==================== ENCODING ====================
    
    @staticmethod
    def base64_encode(data: str) -> str:
        """Base64 encoding"""
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')
    
    @staticmethod
    def base64_decode(data: str) -> str:
        """Base64 decoding"""
        return base64.b64decode(data).decode('utf-8')
    
    @staticmethod
    def base32_encode(data: str) -> str:
        """Base32 encoding"""
        return base64.b32encode(data.encode('utf-8')).decode('utf-8')
    
    @staticmethod
    def base32_decode(data: str) -> str:
        """Base32 decoding"""
        return base64.b32decode(data).decode('utf-8')
    
    @staticmethod
    def base58_encode(data: str) -> str:
        """Base58 encoding (Bitcoin alphabet)"""
        alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        b = data.encode('utf-8')
        n = int.from_bytes(b, 'big')
        result = ''
        while n > 0:
            n, remainder = divmod(n, 58)
            result = alphabet[remainder] + result
        # Add leading 1s for leading zero bytes
        for byte in b:
            if byte == 0:
                result = '1' + result
            else:
                break
        return result
    
    @staticmethod
    def base58_decode(data: str) -> str:
        """Base58 decoding"""
        alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        n = 0
        for char in data:
            n = n * 58 + alphabet.index(char)
        # Convert to bytes
        result = n.to_bytes((n.bit_length() + 7) // 8, 'big')
        # Add leading zero bytes for leading '1's
        for char in data:
            if char == '1':
                result = b'\x00' + result
            else:
                break
        return result.decode('utf-8')
    
    @staticmethod
    def hex_encode(data: str) -> str:
        """Hex encoding"""
        return data.encode('utf-8').hex()
    
    @staticmethod
    def hex_decode(data: str) -> str:
        """Hex decoding"""
        return bytes.fromhex(data).decode('utf-8')
    
    @staticmethod
    def url_encode(data: str) -> str:
        """URL encoding"""
        return base64.urlsafe_b64encode(data.encode('utf-8')).decode('utf-8')
    
    @staticmethod
    def url_decode(data: str) -> str:
        """URL decoding"""
        return base64.urlsafe_b64decode(data).decode('utf-8')
    
    # ==================== CLASSIC CIPHERS ====================
    
    @staticmethod
    def rot13(data: str) -> str:
        """ROT13 cipher (symmetric)"""
        result = []
        for char in data:
            if 'a' <= char <= 'z':
                result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
            else:
                result.append(char)
        return ''.join(result)
    
    @staticmethod
    def rot47(data: str) -> str:
        """ROT47 cipher (symmetric)"""
        result = []
        for char in data:
            code = ord(char)
            if 33 <= code <= 126:
                result.append(chr(33 + (code + 14) % 94))
            else:
                result.append(char)
        return ''.join(result)
    
    @staticmethod
    def caesar_cipher(data: str, shift: int) -> str:
        """Caesar cipher with custom shift"""
        result = []
        for char in data:
            if 'a' <= char <= 'z':
                result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
            else:
                result.append(char)
        return ''.join(result)
    
    @staticmethod
    def atbash(data: str) -> str:
        """Atbash cipher (symmetric)"""
        result = []
        for char in data:
            if 'a' <= char <= 'z':
                result.append(chr(ord('z') - (ord(char) - ord('a'))))
            elif 'A' <= char <= 'Z':
                result.append(chr(ord('Z') - (ord(char) - ord('A'))))
            else:
                result.append(char)
        return ''.join(result)
    
    @staticmethod
    def morse_encode(data: str) -> str:
        """Text to Morse code"""
        morse_dict = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
            'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
            'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
            'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
            'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
            '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
            '8': '---..', '9': '----.', ' ': '/'
        }
        return ' '.join(morse_dict.get(char.upper(), '?') for char in data)
    
    @staticmethod
    def morse_decode(data: str) -> str:
        """Morse code to text"""
        morse_dict = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F',
            '--.': 'G', '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
            '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R',
            '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
            '-.--': 'Y', '--..': 'Z', '-----': '0', '.----': '1', '..---': '2',
            '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
            '---..': '8', '----.': '9', '/': ' '
        }
        return ''.join(morse_dict.get(code, '?') for code in data.split())
    
    # ==================== MODERN SYMMETRIC ====================
    
    @staticmethod
    def aes_gcm_encrypt(data: str, password: str) -> dict:
        """AES-256-GCM encryption"""
        salt = os.urandom(16)
        nonce = os.urandom(12)
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode('utf-8'))
        
        # Encrypt
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, data.encode('utf-8'), None)
        
        return {
            'salt': base64.b64encode(salt).decode('utf-8'),
            'nonce': base64.b64encode(nonce).decode('utf-8'),
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8')
        }
    
    @staticmethod
    def aes_gcm_decrypt(encrypted: dict, password: str) -> str:
        """AES-256-GCM decryption"""
        salt = base64.b64decode(encrypted['salt'])
        nonce = base64.b64decode(encrypted['nonce'])
        ciphertext = base64.b64decode(encrypted['ciphertext'])
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode('utf-8'))
        
        # Decrypt
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        return plaintext.decode('utf-8')
    
    @staticmethod
    def chacha20_encrypt(data: str, password: str) -> dict:
        """ChaCha20-Poly1305 encryption"""
        salt = os.urandom(16)
        nonce = os.urandom(12)
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode('utf-8'))
        
        # Encrypt
        chacha = ChaCha20Poly1305(key)
        ciphertext = chacha.encrypt(nonce, data.encode('utf-8'), None)
        
        return {
            'salt': base64.b64encode(salt).decode('utf-8'),
            'nonce': base64.b64encode(nonce).decode('utf-8'),
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8')
        }
    
    @staticmethod
    def chacha20_decrypt(encrypted: dict, password: str) -> str:
        """ChaCha20-Poly1305 decryption"""
        salt = base64.b64decode(encrypted['salt'])
        nonce = base64.b64decode(encrypted['nonce'])
        ciphertext = base64.b64decode(encrypted['ciphertext'])
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode('utf-8'))
        
        # Decrypt
        chacha = ChaCha20Poly1305(key)
        plaintext = chacha.decrypt(nonce, ciphertext, None)
        
        return plaintext.decode('utf-8')
    
    # ==================== HASHES ====================
    
    @staticmethod
    def hash_md5(data: str) -> str:
        """MD5 hash (deprecated, for education only)"""
        return hashlib.md5(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def hash_sha1(data: str) -> str:
        """SHA-1 hash (deprecated, for education only)"""
        return hashlib.sha1(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def hash_sha256(data: str) -> str:
        """SHA-256 hash"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def hash_sha512(data: str) -> str:
        """SHA-512 hash"""
        return hashlib.sha512(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def hash_sha3_256(data: str) -> str:
        """SHA3-256 hash"""
        return hashlib.sha3_256(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def hash_blake2b(data: str) -> str:
        """BLAKE2b hash"""
        return hashlib.blake2b(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def hash_crc32(data: str) -> str:
        """CRC32 checksum"""
        return format(zlib.crc32(data.encode('utf-8')) & 0xFFFFFFFF, '08x')
    
    @staticmethod
    def hash_argon2id(data: str, salt: Optional[str] = None) -> dict:
        """Argon2id hash for password storage"""
        if salt is None:
            salt = os.urandom(16).hex()
        
        from argon2.low_level import hash_secret, Type
        
        hash_bytes = hash_secret(
            secret=data.encode('utf-8'),
            salt=bytes.fromhex(salt),
            time_cost=3,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            type=Type.ID
        )
        
        return {'salt': salt, 'hash': hash_bytes.hex()}
    
    # ==================== ASYMMETRIC ====================
    
    @staticmethod
    def rsa_generate_keys() -> dict:
        """Generate RSA-2048 key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        private_pem = private_key.private_bytes(
            Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
        ).decode('utf-8')
        
        public_pem = public_key.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return {
            'private_key': private_pem,
            'public_key': public_pem
        }
    
    @staticmethod
    def rsa_sign(data: str, private_key_pem: str) -> str:
        """RSA signature"""
        private_key = load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        
        signature = private_key.sign(
            data.encode('utf-8'),
            asym_padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode('utf-8')
    
    @staticmethod
    def rsa_verify(data: str, signature_b64: str, public_key_pem: str) -> bool:
        """Verify RSA signature"""
        public_key = load_pem_public_key(
            public_key_pem.encode('utf-8'),
            backend=default_backend()
        )
        
        signature = base64.b64decode(signature_b64)
        
        try:
            public_key.verify(
                signature,
                data.encode('utf-8'),
                asym_padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    def ed25519_generate_keys() -> dict:
        """Generate Ed25519 key pair"""
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        private_pem = private_key.private_bytes(
            Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
        ).decode('utf-8')
        
        public_pem = public_key.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return {
            'private_key': private_pem,
            'public_key': public_pem
        }
    
    @staticmethod
    def ed25519_sign(data: str, private_key_pem: str) -> str:
        """Ed25519 signature"""
        private_key = load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        
        signature = private_key.sign(data.encode('utf-8'))
        return base64.b64encode(signature).decode('utf-8')
    
    @staticmethod
    def ed25519_verify(data: str, signature_b64: str, public_key_pem: str) -> bool:
        """Verify Ed25519 signature"""
        public_key = load_pem_public_key(
            public_key_pem.encode('utf-8'),
            backend=default_backend()
        )
        
        signature = base64.b64decode(signature_b64)
        
        try:
            public_key.verify(signature, data.encode('utf-8'))
            return True
        except Exception:
            return False
    
    # ==================== UTILITIES ====================
    
    @staticmethod
    def uuid_v4() -> str:
        """Generate UUID v4"""
        import uuid
        return str(uuid.uuid4())
    
    @staticmethod
    def jwt_decode(token: str) -> dict:
        """Decode JWT token (without verification)"""
        import jwt
        # Decode without verification for inspection
        return jwt.decode(token, options={"verify_signature": False})
    
    @staticmethod
    def compress_zlib(data: str) -> str:
        """ZLIB compression"""
        compressed = zlib.compress(data.encode('utf-8'))
        return base64.b64encode(compressed).decode('utf-8')
    
    @staticmethod
    def decompress_zlib(data: str) -> str:
        """ZLIB decompression"""
        compressed = base64.b64decode(data)
        return zlib.decompress(compressed).decode('utf-8')


class AutoDetector:
    """Auto-detect encoding/format of input data"""
    
    @staticmethod
    def detect(data: str) -> Optional[Dict[str, Any]]:
        """Detect the format of input data"""
        detections = []
        
        # Base64 detection
        if re.match(r'^[A-Za-z0-9+/]+={0,2}$', data) and len(data) % 4 == 0:
            try:
                decoded = base64.b64decode(data)
                if all(32 <= b < 127 or b in (10, 13) for b in decoded):
                    detections.append({
                        'type': 'base64',
                        'confidence': 0.9,
                        'action': 'Decode Base64'
                    })
            except Exception:
                pass
        
        # Hex detection
        if re.match(r'^[0-9a-fA-F]+$', data) and len(data) % 2 == 0:
            try:
                decoded = bytes.fromhex(data)
                if all(32 <= b < 127 or b in (10, 13) for b in decoded):
                    detections.append({
                        'type': 'hex',
                        'confidence': 0.85,
                        'action': 'Decode Hex'
                    })
            except Exception:
                pass
        
        # Base32 detection
        if re.match(r'^[A-Z2-7]+=*$', data) and len(data) % 8 == 0:
            try:
                decoded = base64.b32decode(data)
                if all(32 <= b < 127 or b in (10, 13) for b in decoded):
                    detections.append({
                        'type': 'base32',
                        'confidence': 0.8,
                        'action': 'Decode Base32'
                    })
            except Exception:
                pass
        
        # Morse code detection
        if re.match(r'^[\.\- /]+$', data):
            detections.append({
                'type': 'morse',
                'confidence': 0.7,
                'action': 'Decode Morse'
            })
        
        # JWT detection
        if data.count('.') == 2 and data.startswith('eyJ'):
            detections.append({
                'type': 'jwt',
                'confidence': 0.95,
                'action': 'Decode JWT'
            })
        
        # Return highest confidence detection
        if detections:
            return max(detections, key=lambda x: x['confidence'])
        
        return None
