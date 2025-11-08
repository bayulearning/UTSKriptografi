import streamlit as st
import itertools
import base64

# ==========================
# VIGENERE CIPHER
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
# PLAYFAIR 6x6 (A-Z + 0-9)
# ==========================
def generate_playfair_matrix(key):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    key = "".join(dict.fromkeys(key.upper() + alphabet))  
    matrix = [key[i:i+6] for i in range(0, 36, 6)]
    return matrix

def playfair_positions(matrix):
    return {matrix[r][c]: (r, c) for r in range(6) for c in range(6)}

def playfair_encrypt(text, key):
    text = text.upper().replace(" ", "")
    if len(text) % 2 != 0:
        text += "X"  

    matrix = generate_playfair_matrix(key)
    pos = playfair_positions(matrix)
    pairs = [text[i:i+2] for i in range(0, len(text), 2)]
    result = []

    for a, b in pairs:
        ra, ca = pos[a]
        rb, cb = pos[b]
        if ra == rb:  
            result.append(matrix[ra][(ca+1) % 6] + matrix[rb][(cb+1) % 6])
        elif ca == cb:  
            result.append(matrix[(ra+1) % 6][ca] + matrix[(rb+1) % 6][cb])
        else:  
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
# XOR (Base64)
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
# ENKRIPSI KUNCI DENGAN XOR
# ==========================
def encrypt_key_with_xor(key, xor_key):
    key_cycle = itertools.cycle(xor_key)
    xor_bytes = bytes([ord(a) ^ ord(b) for a, b in zip(key, key_cycle)])
    return base64.b64encode(xor_bytes).decode('utf-8')

def decrypt_key_with_xor(encrypted_key_b64, xor_key):
    cipher_bytes = base64.b64decode(encrypted_key_b64)
    key_cycle = itertools.cycle(xor_key)
    return ''.join(chr(b ^ ord(k)) for b, k in zip(cipher_bytes, key_cycle))


st.set_page_config(page_title="Hybrid Cipher Encryption Tool", page_icon="🔐", layout="centered")

