import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, InvalidElementStateException, StaleElementReferenceException, InvalidSelectorException

try:
    from logger_config import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Tarayıcı başlatılır
logger.info("Test başlıyor. Tarayıcı başlatılıyor...")
service = Service(executable_path='chromedriver.exe')
driver = webdriver.Chrome(service=service)
driver.maximize_window()
driver.implicitly_wait(5)

# Fiyatı formatlar
def clean_price(price_str):
    """Fiyat stringini temizleyip float değere çevirir. Türkçe/Uluslararası formatları destekler."""
    if not price_str:
        return 0.0
    
    price_str = price_str.strip().replace('TL', '').replace('\n', '').replace(' ', '').replace('$', '').replace('€', '')
    
    # Türkçe format (42.779,00) -> Uluslararası format (42779.00)
    if price_str.count(',') == 1 and price_str.count('.') >= 1 and price_str.index(',') > price_str.index('.'):
        price_str = price_str.replace('.', '').replace(',', '.')
    elif price_str.count(',') == 1 and price_str.count('.') == 0:
        price_str = price_str.replace(',', '.')
    
    price_str = price_str.replace('.', '')
    
    try:
        return float(price_str)
    except ValueError:
        logger.warning(f"Fiyat temizleme hatası: '{price_str}' float'a çevrilemedi.")
        return 0.0
    
