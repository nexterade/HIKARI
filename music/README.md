# Local Music Set

Mini player Genesis sengaja memakai HTML5 `<audio>` native agar dapat bekerja dari `file://` tanpa iframe/provider embed.

## Playlist default

Masukkan file audio yang memang kamu miliki/berhak gunakan dengan nama berikut:

1. `01-seraut-wajah.mp3`
2. `02-sketsa-rembulan-emas.mp3`
3. `03-menjaring-matahari.mp3`
4. `04-orang-orang-terkucil.mp3`
5. `05-nyanyian-kasmaran.mp3`
6. `06-bingkai-mimpi.mp3`
7. `07-untuk-kita-renungkan.mp3`
8. `08-senandung-pucuk-pucuk-pinus.mp3`
9. `09-titip-rindu-buat-ayah.mp3`
10. `10-elegi-esok-pagi.mp3`
11. `11-berita-kepada-kawan.mp3`
12. `12-lagu-untuk-sebuah-nama.mp3`
13. `13-kalian-dengarkan-keluhanku.mp3`
14. `14-seberkas-cinta-yang-sirna.mp3`
15. `15-yang-telah-selesai.mp3`
16. `16-masih-ada-waktu.mp3`
17. `17-cinta-sebening-embun.mp3`
18. `18-cintaku-kandas-di-rerumputan.mp3`
19. `19-untukmu-kekasih.mp3`
20. `20-dia-lelaki-ilham-dari-surga.mp3`

Browser tidak boleh membaca folder lokal secara arbitrer. Karena itu mini player menyediakan tombol `FILES` untuk memilih file audio dari perangkat; setelah dipilih, file dimainkan melalui object URL lokal dan tidak di-upload oleh halaman ini.


## Directory-first library
Genesis treats `/storage/emulated/0/Music` as the suggested Android music location. A browser opened from `file://` cannot be assumed to have arbitrary filesystem access, so the UI offers two browser-safe paths: a directory picker (`showDirectoryPicker` when available, with recursive scanning) and a `webkitdirectory` folder-selection fallback. Manual `FILES` selection remains available.

Future native Android integration may map the same library contract to Android Storage Access Framework (SAF) or a native wrapper for true automatic scanning.
