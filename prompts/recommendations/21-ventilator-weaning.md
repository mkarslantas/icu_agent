# Ventilatör Weaning Önerileri

## Amaç
Mekanik ventilasyondan ayırma (weaning) hazırlığını değerlendirerek kanıta dayalı öneriler sunmak.

## Giriş Verileri
- Solunum parametreleri (RR, SpO2, FiO2, PaO2, P/F ratio)
- Ventilasyon ayarları (mod, PEEP, basınç desteği)
- Hemodinamik durum
- Nörolojik durum (GCS, sedation)
- Genel klinik durum

## Referans
`config/weaning-protocols.yaml` - Detaylı weaning kriterleri

## Çıktı Formatı
Türkçe markdown raporu:

```markdown
# 🫁 VENTİLATÖR WEANING DEĞERLENDİRMESİ

## Güncel Ventilasyon Durumu
**Mod:** [mode]
**PEEP:** [value] cmH2O
**FiO2:** [value]%
**SpO2:** [value]%
**P/F Ratio:** [value if available]
**Solunum Hızı:** [value]/dk

## Weaning Hazırlığı Kriterleri Değerlendirmesi

### 1. Oksijenasyon ✅/❌
**Kriter:** PaO2/FiO2 ≥150-200, PEEP ≤5-8, FiO2 ≤40-50%
**Durum:**
- P/F Ratio: [value] ([✓/✗])
- PEEP: [value] cmH2O ([✓/✗])
- FiO2: [value]% ([✓/✗])
**Değerlendirme:** [Yeterli / Yetersiz]

### 2. Hemodinamik Stabilite ✅/❌
**Kriter:** MAP ≥60-65, HR <140, minimal vazopresör
**Durum:**
- MAP: [value] mmHg ([✓/✗])
- Kalp hızı: [value] bpm ([✓/✗])
- Vazopresör: [drug and dose or none] ([✓/✗])
**Değerlendirme:** [Stabil / İnstabil]

### 3. Mental Durum ✅/❌
**Kriter:** GCS ≥13, uyarılabilir, koopere
**Durum:**
- GCS: [value] ([✓/✗])
- RASS: [value] ([✓/✗])
- Komutlara uyuyor: [Evet/Hayır] ([✓/✗])
**Değerlendirme:** [Yeterli / Yetersiz]

### 4. Diğer Kriterler
- **Hemoglobin:** [value] g/dL (Hedef ≥7-10) ([✓/✗])
- **Asit-Baz:** pH [value] (Hedef ≥7.25) ([✓/✗])
- **Elektrolit:** K+ [value], Mg2+ [value], PO4 [value] ([✓/✗])

## Weaning Hazırlığı Sonucu

### ✅ HAZIR - Spontan Solunum Denemesi (SBT) Başlanabilir
[Eğer tüm kriterler karşılanıyorsa]

**SBT Protokolü:**
1. **Yöntem:** Basınç desteği 5-8 cmH2O + PEEP 5 cmH2O (tercih edilen)
   - Alternatif: T-piece 30-120 dakika
2. **Süre:** 30-120 dakika
3. **İzlem:** Her 5-15 dakikada vital bulgular

**SBT Başarı Kriterleri (30-120 dk boyunca):**
- RR <35/dk
- SpO2 >90%
- HR <140 bpm ve %20'den fazla artış yok
- Sistolik KB 90-180 mmHg
- Mental durum değişikliği yok
- Solunum sıkıntısı bulgusu yok

**SBT Başarısızlık Kriterleri (Hemen Durdurun):**
- RR >35/dk (>5 dk)
- SpO2 <90%
- HR >140 veya %20 artış
- Sistolik KB <90 veya >180 mmHg
- Ajitasyon, anksiyete, bilinç değişikliği
- Yardımcı solunum kası kullanımı

**Sonraki Adım:**
- SBT başarılı → Ekstübasyon değerlendirmesi
- SBT başarısız → Rahat ventilasyon ayarlarına dön, 24 saat sonra tekrar dene

### ⚠️ HAZIR DEĞİL - Optimizasyon Gerekli
[Eğer kriterler karşılanmıyorsa]

**Engeller:**
1. [Karşılanmayan kriter 1]
2. [Karşılanmayan kriter 2]

**Optimizasyon Önerileri:**

#### Oksijenasyon İyileştirme
- [Spesifik öneri: PEEP artırma, recruitment, prone pozisyon, diüretik]

#### Hemodinamik Stabilizasyon
- [Spesifik öneri: sıvı, vazopresör optimizasyonu]

#### Mental Durum Optimizasyonu
- [Spesifik öneri: sedasyon kesme, delirium yönetimi]

**Tekrar Değerlendirme:** [24 saat / 48 saat sonra]

### 🔄 KADEMELI WEANING Devam
[Eğer aktif weaning sürecindeyse]

**Güncel Strateji:**
- Basınç desteğini kademeli azaltma (günde 2 cmH2O)
- Hedef PS 5-8 cmH2O → SBT dene

**İlerleme:**
[Trend değerlendirmesi]

## Ekstübasyon Hazırlığı (Eğer SBT Başarılı)

### Havayolu Koruma Değerlendirmesi
- **Öksürük gücü:** [Güçlü / Orta / Zayıf]
- **Gag refleksi:** [İntakt / Zayıf]
- **Sekresyon yönetimi:** [İyi / Sık aspirasyon gerekiyor]

### Üst Havayolu Açıklığı
**Cuff Leak Test İndikasyonu:** [Evet/Hayır]
- Risk faktörleri: Uzun süreli entübasyon (>6 gün), kadın, travmatik entübasyon
- **Sonuç:** [Pozitif/Negatif/Yapılmadı]

### Ekstübasyon Kararı
[✓ EKSTÜBAsıyon ÖNERİLİR / ❌ EKSTÜBAsıon ERTELENMELİ]

**Ekstübasyon Sonrası Plan:**
- **Oksijen:** [Nasal kanül / Maske / HFNC / NIV]
- **Hedef SpO2:** >92-94%
- **Pulmoner toilette:** Teşvik spirometresi, erken mobilizasyon
- **İzlem:** İlk 24 saat yakın takip

## Zor Weaning Durumu

### Tanım
≥3 başarısız weaning denemesi veya >7 gün weaning süresi

### Olası Nedenler
- **Solunum:** Solunum kas güçsüzlüğü, KOAH, yüksek ventilasyon gereksinimi
- **Kardiyak:** Kalp yetmezliği, diastolik disfonksiyon, weaning sırasında iskemi
- **Nörolojik:** ICU-acquired weakness, delirium, frenik sinir disfonksiyonu
- **Metabolik:** Elektrolit bozuklukları, malnütrisyon, hipotiroidi
- **Psikolojik:** Anksiyete, ventilator bağımlılığı

### Yönetim Stratejileri
- [Spesifik öneriler nedenlere göre]
- Erken trakeostomi düşünülmeli (>14-21 gün ventilasyon beklentisi)

## Kanıt Temeli
- **Ely et al. 1996:** Günlük SBT screening ventilasyon süresini azaltır
- **Girard et al. 2008 (ABC Trial):** SAT + SBT mortaliteyi azaltır
- **Brochard et al. 1994:** Basınç desteği weaningi SIMV ve T-piece'e üstün

## Özet Öneri
**[1-2 cümlelik net, uygulanabilir öneri]**

Örnekler:
- "Hasta SBT için hazır. PS 8 cmH2O + PEEP 5 cmH2O ile 120 dakika SBT önerilir, başarı halinde ekstübasyon planlanabilir."
- "FiO2 %60 ile hala hipoksemik, PEEP 12 cmH2O gerekiyor. Önce oksijenasyon optimizasyonu (diürez, prone), 48 saat sonra weaning tekrar değerlendirilmeli."

---
*Bu öneriler karar destek amaçlıdır. Ekstübasyon kararı klinisyen takdirine bağlıdır.*
```

## Önemli İlkeler
1. **Günlük Screening:** Her gün weaning hazırlığını değerlendir
2. **Sedasyon:** Sedasyon kesme + SBT kombinasyonu güçlü
3. **Gecikme Maliyeti:** Gereksiz uzun ventilasyon VAP, zayıflık, uzun yatış
4. **Başarısızlık Zararsız:** Başarısız SBT diagnostik bilgi verir
5. **Hazırlık:** Hasta optimizasyonu (ağrı, pozisyon, sekresyon temizliği)
6. **Trakeostomi:** Uzun süreli ventilasyon beklentisinde erken düşünülmeli
7. **Post-Ekstübasyon NIV:** Yüksek riskli hastalarda re-entübasyon önler

Tüm öneriler Türkçe, spesifik, kanıta dayalı ve uygulanabilir olmalıdır.
