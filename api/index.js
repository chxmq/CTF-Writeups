import express from 'express';
import multer from 'multer';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// Configure multer for file uploads
const upload = multer({
    dest: 'uploads/',
    fileFilter: (req, file, cb) => {
        if (file.mimetype === 'audio/wav' || file.originalname.toLowerCase().endsWith('.wav')) {
            cb(null, true);
        } else {
            cb(new Error('Only WAV files are allowed'), false);
        }
    },
    limits: {
        fileSize: 50 * 1024 * 1024 // 50MB limit
    }
});

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, '../')));

// Serve the main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../templates/index.html'));
});

// Upload endpoint
app.post('/upload', upload.single('audiofile'), (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No file uploaded' });
        }

        // Simulate the analysis process
        const mockSpectrograms = {
            primary: generateMockBase64Image(),
            high_res: generateMockBase64Image(),
            phase: generateMockBase64Image()
        };

        const mockCiphers = {
            primary: "NKOOR_IURP_JLUDWLQD_UHDOP",
            secondary: "FDHVDU_FLSKHU_ZLWK_NHBZRUG",
            tertiary: "WLPH_EDVHG_HQFULSWLRQ",
            quaternary: `WLPH_VKLIW_${(new Date().getHours() % 13).toString().padStart(2, '0')}`
        };

        // Clean up uploaded file
        fs.unlinkSync(req.file.path);

        res.json({
            success: true,
            spectrograms: mockSpectrograms,
            ciphers: mockCiphers,
            frequency_data: [0, 1, 0, 1],
            hint: 'Multiple layers detected. Analyze ALL spectrograms and consider time-based elements.',
            advanced_hint: 'Some ciphers use multi-stage decryption. Current time may be relevant.'
        });

    } catch (error) {
        console.error('Upload error:', error);
        res.status(500).json({ error: 'Processing failed: ' + error.message });
    }
});

// Decrypt endpoint
app.post('/decrypt', (req, res) => {
    try {
        const { cipher_type, cipher_text, key, caesar_shift = 3 } = req.body;

        if (!cipher_text || !key) {
            return res.status(400).json({ error: 'Missing cipher text or key' });
        }

        // Implement basic Caesar + Vigenère decryption
        const decrypted = advancedVigenereDecrypt(cipher_text, key.trim().toUpperCase(), parseInt(caesar_shift));
        const success = checkSolutionComplexity(decrypted, key.trim().toUpperCase());

        res.json({
            success: true,
            decrypted_message: decrypted,
            congratulations: success,
            complexity_score: success ? 'High' : 'Partial',
            hint: success ? '' : 'Try different cipher types and Caesar shifts if unsuccessful.'
        });

    } catch (error) {
        console.error('Decrypt error:', error);
        res.status(500).json({ error: 'Decryption failed: ' + error.message });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'ok', message: 'Eterna Forest CTF is running' });
});

// Helper functions
function generateMockBase64Image() {
    // Generate a simple mock base64 image (1x1 pixel PNG)
    return 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';
}

function advancedVigenereDecrypt(ciphertext, key, caesarShift = 3) {
    if (!ciphertext || !key) return "";

    // Caesar decryption first
    let caesarDecrypted = "";
    for (let char of ciphertext) {
        if (char.match(/[A-Za-z]/)) {
            const offset = char.charCodeAt(0) >= 65 && char.charCodeAt(0) <= 90 ? 65 : 97;
            const shifted = (char.toUpperCase().charCodeAt(0) - 65 - caesarShift + 26) % 26;
            caesarDecrypted += String.fromCharCode(shifted + 65);
        } else {
            caesarDecrypted += char;
        }
    }

    // Vigenère decryption
    let plaintext = '';
    let keyIndex = 0;

    for (let char of caesarDecrypted) {
        if (char.match(/[A-Za-z]/)) {
            const c = char.toUpperCase().charCodeAt(0) - 65;
            const k = key[keyIndex % key.length].charCodeAt(0) - 65;
            const p = (c - k + 26) % 26;
            plaintext += String.fromCharCode(p + 65);
            keyIndex++;
        } else {
            plaintext += char;
        }
    }

    return plaintext;
}

function checkSolutionComplexity(decryptedText, pokemonKey) {
    const successIndicators = [
        'FLAG{', 'CTF{', 'ETERNA', 'GHOST', 'GIRATINA',
        'DISTORTION', 'WORLD', 'PLATINUM', 'SINNOH'
    ];

    const pokemonNames = [
        'GIRATINA', 'DIALGA', 'PALKIA', 'ARCEUS', 'DARKRAI',
        'CRESSELIA', 'ROTOM', 'SPIRITOMB'
    ];

    let score = 0;
    if (successIndicators.some(indicator => decryptedText.toUpperCase().includes(indicator))) {
        score += 10;
    }
    if (pokemonNames.includes(pokemonKey.toUpperCase())) {
        score += 5;
    }

    return score >= 15;
}

// Error handling middleware
app.use((error, req, res, next) => {
    if (error instanceof multer.MulterError) {
        if (error.code === 'LIMIT_FILE_SIZE') {
            return res.status(400).json({ error: 'File too large. Maximum size is 50MB.' });
        }
    }
    res.status(500).json({ error: error.message });
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Visit http://localhost:${PORT} to access the CTF challenge`);
});