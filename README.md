# SVFOTOCOMP — ilk API sunucusu

Bu paket, SVFOTOCOMP için başlangıç API'sidir. Video yükler, oyuncu adı/forma numarasını alır ve FFmpeg/FFprobe varlığını kontrol eder.

## Bilgisayarda çalıştırma

Python 3.11+ ve FFmpeg kurulu olmalı.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Tarayıcıdan `http://localhost:8000/health` ve `http://localhost:8000/docs` adreslerini aç.

## Docker ile çalıştırma

Docker kuruluysa:

```bash
docker compose up --build
```

## Video yükleme

`POST /api/upload` multipart form alanları:
- `video`: mp4, mov, mkv, avi veya webm
- `player_name`: oyuncu adı
- `shirt_number`: forma numarası

Örnek:

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "video=@match.mp4" \
  -F "player_name=Test Oyuncu" \
  -F "shirt_number=10"
```

## Önemli sınırlar

- 16 GB uygulama sınırı tanımlıdır; gerçek yükleme sınırı barındırma sağlayıcısının proxy, disk ve istek limitlerine de bağlıdır.
- Bu bir geliştirme başlangıcıdır. Kimlik doğrulama, kullanıcı bazlı kota, güvenli dosya saklama, otomatik temizleme ve üretim CORS ayarları eklenmeden internete açık bırakma.
- Otomatik oyuncu tanıma/forma numarası OCR ve MP4 highlight üretimi henüz eklenmedi. Bu paket yalnızca yükleme ve temel medya kontrolünü sağlar.
- Yüklenen dosyalar `uploads/` klasöründe saklanır. Gerçek kullanımda kalıcı ve erişim kontrollü depolama gerekir.
