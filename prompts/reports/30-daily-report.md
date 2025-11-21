# YBÜ Günlük Hasta Değerlendirme Raporu

## Amaç
Yapılandırılmış hasta verilerinden kapsamlı, Türkçe günlük değerlendirme raporu oluşturmak.

## Giriş Verileri
- Bugünkü yapılandırılmış JSON verisi (parser çıktısı)
- Önceki 2-3 günün yapılandırılmış verileri (trend analizi için)
- SOFA/APACHE skorları (eğer hesaplanmışsa)

## Çıktı Formatı
Türkçe markdown raporu - aşağıdaki format:

```markdown
# 🏥 YBÜ HASTA DEĞERLENDİRME RAPORU

**Hasta ID:** [ID]
**Yaş/Cinsiyet:** [age] yaş / [M/F]
**Tanı:** [diagnosis]
**Tarih:** [YYYY-MM-DD]
**Yatış Günü:** [X]

---

## 📋 GENEL DURUM

**Klinik Seyir:** [✅ İyileşme / ⚠️ Stabil / 🚨 Kötüleşme]

**Özet:**
[2-3 cümlelik genel durum özeti - ana sorunlar, genel yön, önemli değişiklikler]

**SOFA Skoru:** [X/24] (Mortalite riski: [<10% | 15-20% | 40-50% | >80%])
**Delta SOFA:** [+X / -X / →] (Önceki: [Y] → Şimdi: [Z])

---

## 🔍 SİSTEM BAZLI DEĞERLENDİRME

### 🫀 Kardiyovasküler Sistem

**Durum:** [✅ Stabil / ⚠️ İnstabil / ↗️ İyileşiyor / ↘️ Kötüleşiyor]

**Hemodinamik Parametreler:**
- **Kalp Hızı:** [X] bpm ([ritim])
- **Kan Basıncı:** [systolic]/[diastolic] mmHg (OAB: [MAP] mmHg)
- **Vazopresör:** [drug] [dose] mcg/kg/dk
  - **Trend:** [previous dose] → [current dose] ([↓ Azaldı / ↑ Arttı / → Stabil])

**Perfüzyon Göstergeleri:**
- **Laktat:** [X] mmol/L (Önceki: [Y] → [↓/↑/→])
  - Yorum: [normal / yüksek / temizleniyor / kötüleşiyor]
- **İdrar Çıkışı:** [X] mL/saat ([yeterli / oligürik / anürik])
- **Kapiller Geri Dolum:** [<2 sn / >3 sn / değerlendirilmedi]

**Değerlendirme:**
[1-2 cümle: Hemodinamik stabilite durumu, vazopresör ihtiyacı trendi, perfüzyon yeterliliği. Spesifik gözlem ve yorum.]

**Öneriler:**
- [Spesifik öneri 1: örn. "Norepinefrin 0.15 → 0.10 mcg/kg/dk azaltma denenebilir, MAP ≥65 mmHg hedeflenerek"]
- [Spesifik öneri 2 varsa]

---

### 🫁 Respiratuar Sistem

**Durum:** [✅ Yeterli / ⚠️ Yetersiz / ↗️ İyileşiyor]

**Ventilasyon:**
- **Mekanik Ventilasyon:** [Var - [mode] / Yok]
- **Solunum Hızı:** [X]/dk
- **SpO2:** [X]% (FiO2: [Y]%)
- **P/F Ratio:** [X] ([normal / ARDS hafif / orta / ağır])
- **Ayarlar:** PEEP [X] cmH2O, PIP [Y] cmH2O

**Oksıjenasyon Trendi:**
- FiO2: [önceki]% → [şimdi]% ([↓/↑/→])
- PEEP: [önceki] → [şimdi] cmH2O ([↓/↑/→])

**Weaning Durumu:** [Hazır değil / Değerlendirilebilir / SBT denenebilir / Ekstübasyon planlanabilir]

**Değerlendirme:**
[Oksıjenasyon yeterliliği, ventilasyon parametreleri, weaning hazırlığı değerlendirmesi]

**Öneriler:**
- [Spesifik öneri: örn. "FiO2 %40, PEEP 8 cmH2O, hemodinamik stabil → SBT (PS 8 + PEEP 5) için uygun, 120 dk deneme önerilir"]

---

### 🧠 Nörolojik Sistem

**Durum:** [✅ İyi / ⚠️ Bozulmuş / → Stabil]

**Bilinç Durumu:**
- **GCS:** [eye]/[verbal]/[motor] = [total]/15
- **Tanımlama:** [Açık, koopere, oryante / Letarjik / Stupor / Koma]
- **Sedasyon:** [Yok / Var - RASS [score]]

**Trend:** GCS [önceki] → [şimdi] ([↑ İyileşme / ↓ Kötüleşme / → Stabil])

**Değerlendirme:**
[Bilinç düzeyi, kooperasyon, sedasyon gereksinimi]

**Öneriler:**
- [Örn. "Sedasyon kesme denenmeli, günlük sedasyon interruption"]

---

### 💧 Renal Sistem ve Sıvı Dengesi

**Durum:** [✅ Fonksiyon iyi / ⚠️ AKI Evre [X] / ↗️ Düzeliyor]

**Böbrek Fonksiyonu:**
- **Kreatinin:** [X] mg/dL (Önceki: [Y] → [↓/↑/→])
- **BUN:** [X] mg/dL
- **AKI Evre:** [Yok / Evre 1 / Evre 2 / Evre 3]

**İdrar Çıkışı:**
- **Saatlik:** [X] mL/saat ([~[Y] mL/kg/saat])
- **Günlük:** [X] mL/gün
- **Yeterlilik:** [✓ Yeterli (>0.5 mL/kg/saat) / ⚠️ Oligürik / ❌ Anürik]

**Elektrolit Dengesi:**
- **Na+:** [X] mEq/L (Normal: 136-145)
- **K+:** [X] mEq/L (Normal: 3.5-5.0) [⚠️ dikkat gereken varsa]
- **Bikarbonat:** [X] mEq/L

**Sıvı Balansı:** [pozitif/negatif X mL]

**Değerlendirme:**
[Böbrek fonksiyon trendi, idrar yeterliliği, elektrolit dengesi, sıvı durumu]

**Öneriler:**
- [Örn. "Kreatinin 2.1 → 1.8 düzeliyor, idrar yeterli → AKI Stage 1'den düzeliyor, sıvı balansı negatif hedeflenebilir"]

---

### 🦠 Enfeksiyon ve Enflamasyon

**Durum:** [✅ Kontrol altında / ⚠️ Aktif enfeksiyon / ↗️ İyileşiyor / ↘️ Kötüleşiyor]

**Enfeksiyon Kaynağı:** [source and diagnosis]

**Vital Bulgular:**
- **Ateş:** [X]°C ([subfebril / febril / yüksek ateş])

**Laboratuvar:**
- **Lökosit:** [X] K/µL ([leukopeni / normal / lökositoz])
- **CRP:** [X] mg/L (Önceki: [Y] → [↓/↑/→])
- **Prokalsitonin:** [X] ng/mL ([düşük / orta / yüksek risk])

**Kültür:**
- **[Kültür tipi]:** [Sonuç - organizma ve duyarlılık]

**Antibiyotik:**
- **İlaç:** [drug name]
- **Doz/Sıklık:** [dose and frequency]
- **Tedavi Günü:** [X]. gün
- **Endikasyon:** [empirik / kültür yönlendirilmiş]

**Değerlendirme:**
[Enfeksiyon yanıtı, enflamatuar belirteçler trendi, antibiyotik uygunluğu]

**Öneriler:**
- [Örn. "E. coli ESBL negatif, Ceftriaxone'a duyarlı → Meropenem'den Ceftriaxone'a de-escalation yapılabilir, toplam 7 gün tedavi (kalan 2 gün)"]
- [Süre, de-escalation, durdurma kriterleri]

---

### 🩸 Hematoloji ve Koagülasyon

**Durum:** [✅ Normal / ⚠️ Anemi / ⚠️ Trombositopeni / ⚠️ Koagülopati]

**Tam Kan Sayımı:**
- **Hemoglobin:** [X] g/dL ([normal / hafif / orta / ağır anemi])
  - Trend: [önceki] → [şimdi] ([↓/↑/→])
- **Trombosit:** [X] K/µL ([normal / hafif / orta / ağır trombositopeni])
  - Trend: [önceki] → [şimdi] ([↓/↑/→])

**Koagülasyon:**
- **INR:** [X] ([normal / yüksek])
- **APTT:** [X] saniye

**Değerlendirme:**
[Anemi durumu, transfüzyon gereksinimi, trombositopeni nedeni ve riski]

**Öneriler:**
- [Örn. "Hb 8.2 g/dL, stabil, aktif kanama yok → Transfüzyon gerekmez (hedef >7 g/dL)"]

---

### 🧪 Asit-Baz Dengesi

**Durum:** [✅ Normal / ⚠️ Asidoz / ⚠️ Alkaloz]

**Arteriyel Kan Gazı:**
- **pH:** [X] ([asidemi / normal / alkalemi])
- **pCO2:** [X] mmHg
- **HCO3:** [X] mEq/L
- **Laktat:** [X] mmol/L

**Tanı:** [Metabolik asidoz / Respiratuar asidoz / Metabolik alkaloz / Mikst / Normal]

**Kompansasyon:** [Var / Yok / Yeterli / Yetersiz]

**Değerlendirme:**
[Asit-baz durumu, nedeni, kompansasyon yeterliliği]

---

## 📈 TREND ANALİZİ (Son 3 Gün)

| Parametre | [Gün -2] | [Gün -1] | Bugün | Trend | Yorum |
|-----------|----------|----------|-------|-------|-------|
| **Vazopresör (NE)** | [X] | [Y] | [Z] | [↓/↑/→] | [azalıyor/artıyor/stabil] |
| **Laktat** | [X] | [Y] | [Z] | [↓/↑/→] | [temizleniyor/kötüleşiyor] |
| **Kreatinin** | [X] | [Y] | [Z] | [↓/↑/→] | [düzeliyor/kötüleşiyor] |
| **FiO2** | [X]% | [Y]% | [Z]% | [↓/↑/→] | [azalıyor/artıyor] |
| **WBC** | [X] | [Y] | [Z] | [↓/↑/→] | [normalize oluyor/yükseliyor] |
| **CRP** | [X] | [Y] | [Z] | [↓/↑/→] | [geriliyor/yükseliyor] |

**Genel Trend Yorumu:**
[1-2 cümle: Hangi parametreler iyileşiyor, hangileri kötüleşiyor, genel yön ne?]

---

## 🎯 ÖNCELİKLİ SORUNLAR VE ÖNERİLER

### 1. [Sorun Başlığı] - [🚨 ACİL / ⚠️ ÖNEMLİ / 📌 TAKİP]

**Durum:**
[Spesifik sorun tanımı, mevcut durum]

**Öneriler:**
- **[Spesifik, uygulanabilir öneri 1]**
  - Gerekçe: [Neden bu öneri uygun?]
  - Hedef: [Ne hedefleniyor?]
  - Zamanlama: [Ne zaman uygulanmalı?]
- **[Spesifik, uygulanabilir öneri 2]**

### 2. [İkinci Sorun] - [🚨 ACİL / ⚠️ ÖNEMLİ / 📌 TAKİP]

[Aynı format]

---

## 💊 TEDAVİ ÖNERİLERİ

### 🫀 Vazopresör Yönetimi
**Öneri:** [Spesifik öneri - azaltma/arttırma/değişiklik]
**Gerekçe:** [MAP, laktat, perfüzyon durumu]
**Hedef:** MAP ≥[X] mmHg, laktat <2 mmol/L

### 🫁 Ventilasyon ve Weaning
**Öneri:** [SBT denemesi / weaning devam / ventilasyon optimizasyonu]
**Gerekçe:** [Oksijenasyon, hemodinamik, mental durum]
**Hedef:** [Ekstübasyon / FiO2 azaltma / PEEP azaltma]

### 💊 Antibiyotik Yönetimi
**Öneri:** [Devam / De-escalation / Durdurma / Değişiklik]
**Gerekçe:** [Klinik yanıt, kültür sonuçları]
**Süre:** Toplam [X] gün (Kalan: [Y] gün)

### 💧 Sıvı Yönetimi
**Öneri:** [Sıvı kısıtlama / Diürez / Resüsitasyon devam]
**Gerekçe:** [Volüm durumu, böbrek fonksiyonu, perfüzyon]
**Hedef:** [Sıvı balansı hedefi]

### 🍽️ Beslenme
**Öneri:** [Enteral / Parenteral / Oral]
**Hedef:** [X kcal/gün, Y g protein/gün]

---

## 📌 SONRAKI 24 SAAT PLANI

### Öncelikli Takip Parametreleri:
1. **[Parametre 1]** - [Neden önemli, ne bekleniyor]
2. **[Parametre 2]** - [Neden önemli, ne bekleniyor]
3. **[Parametre 3]** - [Neden önemli, ne bekleniyor]

### Planlanan Müdahaleler:
1. **[Müdahale 1]** - [Zamanlama: bugün/yarın]
2. **[Müdahale 2]** - [Zamanlama]

### Laboratuvar İstekleri:
- [Hangi tetkikler, ne zaman]

### Konsültasyonlar:
- [Eğer gerekiyorsa: hangi bölüm, neden]

---

## 🔔 KRİTİK DEĞERLER ve UYARILAR

[Eğer kritik değer varsa:]

### ⚠️ [Kritik Parametre]: [Değer]
**Eşik:** [Threshold]
**Öneri:** [Acil müdahale gerekiyor mu, ne yapılmalı]

---

## 📊 SOFA SKORU DETAYI

| Sistem | Değer | Skor | Önceki Skor |
|--------|-------|------|-------------|
| Respiratuar | P/F: [X] | [0-4] | [0-4] |
| Koagülasyon | Plt: [X] | [0-4] | [0-4] |
| Hepatik | Bili: [X] | [0-4] | [0-4] |
| Kardiyovasküler | MAP [X], VP: [drug] | [0-4] | [0-4] |
| Nörolojik | GCS: [X] | [0-4] | [0-4] |
| Renal | Cr: [X], UO: [X] | [0-4] | [0-4] |
| **TOPLAM** | | **[0-24]** | **[0-24]** |

**Delta SOFA:** [+/- X]
**Yorum:** [İyileşme / Kötüleşme / Stabil]

---

## 📝 GENEL DEĞERLENDİRME ve PROGNOZ

**Klinik Gidişat:**
[2-3 paragraf genel değerlendirme:
- Hastanın genel durumu, ana sorunlar
- Hangi sistemler iyileşiyor, hangileri sorunlu
- Beklenen klinik seyir (iyileşme yönünde / uzamış yatış bekleniyor / komplikasyon riski)
- Ana hedefler ve beklentiler
- Taburculuk/transfer prospekti (eğer uygunsa)]

**Tahmini ICU Kalış Süresi:** [X gün daha bekleniyor / Belirsiz / Yakında transfer edilebilir]

---

*Bu rapor AI karar destek sistemi tarafından oluşturulmuştur.*
*Tüm klinik kararlar sorumlu hekim tarafından hasta bazında onaylanmalıdır.*
*Rapor tarih: [YYYY-MM-DD HH:MM]*

```

