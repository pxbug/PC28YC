import base64

def simple_encrypt(text, key='pc28_secret_key_2024'):
    key_bytes = key.encode()
    text_bytes = text.encode()
    result = bytearray()
    for i, byte in enumerate(text_bytes):
        result.append(byte ^ key_bytes[i % len(key_bytes)])
    return base64.b64encode(bytes(result)).decode()

def simple_decrypt(encrypted_text, key='pc28_secret_key_2024'):
    try:
        key_bytes = key.encode()
        encrypted_bytes = base64.b64decode(encrypted_text.encode())
        result = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            result.append(byte ^ key_bytes[i % len(key_bytes)])
        return bytes(result).decode()
    except:
        return None

ENCRYPTED_API_URL = "GBdGSCxJSkwCBkZnRQQQcFNAWxsbCRxSLBwL"

ENCRYPTED_KENO_URL = "GBdGSCxJSkwCBkZnRQQQcFNAWxsbBlxXcRkWDBw="

def get_api_url():
    return simple_decrypt(ENCRYPTED_API_URL)

def get_keno_url():
    return simple_decrypt(ENCRYPTED_KENO_URL)

def encrypt_url(url):
    return simple_encrypt(url)

if __name__ == '__main__':
    print("API URL:", get_api_url())
    print("Keno URL:", get_keno_url())
    
