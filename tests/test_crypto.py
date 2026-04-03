"""
CipherNest - Test Suite
Tests for crypto engine and bot functionality
"""

import unittest
import json
from app.crypto_engine import CryptoEngine, AutoDetector
from app.security import RateLimiter, InputValidator
from app.chain_processor import ChainProcessor


class TestCryptoEngine(unittest.TestCase):
    """Test cryptographic operations"""
    
    def setUp(self):
        self.engine = CryptoEngine()
        self.test_text = "Hello, World! 123"
    
    # ==================== ENCODING TESTS ====================
    
    def test_base64_encode_decode(self):
        """Test Base64 encoding and decoding"""
        encoded = self.engine.base64_encode(self.test_text)
        decoded = self.engine.base64_decode(encoded)
        self.assertEqual(decoded, self.test_text)
    
    def test_base32_encode_decode(self):
        """Test Base32 encoding and decoding"""
        encoded = self.engine.base32_encode(self.test_text)
        decoded = self.engine.base32_decode(encoded)
        self.assertEqual(decoded, self.test_text)
    
    def test_base58_encode_decode(self):
        """Test Base58 encoding and decoding"""
        encoded = self.engine.base58_encode(self.test_text)
        decoded = self.engine.base58_decode(encoded)
        self.assertEqual(decoded, self.test_text)
    
    def test_hex_encode_decode(self):
        """Test Hex encoding and decoding"""
        encoded = self.engine.hex_encode(self.test_text)
        decoded = self.engine.hex_decode(encoded)
        self.assertEqual(decoded, self.test_text)
    
    def test_url_encode_decode(self):
        """Test URL encoding and decoding"""
        encoded = self.engine.url_encode(self.test_text)
        decoded = self.engine.url_decode(encoded)
        self.assertEqual(decoded, self.test_text)
    
    # ==================== CLASSIC CIPHER TESTS ====================
    
    def test_rot13_symmetric(self):
        """Test ROT13 is symmetric (encode = decode)"""
        encoded = self.engine.rot13(self.test_text)
        decoded = self.engine.rot13(encoded)
        self.assertEqual(decoded, self.test_text)
    
    def test_rot47_symmetric(self):
        """Test ROT47 is symmetric"""
        encoded = self.engine.rot47(self.test_text)
        decoded = self.engine.rot47(encoded)
        self.assertEqual(decoded, self.test_text)
    
    def test_caesar_cipher(self):
        """Test Caesar cipher with custom shift"""
        shift = 5
        encoded = self.engine.caesar_cipher(self.test_text, shift)
        decoded = self.engine.caesar_cipher(encoded, -shift)
        self.assertEqual(decoded, self.test_text)
    
    def test_atbash_symmetric(self):
        """Test Atbash is symmetric"""
        encoded = self.engine.atbash(self.test_text)
        decoded = self.engine.atbash(encoded)
        self.assertEqual(decoded, self.test_text)
    
    def test_morse_encode_decode(self):
        """Test Morse code encoding and decoding"""
        text = "SOS"
        encoded = self.engine.morse_encode(text)
        decoded = self.engine.morse_decode(encoded)
        self.assertEqual(decoded, text)
    
    # ==================== MODERN ENCRYPTION TESTS ====================
    
    def test_aes_gcm_encrypt_decrypt(self):
        """Test AES-256-GCM encryption and decryption"""
        password = "secure_password_123"
        encrypted = self.engine.aes_gcm_encrypt(self.test_text, password)
        
        # Verify structure
        self.assertIn('salt', encrypted)
        self.assertIn('nonce', encrypted)
        self.assertIn('ciphertext', encrypted)
        
        # Decrypt
        decrypted = self.engine.aes_gcm_decrypt(encrypted, password)
        self.assertEqual(decrypted, self.test_text)
    
    def test_aes_gcm_wrong_password(self):
        """Test AES-256-GCM fails with wrong password"""
        password = "correct_password"
        wrong_password = "wrong_password"
        
        encrypted = self.engine.aes_gcm_encrypt(self.test_text, password)
        
        with self.assertRaises(Exception):
            self.engine.aes_gcm_decrypt(encrypted, wrong_password)
    
    def test_chacha20_encrypt_decrypt(self):
        """Test ChaCha20 encryption and decryption"""
        password = "secure_password_123"
        encrypted = self.engine.chacha20_encrypt(self.test_text, password)
        
        # Verify structure
        self.assertIn('salt', encrypted)
        self.assertIn('nonce', encrypted)
        self.assertIn('ciphertext', encrypted)
        
        # Decrypt
        decrypted = self.engine.chacha20_decrypt(encrypted, password)
        self.assertEqual(decrypted, self.test_text)
    
    # ==================== HASH TESTS ====================
    
    def test_hash_deterministic(self):
        """Test hashes are deterministic"""
        hash1 = self.engine.hash_sha256(self.test_text)
        hash2 = self.engine.hash_sha256(self.test_text)
        self.assertEqual(hash1, hash2)
    
    def test_hash_sha256_length(self):
        """Test SHA-256 produces 64 hex characters"""
        hash_value = self.engine.hash_sha256(self.test_text)
        self.assertEqual(len(hash_value), 64)
    
    def test_hash_sha512_length(self):
        """Test SHA-512 produces 128 hex characters"""
        hash_value = self.engine.hash_sha512(self.test_text)
        self.assertEqual(len(hash_value), 128)
    
    def test_hash_different_inputs(self):
        """Test different inputs produce different hashes"""
        hash1 = self.engine.hash_sha256("input1")
        hash2 = self.engine.hash_sha256("input2")
        self.assertNotEqual(hash1, hash2)
    
    def test_hash_md5_length(self):
        """Test MD5 produces 32 hex characters"""
        hash_value = self.engine.hash_md5(self.test_text)
        self.assertEqual(len(hash_value), 32)
    
    def test_hash_crc32(self):
        """Test CRC32 checksum"""
        hash_value = self.engine.hash_crc32(self.test_text)
        self.assertEqual(len(hash_value), 8)
    
    def test_argon2id_structure(self):
        """Test Argon2id produces salt and hash"""
        result = self.engine.hash_argon2id(self.test_text)
        self.assertIn('salt', result)
        self.assertIn('hash', result)
    
    # ==================== ASYMMETRIC TESTS ====================
    
    def test_rsa_key_generation(self):
        """Test RSA key pair generation"""
        keys = self.engine.rsa_generate_keys()
        self.assertIn('private_key', keys)
        self.assertIn('public_key', keys)
        self.assertIn('BEGIN', keys['private_key'])
        self.assertIn('BEGIN', keys['public_key'])
    
    def test_ed25519_key_generation(self):
        """Test Ed25519 key pair generation"""
        keys = self.engine.ed25519_generate_keys()
        self.assertIn('private_key', keys)
        self.assertIn('public_key', keys)
    
    def test_ed25519_sign_verify(self):
        """Test Ed25519 sign and verify"""
        keys = self.engine.ed25519_generate_keys()
        signature = self.engine.ed25519_sign(self.test_text, keys['private_key'])
        is_valid = self.engine.ed25519_verify(self.test_text, signature, keys['public_key'])
        self.assertTrue(is_valid)
    
    def test_ed25519_wrong_signature(self):
        """Test Ed25519 fails with wrong signature"""
        keys = self.engine.ed25519_generate_keys()
        signature = self.engine.ed25519_sign(self.test_text, keys['private_key'])
        is_valid = self.engine.ed25519_verify("wrong text", signature, keys['public_key'])
        self.assertFalse(is_valid)
    
    # ==================== UTILITY TESTS ====================
    
    def test_uuid_v4_format(self):
        """Test UUID v4 format"""
        import re
        uuid = self.engine.uuid_v4()
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        self.assertTrue(re.match(pattern, uuid, re.IGNORECASE))
    
    def test_zlib_compress_decompress(self):
        """Test ZLIB compression and decompression"""
        compressed = self.engine.compress_zlib(self.test_text)
        decompressed = self.engine.decompress_zlib(compressed)
        self.assertEqual(decompressed, self.test_text)


