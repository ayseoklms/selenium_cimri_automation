# E-Ticaret Sepeti Otomasyon Testi

### **(Cimri.com Entegrasyonu -- Selenium Python Test Projesi)**

Bu proje, belirlenen bir ürünün **Cimri.com üzerinden en uygun fiyatlı
satıcılarının tespitini**, **stok kontrolünü**, **fiyat
karşılaştırmasını** ve **sepete ekleme sürecini** uçtan uca
otomatikleştiren kapsamlı bir Selenium test senaryosudur.

##  1. Proje Amacı ve Kapsam

Bu projenin ana amacı, farklı e-ticaret sitelerinin dinamik yapılarına
karşı dayanıklı, yeniden çalışabilir ve hataya açık olmayan bir
otomasyon testi oluşturmaktır.

### **Kapsam:**

-   Cimri.com'da ürün arama\
-   En ucuz ilk iki satıcının belirlenmesi\
-   Satıcı sitesine yönlendirme ve stok kontrolü\
-   Stok varsa üründen **2 adet** sepete ekleme denemesi
    -   Eğer giriş zorunluluğu varsa, otomatik olarak giriş yapılıp
        işlem tekrar denenir\
-   Sepet sayfasında adet kontrolü ve düzenlemesi
    -   Farklı sitelerin:
        -   `input`,\
        -   `select`,\
        -   `+ / -` buton yapıları desteklenir\
-   Sepet özetinden toplam ödenecek tutarın doğrulanması

##  2. Kullanılan Teknolojiler

  Teknoloji / Araç            Açıklama
  --------------------------- -----------------------------
  **Python**                  Test dili
  **Selenium WebDriver**      Otomasyon çatısı
  **Chrome / ChromeDriver**   Test tarayıcısı ve sürücüsü
  **pip**                     Bağımlılık yönetimi
  **Python logging**          Loglama sistemi

##  3. Kurulum ve Çalıştırma

###  3.1. Ön Gereksinimler

-   Python **3.x**
-   Google Chrome tarayıcısı
-   Chrome sürümüne uygun **chromedriver.exe**
    -   Dosya proje ana dizininde olmalıdır

###  3.2. Bağımlılıkların Kurulumu

``` bash
pip install selenium
```

### 3.3. Proje Yapısı

 test_senaryosu.py        # Ana test akışı
 logger_config.py         # Log ayarları
 otomasyon.log            # Log kayıtları
 chromedriver.exe         # WebDriver dosyası

###  3.4. Testin Çalıştırılması

``` bash
python test_senaryosu.py
```

## 4. Hata Yönetimi ve Loglama

-   Tüm işlemler **otomasyon.log** dosyasına yazılır\
-   Log formatı:
    -   Zaman damgası\
    -   Log seviyesi (INFO, WARNING, ERROR)\
    -   Hata Traceback bilgisi\
-   Log dosyası **üzerine yazılmaz**, her çalıştırmada yeni satırlar
    eklenir

##  5. Sepet Fiyat Doğrulaması

Senaryonun sonunda:

-   Sepete eklenen ürünlerin toplam fiyatı\
-   İndirimler\
-   Sipariş özeti

otomatik olarak kontrol edilir ve doğrulama sonucu loglara yazılır.