st.markdown("""
    <style>
        body {
            background-color: #0e1117;
            color: #f8f9fa;
        }
        .title {
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            color: #f0f2f6;
        }
        .subtitle {
            text-align: center;
            color: #b0b3b8;
            margin-bottom: 20px;
        }
        .box {
            background: #1e1e24;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 0 20px rgba(0,0,0,0.4);
            margin-bottom: 20px;
        }
        .encrypt-box {
            background: linear-gradient(135deg, #1e2a3a 0%, #243447 100%);
            border: 1px solid #2c4762;
        }
        .decrypt-box {
            background: linear-gradient(135deg, #3a2a1e 0%, #473624 100%);
            border: 1px solid #624b2c;
        }
        .result-box {
            background: #131722;
            border-left: 4px solid #4a90e2;
            padding: 15px;
            border-radius: 10px;
            color: #d1d5db;
            font-size: 15px;
        }
        code {
            background-color: #2a2f3a;
            color: #00c2ff;
            padding: 2px 5px;
            border-radius: 5px;
            font-size: 14px;
        }
        .helper {
            color: #9aa4b2;
            font-size: 13px;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================
# 🧠 STATE MANAGEMENT
# ==========================
if "last_plaintext" not in st.session_state:
    st.session_state["last_plaintext"] = ""
if "button_disabled" not in st.session_state:
    st.session_state["button_disabled"] = False
# ensure text_input key exists so we can mutate it programmatically
if "text_input" not in st.session_state:
    st.session_state["text_input"] = "HELLO WORLD"

def on_plaintext_change():
    """
    Jika pengguna mengubah/mengetik ulang plaintext, aktifkan tombol Jalankan kembali.
    """
    st.session_state["button_disabled"] = False

def do_reset():
    """
    Reset manual: kosongkan plaintext & aktifkan tombol.
    """
    st.session_state["text_input"] = ""          # mengosongkan text_area
    st.session_state["button_disabled"] = False
    st.session_state["last_plaintext"] = ""

# ==========================
# 🔐 HEADER
# ==========================
st.markdown("<div class='title'>🔐 Hybrid Chiper</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Vigenère + Playfair 6x6 + XOR + Enkripsi Kunci</div>", unsafe_allow_html=True)

# ==========================
# 🧩 INPUT SECTION
# ==========================
with st.container():
    st.markdown("<div class='box'>", unsafe_allow_html=True)
    mode = st.radio("🧭 Pilih mode operasi:", ["Enkripsi", "Dekripsi"], horizontal=True)
    plaintext = st.text_area(
        "📝 Masukkan teks:",
        key="text_input",
        on_change=on_plaintext_change,
        help="Ubah teks di sini untuk mengaktifkan kembali tombol 'Jalankan'."
    )
    col1, col2 = st.columns(2)
    with col1:
        key_vigenere = st.text_input("🔑 Kunci Vigenère:", "KEY")
        key_playfair = st.text_input("🔑 Kunci Playfair:", "SECRET")
    with col2:
        key_xor = st.text_input("🧩 Kunci XOR:", "abc")
        st.write("")  # spacing

        # dua tombol berdampingan: Jalankan (kanan) dan Reset (kiri)
        btn_col_reset, btn_col_run = st.columns([1, 2])
        with btn_col_reset:
            reset_button = st.button("🔁 Reset", use_container_width=True, on_click=do_reset)
        with btn_col_run:
            start_button = st.button(
                "🚀 Jalankan",
                use_container_width=True,
                disabled=st.session_state["button_disabled"]
            )
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================
# HYBRID ENCRYPTION
# ==========================
def hybrid_encrypt(plaintext, key1, key2, key3):
    # Encrypt the keys first
    enc_key1 = encrypt_key_with_xor(key1, key3)
    enc_key2 = encrypt_key_with_xor(key2, key3)

    
    step1 = vigenere_encrypt(plaintext, key1)
    step2 = playfair_encrypt(step1, key2)
    step3 = xor_encrypt(step2, key3)

    return enc_key1, enc_key2, step1, step2, step3

def hybrid_decrypt(ciphertext, key1_enc, key2_enc, key3):
   
    try:
        key1 = decrypt_key_with_xor(key1_enc, key3)
        key2 = decrypt_key_with_xor(key2_enc, key3)
    except Exception:
      
        key1, key2 = key1_enc, key2_enc

    step1 = xor_decrypt(ciphertext, key3)
    step2 = playfair_decrypt(step1, key2)
    step3 = vigenere_decrypt(step2, key1)

    return key1, key2, step1, step2, step3

if start_button:
    st.session_state["button_disabled"] = True
    st.session_state["last_plaintext"] = st.session_state["text_input"]

    if mode == "Enkripsi":
        enc_key1, enc_key2, step1, step2, cipher = hybrid_encrypt(
            st.session_state["text_input"], key_vigenere, key_playfair, key_xor
        )
        st.markdown("<div class='box encrypt-box'>", unsafe_allow_html=True)
        st.subheader("🔒 Hasil Enkripsi")
        st.markdown(f"""
        <div class='result-box'>
        <b style='color:#00ff99;'>Ciphertext Akhir:</b> ✅ <code>{cipher}</code>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        key1, key2, step1, step2, plain = hybrid_decrypt(
            st.session_state["text_input"], key_vigenere, key_playfair, key_xor
        )
        st.markdown("<div class='box decrypt-box'>", unsafe_allow_html=True)
        st.subheader("🔓 Hasil Dekripsi")
        st.markdown(f"""
        <div class='result-box'>
        <b style='color:#00b7ff;'>Plaintext Akhir:</b> ✅ <code>{plain}</code>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# kecil: indikator status di bawah tombol (opsional)
status_text = "🔒 Sudah diproses — tekan Reset atau ubah teks untuk menjalankan lagi." if st.session_state["button_disabled"] else "✅ Siap dijalankan"
st.markdown(f"<div class='helper'>{status_text}</div>", unsafe_allow_html=True)