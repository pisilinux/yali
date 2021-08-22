## Hatalar
- [ ] Disk boşluklu dosya adı ile bağlı ise ayıramıyor... (kod: 1)

## Yapılacaklar

- [ ] Diğer diller güncellenmeli
- [ ] kurulumdan sonra grub güncellenmeli (update-grub)
- [ ] yalıda uefi desteklense bile istenirse efisiz kurulum yapılbilmeli
- [ ] boot sıralamasında doğrudan ilk sıralamaya yerleştirilmemeli (cdrom vs)
- [x] kurulum yapılacak disk bölümü/bölümleri ayrılmalı (geçici olarak bir çözüm eklendi)
- [x] EFI sistemde otomatik bölümlendirme ayarlanmalı
- [x] 'display manager' ler ayarları için fonksiyonlar yazılmalı
  - [x] sddm ayarları
  - [x] lxdm ayarları
  - [ ] diğer (yeni dm eklendiğinde ayareklenecek!)
- [x] pencere boyutları minimal ve canlı kalıplar için ayrı ayrı ayarlanmalı
- [x] diyalog pencere başlıkları ayarlanmalı (canlı iso için harici başlık olmasın kurulum isosu için harici başlık olsun)
- [x] pisiman mkinitramfs için ayarlandığından mkinitramfs için bazı iyileştirmeler yapıldı
- [x] mkinitramfs ye geçerek lvm2 desteği tekrar sağlandı


## Yapılanlar


- [x] canlı iso paketleri ile kurulum paketleri ayrı olacak şekilde ayarlandı
- [x] efi bölümüme dosyaların yüklenmesi için ekleme
- [x] initramfs yerine mkinitcpio kullanıldı
- [x] canlı kurulum için diyalog başlık çubuğunu kaldır
- [x] ekran güncellemeleri ayarlandı (yerelleştire, ülke seçimi ...)
- [x] paket kurulumu yerine sqfs kurulumu ayarlandı (kurulum sonunda yalı kaldırılmalı)
