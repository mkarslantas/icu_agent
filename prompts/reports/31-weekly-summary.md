# Haftalık Özet Raporu

## Amaç
7 günlük hasta verilerini analiz ederek kapsamlı haftalık özet raporu oluşturmak.

## Giriş Verileri
- Son 7 günün yapılandırılmış JSON verileri
- Günlük SOFA skorları
- Önemli olaylar ve müdahaleler

## Çıktı Formatı

```markdown
# 📅 HAFTALIK ÖZET RAPORU

**Hasta ID:** [ID]
**Rapor Dönemi:** [YYYY-MM-DD] - [YYYY-MM-DD]
**YBÜ Yatış Günü:** [X-Y]

---

## 📊 GENEL SEYİR

**Haftalık Trend:** [✅ İyileşme / ⚠️ Karışık / 🚨 Kötüleşme]

**Özet:**
[2-3 paragraf: Hafta boyunca genel seyir, önemli olaylar, major müdahaleler, komplikasyonlar]

---

## 📈 SOFA SKORU TRENDİ

| Gün | SOFA | Delta | Yorum |
|-----|------|-------|-------|
| 1   | [X]  | -     | [başlangıç] |
| 2   | [X]  | +/-X  | [yorum] |
| ...

**Haftalık Değişim:** [başlangıç] → [son] ([iyileşme/kötüleşme])

---

## 🔍 SİSTEM BAZLI HAFTALIK DEĞERLENDİRME

### 🫀 Kardiyovasküler
**Hafta Başı:** Vazopresör [X], MAP [Y]
**Hafta Sonu:** Vazopresör [X], MAP [Y]
**Trend:** [iyileşme/kötüleşme/stabil]
**Önemli Olaylar:** [vazopresör ekleme/azaltma, kardiyak olay vb.]

### 🫁 Respiratuar
**Hafta Başı:** [ventilasyon durumu]
**Hafta Sonu:** [ventilasyon durumu]
**Önemli Olaylar:** [ekstübasyon, re-entübasyon, weaning denemesi]

### 💧 Renal
**Kreatinin Trendi:** [başlangıç] → [son]
**AKI Evresi:** [değişim varsa]
**İdrar Çıkışı:** [trend]

### 🦠 Enfeksiyon
**Antibiyotik Değişiklikleri:** [başlangıç] → [son]
**Kültür Sonuçları:** [önemli bulgular]
**Enflamatuar Belirteçler:** CRP [başlangıç] → [son], PCT [başlangıç] → [son]

---

## 🎯 MAJOR OLAYLAR ve MÜDAHALELER

### [Tarih]: [Olay Başlığı]
- **Detay:** [açıklama]
- **Müdahale:** [yapılan]
- **Sonuç:** [outcome]

---

## 💊 TEDAVİ ÖZETİ

**Antibiyotikler:**
- [Drug] ([X] gün) - [devam/tamamlandı/değiştirildi]

**Vazopresörler:**
- Hafta boyunca trend: [azaldı/arttı/stabil]

**Ventilasyon:**
- [Hafta başı mod/ayarlar] → [Hafta sonu mod/ayarlar]

---

## 📋 ÖNCELİKLİ SORUNLAR

1. **[Devam Eden Sorun 1]**
   - Durum: [açıklama]
   - Plan: [önümüzdeki hafta planı]

2. **[Devam Eden Sorun 2]**
   - Durum: [açıklama]
   - Plan: [önümüzdeki hafta planı]

---

## 🔮 ÖNÜMÜZDEKİ HAFTA HEDEF ve PLANLARI

**Ana Hedefler:**
1. [Hedef 1]
2. [Hedef 2]
3. [Hedef 3]

**Beklenen Gelişmeler:**
- [Ne bekleniyor]

**Potansiyel Komplikasyonlar:**
- [Risk faktörleri]

---

## 📊 SAYISAL ÖZET

| Parametre | Hafta Başı | Hafta Sonu | Değişim |
|-----------|------------|------------|---------|
| SOFA | [X] | [Y] | [+/-Z] |
| Vazopresör (NE) | [X] | [Y] | [↓/↑] |
| Laktat | [X] | [Y] | [↓/↑] |
| Kreatinin | [X] | [Y] | [↓/↑] |
| FiO2 | [X]% | [Y]% | [↓/↑] |
| WBC | [X] | [Y] | [↓/↑] |
| CRP | [X] | [Y] | [↓/↑] |

---

## 💭 GENEL DEĞERLENDİRME

[2-3 paragraf:
- Hastanın haftalık genel seyri
- Başarılı yönler
- Sorunlu alanlar
- Prognoz değerlendirmesi
- ICU'dan çıkış prospekti]

---

*Haftalık özet raporu*
*Oluşturulma: [YYYY-MM-DD]*

```

## Önemli Noktalar
- 7 günlük perspektif
- Trendlere odaklan
- Major olayları vurgula
- Önümüzdeki hafta için plan
- Prognoz değerlendirmesi

Kapsamlı, trend odaklı haftalık özet oluştur.