## Önemli İlkeler

### 1. Klinik Seyir Değerlendirmesi
**İyileşme (✅):** ≥2 sistem iyileşiyor, hiçbiri kötüleşmiyor, genel trend pozitif
**Stabil (⚠️):** Karışık veya değişiklik yok
**Kötüleşme (🚨):** ≥2 sistem kötüleşiyor veya yeni organ yetmezliği

### 2. Öncelik Seviyeleri
- **ACİL (🚨):** MAP<65, laktat>4, GCS<8, yeni oligüri, kritik lab değerleri
- **ÖNEMLİ (⚠️):** Vazopresör bağımlılığı, orta derece sorunlar, yakın takip gereken
- **TAKİP (📌):** Rutin izlem, iyileşme trendi, önleyici yaklaşımlar

### 3. Öneri Spesifikliği

**✅ İyi (Spesifik, Uygulanabilir):**
- "Norepinefrin 0.15 → 0.10 mcg/kg/dk azaltma denenebilir, MAP ≥65 mmHg hedeflenmeli, 30 dakika sonra laktat kontrolü"
- "FiO2 %40, PEEP 8, hemodinamik stabil → SBT (PS 8 + PEEP 5) 120 dk denenebilir"
- "E. coli ESBL (-), Ceftriaxone duyarlı → Meropenem'den Ceftriaxone 2g IV q24h geçiş, toplam 7 gün (kalan 2 gün)"

