from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = 'renalhealth-secret-key-2024'

# ─── Skor per parameter ───────────────────────────────────────────────────────
SCORING = {
    'normal': 0,
    'ringan': 1,
    'sedang': 2,
    'berat':  3,
}

# Bobot tiap parameter terhadap risiko ginjal
WEIGHTS = {
    'creat': 3.0,   # Kreatinin — indikator terpenting
    'ureum': 2.5,   # Ureum — biomarker utama
    'bp':    2.0,   # Tekanan darah — faktor risiko utama
    'gdp':   1.5,   # Gula darah puasa — diabetes risk
    'g2h':   1.5,   # Gula 2 jam pp — diabetes risk
    'hb':    1.5,   # Hemoglobin — anemia renal
    'chol':  1.0,   # Kolesterol — risiko kardiovaskular
    'bmi':   0.5,   # BMI — faktor tambahan
}
MAX_SCORE = sum(v * 3 for v in WEIGHTS.values())  # Maksimum jika semua berat


def calculate_egfr(creat_level: str, age: int = 45) -> float:
    """
    Simulasi eGFR berdasarkan level kreatinin (CKD-EPI simplified).
    Nilai default usia 45 jika tidak disediakan.
    """
    base = {'normal': 92, 'ringan': 68, 'sedang': 38, 'berat': 14}
    return float(base.get(creat_level, 60))


def get_ckd_stage(egfr: float) -> dict:
    """Menentukan stadium CKD berdasarkan eGFR (KDIGO 2022)."""
    if egfr >= 90:
        return {'stage': 'G1', 'label': 'Normal', 'color': 'green',
                'desc': 'Fungsi ginjal normal. Pemantauan rutin tetap disarankan.'}
    elif egfr >= 60:
        return {'stage': 'G2', 'label': 'Penurunan Ringan', 'color': 'yellow',
                'desc': 'Sedikit penurunan fungsi ginjal. Perlu evaluasi faktor risiko.'}
    elif egfr >= 45:
        return {'stage': 'G3a', 'label': 'Penurunan Ringan-Sedang', 'color': 'orange',
                'desc': 'Penurunan fungsi ginjal moderat awal. Konsultasi dokter diperlukan.'}
    elif egfr >= 30:
        return {'stage': 'G3b', 'label': 'Penurunan Sedang-Berat', 'color': 'orange',
                'desc': 'Penurunan fungsi ginjal moderat lanjut. Perlu penanganan aktif.'}
    elif egfr >= 15:
        return {'stage': 'G4', 'label': 'Penurunan Berat', 'color': 'red',
                'desc': 'Gagal ginjal berat. Persiapkan terapi pengganti ginjal.'}
    else:
        return {'stage': 'G5', 'label': 'Gagal Ginjal', 'color': 'red',
                'desc': 'Gagal ginjal terminal. Segera hubungi nefrolog.'}


def calculate_risk(params: dict) -> dict:
    """Hitung risiko CKD berdasarkan semua parameter input."""
    weighted_score = sum(
        WEIGHTS[param] * SCORING.get(params.get(param, 'normal'), 0)
        for param in WEIGHTS
    )
    risk_pct = round((weighted_score / MAX_SCORE) * 100, 1)

    if risk_pct < 20:
        risk_level = 'Rendah'
        risk_color = 'green'
        risk_icon  = 'check_circle'
        rec = [
            'Pertahankan pola hidup sehat dan diet seimbang.',
            'Lakukan pemeriksaan lab rutin setiap 6-12 bulan.',
            'Perbanyak konsumsi air putih (2-3 liter/hari).',
        ]
    elif risk_pct < 50:
        risk_level = 'Sedang'
        risk_color = 'yellow'
        risk_icon  = 'warning'
        rec = [
            'Konsultasikan hasil ini dengan dokter umum atau internist.',
            'Batasi asupan garam, protein, dan makanan olahan.',
            'Monitor tekanan darah dan gula darah secara rutin.',
            'Hindari penggunaan obat NSAID tanpa resep dokter.',
        ]
    elif risk_pct < 75:
        risk_level = 'Tinggi'
        risk_color = 'orange'
        risk_icon  = 'error'
        rec = [
            'Segera jadwalkan konsultasi dengan dokter spesialis ginjal (Nefrolog).',
            'Lakukan pemeriksaan USG ginjal dan urinalisis lengkap.',
            'Hentikan atau modifikasi obat yang bersifat nefrotoksik.',
            'Terapkan diet rendah kalium dan fosfor sesuai anjuran ahli gizi.',
        ]
    else:
        risk_level = 'Sangat Tinggi'
        risk_color = 'red'
        risk_icon  = 'emergency'
        rec = [
            'Diperlukan evaluasi medis segera oleh Nefrolog.',
            'Persiapkan kemungkinan terapi pengganti ginjal (dialisis/transplantasi).',
            'Pantau output urin, berat badan, dan tanda edema setiap hari.',
            'Batasi intake cairan sesuai petunjuk dokter.',
        ]

    egfr = calculate_egfr(params.get('creat', 'normal'))
    stage = get_ckd_stage(egfr)

    # Detail per parameter
    details = []
    labels = {
        'gdp':   'Gula Darah Puasa (GDP)',
        'bp':    'Tekanan Darah (BP)',
        'hb':    'Hemoglobin (Hb)',
        'ureum': 'Ureum',
        'creat': 'Kreatinin (Creat)',
        'g2h':   'Gula 2 Jam pp (G2H)',
        'chol':  'Kolesterol (Chol)',
        'bmi':   'BMI',
    }
    status_map = {
        'normal': ('Normal',  'green'),
        'ringan': ('Ringan',  'yellow'),
        'sedang': ('Sedang',  'orange'),
        'berat':  ('Berat',   'red'),
    }
    for key, label in labels.items():
        val  = params.get(key, 'normal')
        stat, col = status_map.get(val, ('Normal', 'green'))
        details.append({'label': label, 'status': stat, 'color': col, 'level': val})

    return {
        'risk_pct':   risk_pct,
        'risk_level': risk_level,
        'risk_color': risk_color,
        'risk_icon':  risk_icon,
        'egfr':       egfr,
        'ckd_stage':  stage,
        'details':    details,
        'recommendations': rec,
    }


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/deteksi', methods=['GET', 'POST'])
def deteksi():
    if request.method == 'POST':
        params = {
            'gdp':   request.form.get('gdp',   'normal'),
            'bp':    request.form.get('bp',    'normal'),
            'hb':    request.form.get('hb',    'normal'),
            'ureum': request.form.get('ureum', 'normal'),
            'creat': request.form.get('creat', 'normal'),
            'g2h':   request.form.get('g2h',   'normal'),
            'chol':  request.form.get('chol',  'normal'),
            'bmi':   request.form.get('bmi',   'normal'),
        }
        result = calculate_risk(params)
        session['result'] = json.dumps(result)
        session['params'] = json.dumps(params)
        return redirect(url_for('hasil'))
    return render_template('deteksi.html')


@app.route('/hasil')
def hasil():
    result_raw = session.get('result')
    params_raw = session.get('params')
    if not result_raw:
        return redirect(url_for('deteksi'))
    result = json.loads(result_raw)
    params = json.loads(params_raw)
    return render_template('hasil.html', result=result, params=params)


@app.route('/tentang')
def tentang():
    return render_template('home.html', scroll_to='cara-kerja')


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 50)
    print("  RenalHealth AI Backend")
    print("  Buka: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