class TestAutoDetector(unittest.TestCase):
    """Test auto-detection functionality"""
    
    def test_detect_base64(self):
        """Test Base64 detection"""
        data = "SGVsbG8gV29ybGQ="  # "Hello World" in Base64
        result = AutoDetector.detect(data)
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'base64')
    
    def test_detect_hex(self):
        """Test Hex detection"""
        data = "48656c6c6f"  # "Hello" in Hex
        result = AutoDetector.detect(data)
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'hex')
    
    def test_detect_jwt(self):
        """Test JWT detection"""
        data = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        result = AutoDetector.detect(data)
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'jwt')
    
    def test_no_detection_plain_text(self):
        """Test plain text returns no detection"""
        data = "Hello, World!"
        result = AutoDetector.detect(data)
        self.assertIsNone(result)


class TestSecurity(unittest.TestCase):
    """Test security features"""
    
    def test_rate_limiter(self):
        """Test rate limiting"""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        user_id = 12345
        
        # Should allow first 3 requests
        self.assertTrue(limiter.check_rate_limit(user_id))
        self.assertTrue(limiter.check_rate_limit(user_id))
        self.assertTrue(limiter.check_rate_limit(user_id))
        
        # Should block 4th request
        self.assertFalse(limiter.check_rate_limit(user_id))
    
    def test_input_validator_empty(self):
        """Test input validator rejects empty input"""
        is_valid, msg = InputValidator.validate_text("")
        self.assertFalse(is_valid)
    
    def test_input_validator_too_long(self):
        """Test input validator rejects too long input"""
        long_text = "a" * 10001
        is_valid, msg = InputValidator.validate_text(long_text)
        self.assertFalse(is_valid)
    
    def test_input_validator_safe_text(self):
        """Test input validator accepts safe text"""
        is_valid, msg = InputValidator.validate_text("Hello, World!")
        self.assertTrue(is_valid)
    
    def test_input_validator_suspicious(self):
        """Test input validator rejects suspicious patterns"""
        suspicious = "<script>alert('xss')</script>"
        is_valid, msg = InputValidator.validate_text(suspicious)
        self.assertFalse(is_valid)
    
    def test_password_validator_weak(self):
        """Test password validator rejects weak passwords"""
        is_valid, msg = InputValidator.validate_password("short")
        self.assertFalse(is_valid)
    
    def test_password_validator_strong(self):
        """Test password validator accepts strong passwords"""
        is_valid, msg = InputValidator.validate_password("secure_password_123")
        self.assertTrue(is_valid)


