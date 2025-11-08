import streamlit as st
import itertools
import base64

# ==========================
# 🔐 VIGENERE CIPHER
# ==========================
def vigenere_encrypt(text, key):
    text = text.upper().replace(" ", "")
    key = key.upper()
    encrypted = []
    for i, char in enumerate(text):
        shift = ord(key[i % len(key)]) - 65
        new_char = chr(((ord(char) - 65 + shift) % 26) + 65)
        encrypted.append(new_char)
    return ''.join(encrypted)

def vigenere_decrypt(cipher, key):
    cipher = cipher.upper().replace(" ", "")
    key = key.upper()
    decrypted = []
    for i, char in enumerate(cipher):
        shift = ord(key[i % len(key)]) - 65
        new_char = chr(((ord(char) - 65 - shift) % 26) + 65)
        decrypted.append(new_char)
    return ''.join(decrypted)


# ==========================
# 🔐 PLAYFAIR 6x6 (A-Z + 0-9)
# ==========================
def generate_playfair_matrix(key):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    key = "".join(dict.fromkeys(key.upper() + alphabet))  # remove duplicates, keep order
    matrix = [key[i:i+6] for i in range(0, 36, 6)]
    return matrix

def playfair_positions(matrix):
    return {matrix[r][c]: (r, c) for r in range(6) for c in range(6)}

def playfair_encrypt(text, key):
    text = text.upper().replace(" ", "")
    if len(text) % 2 != 0:
        text += "X"  # padding

    matrix = generate_playfair_matrix(key)
    pos = playfair_positions(matrix)
    pairs = [text[i:i+2] for i in range(0, len(text), 2)]
    result = []

    for a, b in pairs:
        ra, ca = pos[a]
        rb, cb = pos[b]
        if ra == rb:  # same row
            result.append(matrix[ra][(ca+1) % 6] + matrix[rb][(cb+1) % 6])
        elif ca == cb:  # same column
            result.append(matrix[(ra+1) % 6][ca] + matrix[(rb+1) % 6][cb])
        else:  # rectangle
            result.append(matrix[ra][cb] + matrix[rb][ca])
    return ''.join(result)

def playfair_decrypt(cipher, key):
    matrix = generate_playfair_matrix(key)
    pos = playfair_positions(matrix)
    pairs = [cipher[i:i+2] for i in range(0, len(cipher), 2)]
    result = []

    for a, b in pairs:
        ra, ca = pos[a]
        rb, cb = pos[b]
        if ra == rb:
            result.append(matrix[ra][(ca-1) % 6] + matrix[rb][(cb-1) % 6])
        elif ca == cb:
            result.append(matrix[(ra-1) % 6][ca] + matrix[(rb-1) % 6][cb])
        else:
            result.append(matrix[ra][cb] + matrix[rb][ca])
    return ''.join(result)


# ==========================
# 🔐 XOR (Base64)
# ==========================
def xor_encrypt(text, key):
    key_cycle = itertools.cycle(key)
    xor_bytes = bytes([ord(a) ^ ord(b) for a, b in zip(text, key_cycle)])
    return base64.b64encode(xor_bytes).decode('utf-8')

def xor_decrypt(cipher_b64, key):
    cipher_bytes = base64.b64decode(cipher_b64)
    key_cycle = itertools.cycle(key)
    decrypted = ''.join(chr(b ^ ord(k)) for b, k in zip(cipher_bytes, key_cycle))
    return decrypted


# ==========================
# 🔐 ENKRIPSI KUNCI DENGAN XOR
# ==========================
def encrypt_key_with_xor(key, xor_key):
    key_cycle = itertools.cycle(xor_key)
    xor_bytes = bytes([ord(a) ^ ord(b) for a, b in zip(key, key_cycle)])
    return base64.b64encode(xor_bytes).decode('utf-8')

def decrypt_key_with_xor(encrypted_key_b64, xor_key):
    cipher_bytes = base64.b64decode(encrypted_key_b64)
    key_cycle = itertools.cycle(xor_key)
    return ''.join(chr(b ^ ord(k)) for b, k in zip(cipher_bytes, key_cycle))


# ==========================
# 🔐 HYBRID ENCRYPTION
# ==========================
def hybrid_encrypt(plaintext, key1, key2, key3):
    # Encrypt the keys first
    enc_key1 = encrypt_key_with_xor(key1, key3)
    enc_key2 = encrypt_key_with_xor(key2, key3)

    # Use original keys for encryption
    step1 = vigenere_encrypt(plaintext, key1)
    step2 = playfair_encrypt(step1, key2)
    step3 = xor_encrypt(step2, key3)

    return enc_key1, enc_key2, step1, step2, step3

def hybrid_decrypt(ciphertext, key1_enc, key2_enc, key3):
    # Coba deteksi apakah key sudah base64 terenkripsi
    try:
        key1 = decrypt_key_with_xor(key1_enc, key3)
        key2 = decrypt_key_with_xor(key2_enc, key3)
    except Exception:
        # Jika gagal decode Base64, berarti user memasukkan key mentah
        key1, key2 = key1_enc, key2_enc

    # Gunakan decrypted key (atau original key)
    step1 = xor_decrypt(ciphertext, key3)
    step2 = playfair_decrypt(step1, key2)
    step3 = vigenere_decrypt(step2, key1)

    return key1, key2, step1, step2, step3


# ==========================
# 🧩 STREAMLIT UI
# ==========================
st.title("🔐 Hybrid Cipher (Vigenère + Playfair6x6 + XOR + Enkripsi Kunci)")

mode = st.radio("Pilih mode:", ["Enkripsi", "Dekripsi"])
plaintext = st.text_area("Masukkan teks:", "HELLO WORLD")
key_vigenere = st.text_input("Kunci Vigenère:", "KEY")
key_playfair = st.text_input("Kunci Playfair:", "SECRET")
key_xor = st.text_input("Kunci XOR:", "abc")

if st.button("Jalankan"):
    if mode == "Enkripsi":
        enc_key1, enc_key2, step1, step2, cipher = hybrid_encrypt(
            plaintext, key_vigenere, key_playfair, key_xor
        )

        st.subheader("🔒 Hasil Enkripsi")
        st.write("**Langkah 0 - Enkripsi Kunci Vigenère (XOR):**", enc_key1)
        st.write("**Langkah 0 - Enkripsi Kunci Playfair (XOR):**", enc_key2)
        st.write("**Langkah 1 - Vigenère →**", step1)
        st.write("**Langkah 2 - Playfair 6x6 →**", step2)
        st.write("**Langkah 3 - XOR (Base64):**", cipher)
        st.success(f"Ciphertext Akhir: {cipher}")

    else:
        key1, key2, step1, step2, plain = hybrid_decrypt(
            plaintext, key_vigenere, key_playfair, key_xor
        )

        st.subheader("🔓 Hasil Dekripsi")
        st.write("**Langkah 0 - Dekripsi Kunci Vigenère (XOR):**", key1)
        st.write("**Langkah 0 - Dekripsi Kunci Playfair (XOR):**", key2)
        st.write("**Langkah 1 - XOR → Playfair Input:**", step1)
        st.write("**Langkah 2 - Playfair → Vigenère Input:**", step2)
        st.write("**Langkah 3 - Vigenère Dekripsi:**", plain)
        st.success(f"Plaintext Akhir: {plain}")