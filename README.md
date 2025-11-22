**E-Ticaret Sepeti Otomasyon Testi (Cimri.com Entegrasyonu)**
Bu proje, belirlenen bir ürünün Cimri.com üzerinden en uygun fiyatlı satıcıları bulunmasını, stok kontrolünü, fiyat karşılaştırmasını ve ürünü sepete ekleme sürecini otomatikleştiren kapsamlı bir Selenium Python test senaryosunu içerir.

**1. Proje Amacı ve Kapsam**
Projenin temel amacı, e-ticaret sitelerinin farklı dinamik yapılarına (adet giriş mekanizmaları, sepet özeti formatları, giriş zorunlulukları) karşı test senaryosunun dayanıklılığını ve hata yönetimini ölçmektir.

**Kapsam:**
- Cimri.com'da ürün arama.
- En ucuz ilk iki satıcının belirlenmesi.
- Satıcı sitesine geçiş ve stok kontrolü.
- Stokta varsa 2 adet ürünü sepete ekleme denemesi (Giriş zorunluluğu varsa, giriş yapıldıktan sonra tekrar deneme mantığı içerir).
- Sepet sayfasında adet kontrolü ve düzenlemesi (Farklı sitelerin input, select veya artı butonu yapılarına uyumlu).
- Sepet özetindeki ödenecek tutarın doğruluk kontrolü.

**2. Teknolojiler**
* Dil: Python
* Otomasyon Kütüphanesi: Selenium WebDriver
* Web Tarayıcısı: Google Chrome (veya chromedriver.exe ile uyumlu diğer tarayıcılar)
* Bağımlılık Yönetimi: pip
* Loglama: Python logging modülü (Ayrı dosyaya ve konsola çıktı)

**3. Kurulum ve Çalıştırma**
***3.1. Ön Gereksinimler***
* Python 3.x: Sisteminizde Python kurulu olmalıdır.
* Chrome Tarayıcı: Google Chrome yüklü olmalıdır.
* ChromeDriver: Kullanılan Chrome sürümüne uygun chromedriver.exe dosyası projenin ana dizinine yerleştirilmelidir.

***3.2. Bağımlılıkların Kurulumu***
Proje klasöründe aşağıdaki komutu çalıştırarak gerekli Python kütüphanelerini yükleyin:
pip install selenium

***3.3. Proje Yapısı***
test_senaryosu.py: Ana test mantığını ve otomasyon adımlarını içerir.
otomasyon.log: Tüm test sonuçlarının, hata izlerinin ve fiyat listelerinin kaydedildiği log dosyası.
logger_config.py: Loglama ayarlarının bulunduğu dosya.
chromedriver.exe: Tarayıcıyı kontrol etmek için gerekli olan WebDriver yürütülebilir dosyası.

***3.4. Testin Başlatılması***
Testi başlatmak için proje dizininde aşağıdaki komutu çalıştırın:
python test_senaryosu.py

**4. Hata Yönetimi ve Loglama**
Proje, detaylı hata yönetimi ve loglama prensiplerini benimser:

- Tüm işlemler otomasyon.log dosyasına kaydedilir.
- Loglar, zaman damgası, hata seviyesi (INFO, WARNING, ERROR) ve detaylı Traceback bilgisini içerir.
- Log dosyası, her çalıştırmada önceki sonuçların üzerine yazılmaz, yeni çıktıları sona ekler.

**5. Sepet Fiyat Doğrulaması**
Senaryo, sepete ekleme başarılı olduktan sonra sepet sayfasına geçer ve ödenecek tutarın (indirimler ve ürün fiyatı toplamı dikkate alınarak) doğru hesaplanıp hesaplanmadığını kontrol eder ve sonucu loglar.
