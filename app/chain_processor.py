"""
CipherNest - Telegram Crypto Bot
Chain processing for multiple transformations
"""

from typing import List, Dict, Any
from app.crypto_engine import CryptoEngine


class ChainProcessor:
    """Process multiple transformations in sequence"""
    
    def __init__(self):
        self.engine = CryptoEngine()
    
    def process_chain(self, data: str, chain: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a chain of transformations

        Args:
            data: Input data
            chain: List of {'algorithm': str, 'operation': str, 'params': dict}

        Returns:
            Dict with 'steps' (list of intermediate results) and 'final' (last result)
        """
        current_data = data
        steps = []

        for step in chain:
            algo = step['algorithm']
            operation = step['operation']
            params = step.get('params', {})

            current_data = self._apply_transformation(
                current_data, algo, operation, params
            )
            steps.append({
                'algorithm': algo,
                'operation': operation,
                'result': current_data
            })

        return {
            'steps': steps,
            'final': current_data
        }
    
    def _apply_transformation(self, data: str, algorithm: str,
                            operation: str, params: dict) -> str:
        """Apply a single transformation"""
        
        # Classic ciphers (symmetric - same for encode/decode)
        if algorithm in ['rot13', 'rot47', 'caesar', 'atbash']:
            if algorithm == 'rot13':
                return self.engine.rot13(data)
            elif algorithm == 'rot47':
                return self.engine.rot47(data)
            elif algorithm == 'caesar':
                shift = params.get('shift', 3)
                return self.engine.caesar_cipher(data, shift)
            elif algorithm == 'atbash':
                return self.engine.atbash(data)

        # Encoding operations
        if operation == 'encode':
            if algorithm == 'base64':
                return self.engine.base64_encode(data)
            elif algorithm == 'base32':
                return self.engine.base32_encode(data)
            elif algorithm == 'base58':
                return self.engine.base58_encode(data)
            elif algorithm == 'hex':
                return self.engine.hex_encode(data)
            elif algorithm == 'url_encode':
                return self.engine.url_encode(data)
            elif algorithm == 'morse':
                return self.engine.morse_encode(data)
            elif algorithm == 'zlib_compress':
                return self.engine.compress_zlib(data)

        elif operation == 'decode':
            if algorithm == 'base64':
                return self.engine.base64_decode(data)
            elif algorithm == 'base32':
                return self.engine.base32_decode(data)
            elif algorithm == 'base58':
                return self.engine.base58_decode(data)
            elif algorithm == 'hex':
                return self.engine.hex_decode(data)
            elif algorithm == 'url_encode':
                return self.engine.url_decode(data)
            elif algorithm == 'morse':
                return self.engine.morse_decode(data)
            elif algorithm == 'zlib_decompress':
                return self.engine.decompress_zlib(data)
        
        # Hash operations
        elif operation == 'hash':
            if algorithm == 'md5':
                return self.engine.hash_md5(data)
            elif algorithm == 'sha1':
                return self.engine.hash_sha1(data)
            elif algorithm == 'sha256':
                return self.engine.hash_sha256(data)
            elif algorithm == 'sha512':
                return self.engine.hash_sha512(data)
            elif algorithm == 'sha3_256':
                return self.engine.hash_sha3_256(data)
            elif algorithm == 'blake2b':
                return self.engine.hash_blake2b(data)
            elif algorithm == 'crc32':
                return self.engine.hash_crc32(data)
        
        # Symmetric encryption
        elif operation == 'encrypt':
            password = params.get('password')
            if algorithm == 'aes_gcm':
                encrypted = self.engine.aes_gcm_encrypt(data, password)
                return str(encrypted)
            elif algorithm == 'chacha20':
                encrypted = self.engine.chacha20_encrypt(data, password)
                return str(encrypted)
        
        elif operation == 'decrypt':
            password = params.get('password')
            # Note: This would need proper parsing of encrypted data
            pass
        
        raise ValueError(f"Unsupported transformation: {algorithm}/{operation}")