class TestChainProcessor(unittest.TestCase):
    """Test chain processing"""
    
    def setUp(self):
        self.processor = ChainProcessor()
        self.test_text = "Hello, World!"
    
    def test_simple_chain(self):
        """Test simple encoding chain"""
        chain = [
            {'algorithm': 'base64', 'operation': 'encode'},
            {'algorithm': 'hex', 'operation': 'encode'}
        ]
        result = self.processor.process_chain(self.test_text, chain)
        
        # Verify result is hex-encoded base64
        decoded_hex = bytes.fromhex(result).decode('utf-8')
        import base64
        decoded_base64 = base64.b64decode(decoded_hex).decode('utf-8')
        self.assertEqual(decoded_base64, self.test_text)
    
    def test_chain_with_classic_cipher(self):
        """Test chain with classic cipher"""
        chain = [
            {'algorithm': 'base64', 'operation': 'encode'},
            {'algorithm': 'rot13', 'operation': 'encode'}
        ]
        result = self.processor.process_chain(self.test_text, chain)
        
        # Should be ROT13 of Base64
        import base64
        base64_encoded = base64.b64encode(self.test_text.encode()).decode()
        from app.crypto_engine import CryptoEngine
        expected = CryptoEngine().rot13(base64_encoded)
        self.assertEqual(result, expected)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases"""
    
    def setUp(self):
        self.engine = CryptoEngine()
    
    def test_empty_string(self):
        """Test handling of empty strings"""
        encoded = self.engine.base64_encode("")
        decoded = self.engine.base64_decode(encoded)
        self.assertEqual(decoded, "")
    
    def test_unicode_emoji(self):
        """Test handling of Unicode and emoji"""
        text = "Hello 🌍 Привет 世界"
        encoded = self.engine.base64_encode(text)
        decoded = self.engine.base64_decode(encoded)
        self.assertEqual(decoded, text)
    
    def test_binary_data(self):
        """Test handling of binary-like data"""
        text = "\x00\x01\x02\x03"
        encoded = self.engine.hex_encode(text)
        decoded = self.engine.hex_decode(encoded)
        self.assertEqual(decoded, text)
    
    def test_very_long_text(self):
        """Test handling of long text"""
        text = "A" * 10000
        encoded = self.engine.base64_encode(text)
        decoded = self.engine.base64_decode(encoded)
        self.assertEqual(decoded, text)
    
    def test_special_characters(self):
        """Test handling of special characters"""
        text = "!@#$%^&*()_+-=[]{}|;':\",.<>?/~`"
        encoded = self.engine.base64_encode(text)
        decoded = self.engine.base64_decode(encoded)
        self.assertEqual(decoded, text)


if __name__ == '__main__':
    unittest.main()
