# =================== CRITICAL: SET BACKEND FIRST ===================
import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template, request, jsonify
import os
import numpy as np
from scipy.io import wavfile
from scipy.fft import fft
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import io
import base64
from mutagen.wave import WAVE
import tempfile
import hashlib
from datetime import datetime

# =================== FIX: TEMPLATE PATH ===================
# Get absolute path to templates directory
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(os.path.dirname(current_dir), 'templates')

# Create Flask app with correct template folder
app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'ultra_eterna_forest_giratina_2025_vercel'

def extract_multi_lsb_audio(data, bit_positions=[0, 1, 2]):
    """Extract LSB from multiple bit positions for layered hiding"""
    if len(data.shape) > 1:
        data = np.mean(data, axis=1).astype(np.int16)
    
    layers = {}
    for bit_pos in bit_positions:
        lsb_data = (data >> bit_pos) & 1
        hidden_audio = (lsb_data * 2 - 1) * (16383 >> bit_pos)
        layers[f'layer_{bit_pos}'] = hidden_audio.astype(np.int16)
    
    return layers

def extract_frequency_domain_data(data, sample_rate):
    """Extract hidden data from frequency domain"""
    try:
        fft_data = fft(data)
        phase = np.angle(fft_data)
        freq_bins = np.fft.fftfreq(len(data), 1/sample_rate)
        target_freqs = [440, 880, 1320, 1760]
        
        hidden_data = []
        for freq in target_freqs:
            bin_idx = np.argmin(np.abs(freq_bins - freq))
            if bin_idx < len(phase):
                phase_int = int(phase[bin_idx] * 1000) % 2
                hidden_data.append(phase_int)
        
        return hidden_data
    except Exception:
        return [0, 1, 0, 1]

def generate_advanced_spectrogram(audio_data, sample_rate):
    """Generate spectrograms using Figure objects (serverless-safe)"""
    spectrograms = {}
    
    try:
        # Reduce size for serverless limits
        max_length = min(len(audio_data), sample_rate * 30)
        audio_data = audio_data[:max_length]
        
        # Primary spectrogram
        fig = Figure(figsize=(12, 6))
        ax = fig.subplots()
        ax.specgram(audio_data, Fs=sample_rate, cmap='plasma', NFFT=1024, noverlap=512)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Frequency (Hz)')
        ax.set_title('Primary Spectrogram - Look for Visual Patterns')
        ax.set_ylim(0, 4000)
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        spectrograms['primary'] = base64.b64encode(buf.getvalue()).decode()
        buf.close()
        
        # High resolution spectrogram
        fig = Figure(figsize=(12, 6))
        ax = fig.subplots()
        ax.specgram(audio_data, Fs=sample_rate, cmap='viridis', NFFT=2048, noverlap=1024)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Frequency (Hz)')
        ax.set_title('High Resolution Spectrogram')
        ax.set_ylim(0, 4000)
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        spectrograms['high_res'] = base64.b64encode(buf.getvalue()).decode()
        buf.close()
        
        # Simplified phase analysis
        fft_data = fft(audio_data[:min(len(audio_data), 50000)])
        phase = np.angle(fft_data)
        
        fig = Figure(figsize=(12, 6))
        ax = fig.subplots()
        ax.plot(phase[:1000])
        ax.set_xlabel('Sample Index')
        ax.set_ylabel('Phase (radians)')
        ax.set_title('Phase Analysis - Hidden Patterns May Appear')
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        spectrograms['phase'] = base64.b64encode(buf.getvalue()).decode()
        buf.close()
        
    except Exception as e:
        print(f"Spectrogram generation error: {e}")
        spectrograms = {
            'primary': '',
            'high_res': '',
            'phase': ''
        }
    
    return spectrograms