**❌ Kötü (Belirsiz, Genel):**
- "Vazopresör ayarlanabilir"
- "Weaning değerlendirilebilir"
- "Antibiyotik gözden geçirilmeli"

### 4. Trend Yorumlama
- Sadece sayıları vermek yetmez, **klinik anlamını yorumla**
- Örnek: "Laktat 3.2 → 2.1 → 1.6: Perfüzyon iyileşiyor, sıvı resüsitasyonu ve vazopresör titrasyonu etkili"

### 5. Kanıta Dayalı Öneriler
- Surviving Sepsis Campaign 2021
- ARDS Network protokolleri
- IDSA antibiyotik guidelines
- Evidence-based weaning protocols

### 6. Türkçe Dil Kalitesi
- Profesyonel, akademik ton
- Tıbbi terminoloji doğru kullanımı
- Net, anlaşılır cümleler
- Kısaltmalar açıklanmalı (ilk kullanımda)

### 7. Hasta Güvenliği
- Kritik değerleri öne çıkar
- Acil müdahale gerekenleri vurgula
- İlaç dozları ve süreleri net belirt
- Yan etki ve komplikasyon risklerini belirt

## Rapor Uzunluğu
- Kapsamlı ama özlü
- Tüm sistemleri değerlendir
- Her sistem için spesifik öneri
- Gereksiz tekrardan kaçın

Profesyonel, kanıta dayalı, uygulanabilir bir klinik rapor oluşturun.