try:
    logger.info("Cimri.com'a gidiliyor...")
    driver.get("https://www.cimri.com")
    
    try:
        cerez_locator = (By.XPATH, "//button[contains(text(), 'KABUL ET')] | //a[contains(text(), 'KABUL ET')] | //button[.//div[text()='KABUL ET']]")
        kabul_et_butonu = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(cerez_locator))
        kabul_et_butonu.click()
        logger.info("Çerezler kabul edildi.")
    except Exception:
        logger.info("Çerez penceresi bulunamadı veya zaten kabul edilmiş.")
    
    logger.info("Arama işlemi başlatılıyor...")
    sahte_arama_kutusu = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Neyi en ucuza almak istersin?']")))
    sahte_arama_kutusu.click()
    gercek_arama_kutusu = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='Neyi en ucuza almak istersin?']")))
    gercek_arama_kutusu.send_keys("macbook air m2")
    gercek_arama_kutusu.send_keys(Keys.ENTER)
    logger.info("Arama sonuçları sayfası başarıyla yüklendi!")

    logger.info("Arama sonuçlarındaki ilk ürün bulunuyor...")
    ilk_urun_karti_locator = (By.CSS_SELECTOR, "div#productListContainer a:first-child")
    ilk_urun_karti = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(ilk_urun_karti_locator))
    ilk_urun_karti.click()
    logger.info("İlk ürünün detay sayfasına gidildi.")
    
    logger.info("Ürün sayfasındaki tüm satıcı teklifleri toplanıyor...")
    fiyatlar_bolumu_locator = (By.ID, "fiyatlar")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located(fiyatlar_bolumu_locator))
    teklif_elementleri = driver.find_elements(By.CSS_SELECTOR, "div[data-offer]")
    teklif_listesi = []
    
    # Teklifler listelenir
    for teklif_element in teklif_elementleri:
        try:
            satici_adi = teklif_element.find_element(By.CSS_SELECTOR, "div.LUOwR img").get_attribute("alt")
            fiyat_str = teklif_element.find_element(By.CSS_SELECTOR, "div.rTdMX").text
            fiyat_numeric = clean_price(fiyat_str)
            tıklanacak_asıl_element = teklif_element.find_element(By.CSS_SELECTOR, "button[aria-label='teklif kartı linki']")
            teklif_listesi.append({"satici": satici_adi, "fiyat": fiyat_numeric, "element": tıklanacak_asıl_element})
        except Exception:
            logger.warning("Bir teklif kartı okunamadı, atlanıyor.")
    
    if not teklif_listesi:
        raise Exception("Hiçbir geçerli satıcı teklifi bulunamadı.")
    
    teklif_listesi.sort(key=lambda x: x["fiyat"])
    logger.info("Tüm teklifler fiyata göre sıralandı.")

    # Fiyatlar konsolda loglanır
    logger.info("--- SIRALANMIŞ SATICI VE FİYAT LİSTESİ (En Ucuzdan En Pahalıya) ---")
    for idx, teklif in enumerate(teklif_listesi):
        logger.info(f"{idx+1}. Satıcı: {teklif['satici']}, Fiyat: {teklif['fiyat']} TL")
    logger.info("------------------------------------------------------------------")
    
    # Sepete eklenir
    def sepet_islemi_denemesi(driver, deneme_adi="İlk Deneme"):
        """Stok kontrolü, 2 adet sepete ekleme ve sepet sayfasına gitme işlemlerini dener."""
        logger.info(f"Sepet İşlemi Denemesi: {deneme_adi} başlatılıyor.")
        
        # Stok kontrolü yapılır
        sayfa_kaynagi = driver.page_source.lower()
        stok_yok_ifadeleri = ["tükendi", "stokta yok", "geçici olarak temin edilemiyor", "out of stock"]
        stok_durumu = not any(ifade in sayfa_kaynagi for ifade in stok_yok_ifadeleri)
        
        if not stok_durumu:
            logger.warning("Ürün stokta değil. Sonraki satıcıya geçiliyor.")
            return False
            
        eklenecek_adet = 2
        logger.info(f"Ürün stokta mevcut. Sepete {eklenecek_adet} adet ekleme işlemi başlatılıyor.")
        
        # Ürün fiyatını alır
        urun_fiyati_str = None 
        try:
            urun_fiyati_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#corePriceDisplay_desktop_feature_div .a-price-whole, .priceToPay, #priceblock_ourprice")))
            urun_fiyati_str = urun_fiyati_element.text
        except:
            logger.warning("Ürün detay sayfasında birim fiyat elementi bulunamadı. Fiyat kontrolü sadece toplam üzerinden yapılacak.")
            
        try:
            # Adet alanı güncellenir (input olarak)
            logger.info("Ürün sayfasında adet alanını 2 olarak ayarlama deneniyor...")
            
            adet_alani_locator = (By.XPATH, "//select[contains(@id, 'quantity')] | //input[@type='number' and @min='1'] | //input[contains(@id, 'qty')]")

            try:
                adet_alani = WebDriverWait(driver, 3).until(EC.presence_of_element_located(adet_alani_locator))
                tag_name = adet_alani.tag_name
                
                if tag_name == 'select':
                    Select(adet_alani).select_by_value(str(eklenecek_adet))
                    logger.info(f"Ürün sayfasında adet (Select) başarıyla {eklenecek_adet} olarak ayarlandı.")
                elif tag_name == 'input':
                    driver.execute_script(f"arguments[0].value = '{eklenecek_adet}';", adet_alani)
                    adet_alani.send_keys(Keys.TAB)
                    logger.info(f"Ürün sayfasında adet (Input) JS ile {eklenecek_adet} olarak ayarlandı.")
                
                time.sleep(2)

            except TimeoutException:
                logger.warning("Ürün sayfasında adet (quantity) alanı bulunamadı. Varsayılan 1 adet kabul ediliyor.")
            
            # Sepete ekle butonunun tıklanması işlemi
            current_url = driver.current_url.lower()
            
            if "vatanbilgisayar" in current_url or "amazon" in current_url:
                locator = (By.ID, "add-to-cart-button")
            else:
                kapsayici_xpath = "//button[contains(translate(text(), 'SEPETEK', 'sepetek'), 'sepete ekle')] | //a[contains(translate(text(), 'SEPETEK', 'sepetek'), 'sepete ekle')]"
                locator = (By.XPATH, kapsayici_xpath)
                
            sepete_ekle_buton = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            
            # Güvenli tıklama gerçekleştirilir (Normal click -> JS click)
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", sepete_ekle_buton)
                time.sleep(1) 
                sepete_ekle_buton.click()
                logger.info("Standart tıklama ile 'Sepete Ekle' butonuna basıldı.")
            except (ElementClickInterceptedException, TimeoutException, InvalidElementStateException):
                logger.warning("Standart tıklama engellendi! JavaScript ile tıklama denenecek.")
                driver.execute_script("arguments[0].click();", sepete_ekle_buton)

            logger.info("'Sepete Ekle' işlemi başarıyla tetiklendi.")
            time.sleep(3)

            # Sepetten sonra çıkan kasko/ekleme diyaloglarını kapatma/geçme denemesi
            try:
                devam_et_xpath = "//*[contains(translate(text(), 'ETD', 'etd'), 'eklemeden devam et') or contains(translate(text(), 'HAYIRET', 'hayiret'), 'hayır teşekkürler')]"
                devam_et_butonu = driver.find_element(By.XPATH, devam_et_xpath)
                driver.execute_script("arguments[0].click();", devam_et_butonu)
                logger.info("Sepet sonrası çıkan diyalog geçildi.")
                time.sleep(2)
            except NoSuchElementException:
                pass 
            
            # Sepete gidilir
            try:
                sepete_git_xpath = "//*[contains(translate(text(), 'SEPETG', 'sepetg'), 'sepete git') or contains(translate(text(), 'SEPETG', 'sepetg'), 'sepeti görüntüle')]"
                sepete_git_buton = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, sepete_git_xpath)))
                sepete_git_buton.click()
            except TimeoutException:
                logger.info("'Sepete Git' butonu bulunamadı, sepet ikonuna tıklanacak.")
                sepet_ikonu = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='sepet'], a[href*='cart'], a[href*='basket']")))
                sepet_ikonu.click()

            WebDriverWait(driver, 15).until(EC.title_contains("Sepet") or EC.url_contains("cart"))
            logger.info("Sepet sayfasına başarıyla ulaşıldı! Sepet içi adet kontrolü yapılıyor.")
            
            # Sepet içi adet kontrolü yapılır
            sepet_adet_locator = (By.XPATH, 
                "//select[contains(@name, 'quantity') and contains(@class, 'a-native-dropdown')] | " + 
                "//div[contains(@class, 'counterWrapper')]/div/div[contains(@class, 'container')]/input[@type='text'] | //div[contains(@class, 'product_quantities')]/input[@type='number']"
            )
            
            try:
                sepet_adet_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located(sepet_adet_locator))
                tag_name = sepet_adet_element.tag_name
                
                # Mevcut adedi oku (Amazon'daki Fieldset'in içindeki span'i de oku)
                mevcut_adet = 1
                try:
                    mevcut_adet_span = driver.find_element(By.XPATH, "//fieldset[@name='sc-quantity']//span[@data-a-selector='value']")
                    mevcut_adet = int(mevcut_adet_span.text.strip())
                except:
                    try:
                        mevcut_adet = int(sepet_adet_element.get_attribute("value"))
                    except:
                        pass

                if mevcut_adet < eklenecek_adet:
                    logger.warning(f"Sepetteki mevcut adet ({mevcut_adet}) hedef ({eklenecek_adet}) adetten az. Güncelleme denemeleri yapılıyor.")
                    
                    input_success = False
                    
                    if tag_name == 'select':
                        Select(sepet_adet_element).select_by_value(str(eklenecek_adet))
                        logger.info(f"Adet (Select) başarıyla {eklenecek_adet} olarak ayarlandı.")
                        input_success = True
                        
                    elif tag_name == 'input':
                        # Input alanına yazarak güncelleme
                        try:
                            sepet_adet_input = WebDriverWait(driver, 3).until(EC.presence_of_element_located(sepet_adet_locator))
                            sepet_adet_input.clear()
                            sepet_adet_input.send_keys(str(eklenecek_adet))
                            sepet_adet_input.send_keys(Keys.ENTER) 
                            time.sleep(2)
                            
                            sepet_adet_input_guncel = WebDriverWait(driver, 3).until(EC.presence_of_element_located(sepet_adet_locator))
                            if int(sepet_adet_input_guncel.get_attribute("value")) == eklenecek_adet:
                                logger.info("Adet, input alanına yazılarak başarıyla güncellendi.")
                                input_success = True
                            
                        except Exception as e:
                            logger.warning(f"Input ile güncelleme başarısız oldu (Hata: {e.__class__.__name__}). '+' butonu deneniyor.")
                    
                    # Alternatif: Artı butonuna tıklayarak güncelleme
                    if not input_success:
                        
                        # Artırma butonu locator'ları
                        artirma_butonu_locator = (By.XPATH, 
                            "//a[@aria-label='Ürünü Arttır'] | //button[./i[@class='eptticon-plus']] | //button[@data-a-selector='increment']"
                        )
                        artirma_butonu = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(artirma_butonu_locator))
                        
                        mevcut_adet_guncel = 1
                        try:
                            mevcut_adet_span = driver.find_element(By.XPATH, "//fieldset[@name='sc-quantity']//span[@data-a-selector='value']")
                            mevcut_adet_guncel = int(mevcut_adet_span.text.strip())
                        except:
                            try:
                                mevcut_adet_guncel = int(driver.find_element(*sepet_adet_locator).get_attribute("value"))
                            except:
                                pass

                        gerekli_tiklama_sayisi = eklenecek_adet - mevcut_adet_guncel
                        
                        for _ in range(gerekli_tiklama_sayisi):
                            artirma_butonu.click()
                            time.sleep(2)

                        logger.info("Adet '+' butonu ile artırıldı.")
                    
                    # Adedin gerçekten değiştiğini doğrular
                    WebDriverWait(driver, 5).until(
                        lambda d: (d.find_element(*sepet_adet_locator).get_attribute("value") and int(d.find_element(*sepet_adet_locator).get_attribute("value")) == eklenecek_adet) or 
                                 (d.find_elements(By.XPATH, "//fieldset[@name='sc-quantity']//span[@data-a-selector='value']") and int(d.find_element(By.XPATH, "//fieldset[@name='sc-quantity']//span[@data-a-selector='value']").text) == eklenecek_adet)
                    )
                    time.sleep(3)
                    
                else:
                    logger.info(f"Sepetteki adet zaten {mevcut_adet}. Hedef karşılandı.")
                    
            except TimeoutException:
                logger.warning("Sepet içindeki adet giriş alanı/butonu bulunamadı.")
            except Exception as sepet_e:
                logger.error(f"Sepet içi adet kontrolünde kritik hata: {sepet_e}. Hata Türü: {sepet_e.__class__.__name__}", exc_info=True)

            # Fiyat doğrulama
            logger.info("Fiyat doğrulama adımına geçiliyor.")
                        
            # XPath locator'ları
            xpath_locators = [
                "//div[@class='totalAmount__c3LHr']/span[@class='amount__s7GOs']", # PttAVM Ödenecek Tutar
                "//*[contains(text(), 'Toplam') or contains(text(), 'Genel Toplam')]/following-sibling::*//span[contains(@class, 'price') or contains(@class, 'total')]"
            ]
            # CSS locator'ları
            css_locators = [
                "#sc-subtotal-amount-buybox", "#sc-subtotal-amount", "#sc-order-total .a-price-whole" # Amazon/Genel CSS
            ]
            
            toplam_fiyat_elementi = None
            
            # XPath'ler denenir
            for xpath in xpath_locators:
                try:
                    toplam_fiyat_elementi = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, xpath)))
                    logger.info(f"Toplam fiyat elementi XPath ile bulundu: {xpath}")
                    break
                except TimeoutException:
                    continue
            
            # Bulunamazsa, CSS Selector'lar denenir
            if toplam_fiyat_elementi is None:
                for css in css_locators:
                    try:
                        toplam_fiyat_elementi = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
                        logger.info(f"Toplam fiyat elementi CSS ile bulundu: {css}")
                        break
                    except TimeoutException:
                        continue
            
            # Fiyat Doğrulanır
            try:
                if toplam_fiyat_elementi is None:
                    raise TimeoutException("Toplam fiyat elementi bulunamadı.")
                
                toplam_fiyat_gercek = clean_price(toplam_fiyat_elementi.text)

                # Birim fiyatı hesaplamak için ürün fiyatı toplamı bulunur
                try:
                    urun_toplami_locator_pttavm = (By.XPATH, "//span[text()='Ürün Fiyatı Toplamı']/following-sibling::span[@class='amount__s7GOs']")
                    urun_toplami_elementi = driver.find_element(*urun_toplami_locator_pttavm)
                    urun_toplami_gercek = clean_price(urun_toplami_elementi.text)
                    
                    indirim_elementi = driver.find_element(By.XPATH, "//span[text()='İndirim Tutarı']/following-sibling::span[@class='amount__s7GOs discount__gd7ma']")
                    indirim_tutari = clean_price(indirim_elementi.text)
                    
                    toplam_fiyat_hesaplanan = urun_toplami_gercek - indirim_tutari
                    
                except NoSuchElementException:
                    if urun_fiyati_str:
                        urun_fiyati_numeric = clean_price(urun_fiyati_str)
                        toplam_fiyat_hesaplanan = urun_fiyati_numeric * eklenecek_adet
                    else:
                        raise Exception("Fiyat doğrulama için gerekli birim veya ürün toplam fiyatı bulunamadı.")
                    
                
                # Doğrulama son aşama
                if abs(toplam_fiyat_hesaplanan - toplam_fiyat_gercek) < 1.0:
                    logger.info(f"Sepet Kontrolü BAŞARILI: Ödenecek Tutar ({toplam_fiyat_gercek:.2f} TL) doğru hesaplandı.")
                else:
                    logger.error(f"Sepet Kontrolü HATA: Hesaplanan Toplam Fiyat ({toplam_fiyat_hesaplanan:.2f}) Gerçek Fiyat ({toplam_fiyat_gercek:.2f}) ile uyuşmuyor.")
                    
            except Exception as fiyat_e:
                logger.error(f"Sepet Kontrolü HATA: Fiyat doğrulama sırasında beklenmeyen hata oluştu. Hata Türü: {fiyat_e.__class__.__name__}", exc_info=True)
            
            return True

        except Exception as e:
            logger.error(f"'{driver.title}' sitesinde sepete ekleme adımlarında kritik hata oluştu. Hata Türü: {e.__class__.__name__}", exc_info=True)
            return False 
    
    for i, teklif in enumerate(teklif_listesi):
        if i > 1:
            logger.warning("İlk iki en ucuz satıcıda da stok bulunamadı veya bir hata oluştu. Test sonlandırılıyor.")
            break

        logger.info(f"Deneme {i+1}: En ucuz {i+1}. satıcıya gidiliyor -> Satıcı: {teklif['satici']}, Fiyat: {teklif['fiyat']}")
        
        cimri_penceresi = driver.current_window_handle
        driver.execute_script("arguments[0].click();", teklif['element'])
        time.sleep(5) 

        all_pencere_handles = driver.window_handles
        if len(all_pencere_handles) < 2:
            logger.warning(f"Satıcı sitesine geçilemedi, sekme açılmadı: {teklif['satici']}. Bir sonraki denenecek.")
            continue
            
        yeni_pencere = [handle for handle in all_pencere_handles if handle != cimri_penceresi][0]
        driver.switch_to.window(yeni_pencere)
        logger.info(f"Satıcı sitesine geçiş yapıldı: {driver.title}")

        if sepet_islemi_denemesi(driver, "İlk Deneme"):
            sepet_islemi_basarili = True
            break 
        
        else:
            logger.info("Sepete ekleme ilk denemede başarısız oldu. Giriş yapmayı denenecek...")
            
            try:
                giris_xpath = "//*[contains(translate(text(), 'GIRIŞY', 'girişy'), 'giriş yap') or contains(translate(text(), 'ÜYEOL', 'üyeol'), 'üye ol')]"
                giris_butonlari = driver.find_elements(By.XPATH, giris_xpath)
                
                if giris_butonlari:
                    driver.execute_script("arguments[0].click();", giris_butonlari[0])
                    logger.info("'Giriş Yap' butonuna tıklandı.")
                    
                    time.sleep(5) 
                    logger.info("Giriş yapma işlemi (varsayımsal) tamamlandı. Ürün sayfası yeniden yükleniyor...")
                    driver.get(driver.current_url) 
                    time.sleep(3)
                    
                    if sepet_islemi_denemesi(driver, "Giriş Sonrası İkinci Deneme"):
                        sepet_islemi_basarili = True
                        break 
                    else:
                        logger.warning("Giriş yapılmasına rağmen sepete ekleme başarısız oldu.")
                    
                else:
                    logger.warning("Giriş yapma butonu bulunamadı veya login adımı atlanıyor.")
            
            except Exception as login_e:
                logger.error(f"Giriş yapma denemesi sırasında kritik bir hata oluştu. Hata Türü: {login_e.__class__.__name__}", exc_info=True)
            
            finally:
                driver.close()
                driver.switch_to.window(cimri_penceresi)
                logger.info("Cimri.com'a geri dönüldü, bir sonraki en ucuz satıcı denenecek.")
                continue

    if not sepet_islemi_basarili:
        logger.error("Stokta ürün bulunan ve sepete 2 adet ekleme yapılabilen bir satıcı bulunamadı.")

except Exception as e:
    logger.error(f"ANA İŞLEM SIRASINDA KRİTİK BİR HATA OLUŞTU! Hata Türü: {e.__class__.__name__}", exc_info=True)

finally:
    logger.info("Test 10 saniye sonra sonlanacak.")
    time.sleep(10)
    logger.info("Test tamamlandı, tarayıcı kapatılıyor.")
    driver.quit()