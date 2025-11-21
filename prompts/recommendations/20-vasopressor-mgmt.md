# Vazopresör Yönetimi Önerileri

## Amaç
Hemodinamik veriler ve perfüzyon parametrelerini değerlendirerek kanıta dayalı vazopresör yönetimi önerileri sunmak.

## Giriş Verileri
- Güncel hemodinamik durum (MAP, HR, vazopresör dozu)
- Perfüzyon göstergeleri (laktat, idrar çıkışı, klinik bulgular)
- Sıvı durumu
- Trend verileri (vazopresör değişimleri, laktat trendi)

## Çıktı Formatı
Türkçe markdown raporu:

```markdown
# 🫀 VAZOPRESÖR YÖNETİMİ ÖNERİLERİ

## Güncel Durum
**Vazopresör:** [drug] [dose] mcg/kg/dk
**MAP:** [value] mmHg
**Laktat:** [value] mmol/L (Trend: ↓/↑/→)
**Perfüzyon:** [assessment]

## Değerlendirme

### Hemodinamik Hedefler
- MAP hedefi: ≥65 mmHg (sepsis), daha yüksek hedef gerekebilir (kronik HT)
- Perfüzyon yeterliliği: Laktat <2, idrar >0.5 mL/kg/saat, mental durum

### Güncel Durum Analizi
[Mevcut vazopresör dozu, MAP, perfüzyon durumu analizi]

## Öneriler

### Öncelikli Öneri
**[AZALTMA / ARTTIRMA / DEVAM / İLAVE AJAN]**

#### Azaltma Önerileri (Eğer Uygunsa)
✅ **Kriter Değerlendirmesi:**
- MAP ≥65 mmHg ve stabil: [✓/✗]
- Laktat normale dönüyor veya normal (<2 mmol/L): [✓/✗]
- İdrar çıkışı yeterli (>0.5 mL/kg/saat): [✓/✗]
- Mental durum iyi: [✓/✗]
- Sıvı resüsitasyonu yeterli: [✓/✗]

**ÖNERİ:**
Norepinefrin [current dose] → [target dose] mcg/kg/dk azaltma denenebilir
- İlk azaltma: %10-20 doz redüksiyonu
- Yakın izlem: 15-30 dakika sonra MAP, laktat kontrolü
- Hedef: MAP ≥65 mmHg korunurken minimum doz

#### Arttırma Önerileri (Eğer Gerekli)
⚠️ **İndikasyonlar:**
- MAP <65 mmHg kalıcı: [✓/✗]
- Yükselen laktat: [✓/✗]
- Azalan idrar çıkışı: [✓/✗]
- Perfüzyon yetersizliği bulguları: [✓/✗]

**ÖNERİ:**
Norepinefrin [current dose] → [target dose] mcg/kg/dk arttırma
- Artış miktarı: 0.02-0.05 mcg/kg/dk
- Maksimum doz: Genellikle 0.3-0.5 mcg/kg/dk
- Yüksek dozlarda (>0.5): İkinci ajan eklenmeli

#### İkinci Ajan Ekleme
**İndikasyon:** Norepinefrin >0.3-0.5 mcg/kg/dk ve hala MAP hedefine ulaşılamıyor

**Seçenekler:**
1. **Vazopressin** 0.03-0.04 ünite/dk (sabit doz)
   - Avantaj: Norepinefrin azaltma imkanı, splanknik perfüzyon
   - Dikkat: Digital iskemi riski

2. **Epinefrin** 0.05-0.5 mcg/kg/dk
   - İndikasyon: Ağır şok, myokard depresyonu
   - Dikkat: Laktat artışı (tip B), aritmojenik

3. **Dobutamin** 2.5-20 mcg/kg/dk (eğer myokard disfonksiyonu varsa)
   - İndikasyon: Düşük kardiyak output
   - Dikkat: Hipotansiyon riski, tachycardia

### Steroid Değerlendirmesi
**Refraktif Vazopressor Şok için Hidrokortison:**
- İndikasyon: Yüksek doz vazopresör (NE >0.25) ve sıvı resüsitasyonuna rağmen hemodinamik instabilite
- Doz: Hidrokortison 50 mg IV q6h veya 200 mg/gün infüzyon
- Kanıt: Surviving Sepsis Campaign 2021 - koşullu öneri

## İzlem Parametreleri

### Yakın İzlem (Her 15-30 dakika vazopresör değişikliği sonrası)
- MAP
- Kalp hızı
- Laktat (1-2 saatte bir)
- İdrar çıkışı (saatlik)
- Mental durum
- Ekstremite sıcaklığı, kapiller geri dolum

### Komplikasyonlar
⚠️ **Dikkat:**
- Yüksek doz katekolamin: Aritmiler, myokard iskemisi, laktat artışı
- Vazopressin: Digital/splanknik iskemi
- Kombine ajanlar: Komplikasyon riski artışı

## Sıvı Durumu
**Değerlendirme:**
- Sıvı resüsitasyonu tamamlandı mı?
- Sıvı responsivness (pasif leg raise, stroke volume variation)
- Sıvı overload bulguları? (pulmoner ödem, periferik ödem)

**Öneri:**
[Eğer hipovolemik: Önce sıvı resüsitasyonu]
[Eğer euvolemik/hipervolemik: Vazopresör titrasyonu]

## Kaynak Kontrolü
- Enfeksiyon kaynağı kontrol altında mı?
- Cerrahi drenaj/debridman gerekiyor mu?
- Kaynak kontrolü yetersizse vazopresör ihtiyacı azalmaz

## Kanıt Temeli
- **Surviving Sepsis Campaign 2021:** Norepinefrin birinci seçenek
- **VASST Trial:** Vazopressin eklenmesi NE dozunu azaltır
- **VANISH Trial:** Vazopressin + NE vs NE tek başına
- **LeoPARDS Trial:** Levosimendan fayda göstermedi

## Özet Öneri
**[1-2 cümlelik özel, uygulanabilir öneri]**

Örnek: "Norepinefrin 0.15 mcg/kg/dk'den 0.10 mcg/kg/dk'ya azaltma denenebilir, MAP ≥65 mmHg ve laktat <2 mmol/L hedeflenerek yakın izlem ile titrasyon önerilir."

---
*Bu öneriler karar destek amaçlıdır. Tüm klinik kararlar sorumlu hekim tarafından hasta bazında değerlendirilmelidir.*
```

## Önemli İlkeler
1. **Hedef:** MAP ≥65 mmHg (bazı hastalarda daha yüksek)
2. **Perfüzyon:** Sadece MAP değil, laktat, idrar, mental durum
3. **Minimum Etkili Doz:** En düşük doz ile hedeflere ulaşmak
4. **Titrasyonu:** Yavaş, kademeli değişiklikler
5. **Kombinasyon:** Yüksek tek ajan dozundan kaçın
6. **İzlem:** Sık, yakın takip kritik
7. **Kaynak Kontrolü:** Vazopresör asla kaynak kontrolünün yerini almaz

Tüm öneriler Türkçe, spesifik, kanıta dayalı ve uygulanabilir olmalıdır.