def extract_complex_metadata(file_path):
    """Extract multiple cipher texts from various metadata sources"""
    ciphers = {
        'primary': "NKOOR_IURP_JLUDWLQD_UHDOP",
        'secondary': "FDHVDU_FLSKHU_ZLWK_NHBZRUG",
        'tertiary': "WLPH_EDVHG_HQFULSWLRQ",
        'quaternary': f"WLPH_VKLIW_{datetime.now().hour % 13:02d}"
    }
    
    try:
        audio = WAVE(file_path)
        if audio.tags:
            cipher_from_metadata = ""
            for key in ['TIT2', 'TALB', 'TPE1', 'TCON']:
                if key in audio.tags:
                    cipher_from_metadata += str(audio.tags[key][0])
            if cipher_from_metadata:
                ciphers['tertiary'] = cipher_from_metadata
    except Exception:
        pass
    
    return ciphers

def advanced_vigenere_decrypt(ciphertext, key, caesar_shift=3):
    """Multi-layer decryption: Caesar + Vigenère"""
    if not ciphertext or not key:
        return ""
    
    # Caesar decryption first
    caesar_decrypted = ""
    for char in ciphertext:
        if char.isalpha():
            offset = ord('A')
            shifted = (ord(char.upper()) - offset - caesar_shift) % 26
            caesar_decrypted += chr(shifted + offset)
        else:
            caesar_decrypted += char
    
    # Vigenère decryption
    key = key.upper()
    plaintext = ''
    key_index = 0
    
    for char in caesar_decrypted:
        if char.isalpha():
            offset = ord('A')
            c = ord(char.upper()) - offset
            k = ord(key[key_index % len(key)]) - offset
            p = (c - k) % 26
            plaintext += chr(p + offset)
            key_index += 1
        else:
            plaintext += char
    
    return plaintext

def check_solution_complexity(decrypted_text, pokemon_key):
    """Advanced solution validation"""
    success_indicators = [
        'FLAG{', 'CTF{', 'ETERNA', 'GHOST', 'GIRATINA', 
        'DISTORTION', 'WORLD', 'PLATINUM', 'SINNOH'
    ]
    
    pokemon_names = [
        'GIRATINA', 'DIALGA', 'PALKIA', 'ARCEUS', 'DARKRAI', 
        'CRESSELIA', 'ROTOM', 'SPIRITOMB'
    ]
    
    score = 0
    if any(indicator in decrypted_text.upper() for indicator in success_indicators):
        score += 10
    if pokemon_key.upper() in pokemon_names:
        score += 5
    
    return score >= 15

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audiofile' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['audiofile']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.wav'):
        return jsonify({'error': 'Only WAV files are accepted'}), 400
    
    try:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            file.save(tmp_file.name)
            
            sample_rate, data = wavfile.read(tmp_file.name)
            
            # Multi-layer LSB extraction
            lsb_layers = extract_multi_lsb_audio(data, [0, 1, 2])
            
            # Frequency domain analysis
            freq_data = extract_frequency_domain_data(data, sample_rate)
            
            # Advanced spectrograms
            spectrograms = generate_advanced_spectrogram(lsb_layers['layer_0'], sample_rate)
            
            # Complex metadata extraction
            ciphers = extract_complex_metadata(tmp_file.name)
            
            # Clean up
            os.unlink(tmp_file.name)
        
        return jsonify({
            'success': True,
            'spectrograms': spectrograms,
            'ciphers': ciphers,
            'frequency_data': freq_data,
            'hint': 'Multiple layers detected. Analyze ALL spectrograms and consider time-based elements.',
            'advanced_hint': 'Some ciphers use multi-stage decryption. Current time may be relevant.'
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/decrypt', methods=['POST'])
def decrypt_cipher():
    data = request.get_json()
    cipher_type = data.get('cipher_type', 'primary')
    cipher_text = data.get('cipher_text', '')
    key = data.get('key', '').strip().upper()
    caesar_shift = int(data.get('caesar_shift', 3))
    
    if not cipher_text or not key:
        return jsonify({'error': 'Missing cipher text or key'}), 400
    
    decrypted = advanced_vigenere_decrypt(cipher_text, key, caesar_shift)
    success = check_solution_complexity(decrypted, key)
    
    return jsonify({
        'success': True,
        'decrypted_message': decrypted,
        'congratulations': success,
        'complexity_score': 'High' if success else 'Partial',
        'hint': 'Try different cipher types and Caesar shifts if unsuccessful.' if not success else ''
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
