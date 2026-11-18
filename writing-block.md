# Spesifikasi Proyek: Functional Programming Library (`fplib.py`) & 5 Aplikasi Terapan (`app1.py` – `app5.py`)

## 1. Tujuan dan Ruang Lingkup Proyek

Membangun satu modul library inti (`fplib.py`) berbasis paradigma **Functional Programming** menggunakan bahasa Python, mengacu pada kurikulum Modul 1–4 Pemrograman Fungsional UMM.

Proyek ini juga mencakup **5 aplikasi independen** (`app1.py` hingga `app5.py`) yang mengimpor dan memanfaatkan fungsi-fungsi dari `fplib.py` untuk menyelesaikan berbagai studi kasus nyata.

Setiap aplikasi harus menunjukkan penerapan konsep Functional Programming secara nyata, bukan sekadar menggunakan fungsi library tanpa konteks penerapan.

## 2. Aturan Arsitektur dan Batasan Teknis

Seluruh aturan berikut WAJIB dipatuhi oleh AI Agent selama proses implementasi.

### 2.1 Pure Functions dan Effect-Free Core

- Seluruh fungsi komputasi di dalam `fplib.py` dan fungsi logika inti di `app1.py`–`app5.py` wajib bersifat *pure*.
- Fungsi harus deterministik: input yang sama menghasilkan output yang sama.
- Dilarang menggunakan `print()`, `input()`, mutasi variabel global, maupun operasi I/O di dalam fungsi komputasi.
- Seluruh proses I/O, seperti `print()`, parsing CLI, dan pencetakan laporan, harus diisolasi pada blok:

  ```python
  if __name__ == "__main__":
  ```

### 2.2 Strict Immutability

- Dilarang melakukan mutasi *in-place*, seperti:
  - `.append()`
  - `.pop()`
  - `.sort()`
  - `dict[key] = value` langsung pada parameter input.
- Gunakan `copy.deepcopy()` untuk menangani data bersarang (*nested data*).
- Gunakan konstruksi koleksi baru, seperti:
  - `sorted()`
  - List comprehension
  - Dictionary comprehension
  - Dictionary unpacking (`{**old, **new}`)

Seluruh fungsi transformasi harus menghasilkan objek baru tanpa mengubah data asli yang diterima.

### 2.3 No Imperative Loops pada Operasi Rekursif

Khusus fungsi rekursif di `fplib.py` dan logika agregasi rekursif pada aplikasi:

- Dilarang menggunakan `for`.
- Dilarang menggunakan `while`.
- Dilarang menggunakan `len()` bawaan Python.
- Dilarang menggunakan `sum()` bawaan Python.
- Wajib menggunakan pendekatan dekomposisi *head and tail*.
- Wajib menerapkan pola `try-except-else` pada fungsi rekursif yang memerlukan penanganan kondisi akhir.

### 2.4 Declarative Programming dan Dokumentasi

Setiap fungsi di `fplib.py` wajib memiliki *docstring* dengan format:

```python
"""
desc:
    Penjelasan fungsi.

pre-cond:
    Kondisi yang harus dipenuhi sebelum fungsi dijalankan.

post-cond:
    Kondisi yang dijamin setelah fungsi dijalankan.
"""
```

### 2.5 Zero External Dependencies

- Hanya diperbolehkan menggunakan Python Standard Library.
- Tidak diperbolehkan menggunakan library eksternal yang membutuhkan instalasi melalui `pip`.
- Contoh library yang diperbolehkan:
  - `copy`
  - `time`
  - `functools`
  - `json`
  - `statistics`
  - `operator`
  - `itertools`

Proyek harus dapat dijalankan langsung pada lingkungan Fedora Linux menggunakan Python 3.

## 3. Struktur Direktori Target

Buat struktur direktori proyek sebagai berikut:

```text
functional-programming-project/
├── fplib.py          # Core Functional Programming Library (Modul 1–4)
├── app1.py           # E-Commerce Dynamic Pricing & Order Pipeline
├── app2.py           # IoT Telemetry & Sensor Anomaly Stream Analyzer
├── app3.py           # Academic Gradebook & Scholarship Eligibility Evaluator
├── app4.py           # Server Log Audit & Security Incident Filter
├── app5.py           # Nested Inventory & Warehouse Valuation Engine
└── README.md         # Dokumentasi arsitektur dan pemetaan konsep Modul 1–4
```

## 4. Spesifikasi Lengkap Library Inti (`fplib.py`)

AI Agent wajib mengimplementasikan seluruh komponen berikut.

### A. Modul 4 — Decorators (`@`)

#### 1. `measure_time(func)`

- Mengukur waktu eksekusi fungsi.
- Menggunakan `functools.wraps`.
- Menggunakan `time.perf_counter()`.
- Mengembalikan tuple:

  ```python
  (hasil_fungsi, durasi_ms)
  ```

- Durasi harus dinyatakan dalam milidetik.

#### 2. `enforce_immutability(func)`

- Melakukan `copy.deepcopy()` terhadap seluruh `*args` dan `**kwargs` sebelum diteruskan ke fungsi.
- Memastikan fungsi yang dibungkus tidak dapat mengubah objek asli milik pemanggil melalui argumen yang diterimanya.
- Menggunakan `functools.wraps`.

#### 3. `validate_non_empty(func)`

- Memeriksa apakah argumen pertama kosong.
- Jika kosong, bangkitkan `ValueError` dengan pesan informatif.
- Menggunakan `functools.wraps`.

### B. Modul 1 dan 3 — Pure Recursion & Exception Handling

#### 1. `recursive_length(seq, index=0)`

- Menghitung panjang sequence secara rekursif.
- Tidak boleh menggunakan `len()` maupun perulangan.
- Menggunakan `try-except IndexError-else`.

#### 2. `recursive_sum(numbers)`

- Menjumlahkan seluruh elemen numerik pada *flat sequence*.
- Menggunakan pola:

  ```python
  numbers[0] + recursive_sum(numbers[1:])
  ```

- Tidak boleh menggunakan `sum()` bawaan Python.

#### 3. `recursive_sum_field(records, field_name)`

- Menjumlahkan seluruh nilai dari `field_name` pada struktur `list[dict]`.
- Menggunakan pendekatan rekursif.
- Tidak boleh menggunakan perulangan maupun `sum()` bawaan Python.

#### 4. `recursive_flatten(nested_list)`

- Meratakan struktur *nested list* dengan kedalaman bebas menjadi *flat list* satu dimensi.
- Menggunakan rekursi.
- Tidak boleh menggunakan `for`, `while`, maupun fungsi flatten eksternal.

#### 5. `safe_execute(func, *args, fallback=None, **kwargs)`

- Menjalankan fungsi di dalam blok `try-except-else`.
- Mengembalikan dictionary dengan format:

  ```python
  {
      "ok": bool,
      "data": Any,
      "error": str | None
  }
  ```

- Jika berhasil, `ok` bernilai `True`, `data` berisi hasil fungsi, dan `error` bernilai `None`.
- Jika gagal, `ok` bernilai `False`, `data` berisi nilai `fallback`, dan `error` berisi pesan kesalahan.

### C. Modul 2 — Immutability & Lazy Evaluation (`yield`)

#### 1. `immutable_update_record(record, updates)`

- Menghasilkan dictionary baru berdasarkan penggabungan `record` dan `updates`.
- Menggunakan `copy.deepcopy()`.
- Tidak boleh mengubah dictionary asli.
- Mendukung data bersarang.

#### 2. `lazy_filter_stream(iterable, predicate)`

- Merupakan *generator function* menggunakan `yield`.
- Menyaring item satu per satu secara *lazy*.
- Hanya menghasilkan item yang memenuhi `predicate`.
- Menghasilkan `copy.deepcopy(item)` agar konsumen generator tidak memperoleh referensi langsung ke objek sumber.

#### 3. `lazy_transform_stream(iterable, transformer)`

- Merupakan *generator function* menggunakan `yield`.
- Mentransformasi item satu per satu secara *lazy*.
- Tidak boleh mengubah item asli.
- Hasil transformasi harus mengikuti kontrak immutability.

### D. Modul 3 dan 4 — Currying, Closures, Lambda & Declarative Pipeline

#### 1. `curry_filter_by(key)(comparator)(threshold)`

- Merupakan *Curried Higher-Order Function*.
- Menghasilkan *closure* berupa fungsi predikat:

  ```python
  predicate(record) -> bool
  ```

- Digunakan untuk menyaring dictionary berdasarkan field, operator pembanding, dan nilai ambang.

#### 2. `curry_transform_field(source_key)(target_key)(calc_fn)`

- Merupakan *Curried Higher-Order Function*.
- Menghasilkan *closure* mapper.
- Mengambil nilai dari `source_key`.
- Mengolah nilai menggunakan `calc_fn`.
- Menambahkan hasil ke `target_key`.
- Menghasilkan dictionary baru menggunakan pendekatan *deep-copy*.

#### 3. `curry_rate_adjuster(rate_percent)`

- Menghasilkan fungsi kalkulasi penyesuaian persentase.
- Rumus:

  ```python
  base_amount * (1 + rate_percent / 100)
  ```

- Mendukung diskon maupun kenaikan harga.

#### 4. `COMPARATORS`

Dictionary *First-Class Functions* yang berisi lambda untuk:

| Key | Operasi |
|---|---|
| `eq` | Sama dengan (`==`) |
| `neq` | Tidak sama dengan (`!=`) |
| `gt` | Lebih besar (`>`) |
| `gte` | Lebih besar atau sama dengan (`>=`) |
| `lt` | Lebih kecil (`<`) |
| `lte` | Lebih kecil atau sama dengan (`<=`) |
| `contains` | Memeriksa keberadaan elemen atau substring |

#### 5. `add_values`

Ekspresi lambda untuk agregasi:

```python
add_values = lambda acc, val: acc + val
```

Digunakan bersama `functools.reduce()`.

#### 6. `run_pipeline(dataset, *steps)`

- Dibungkus menggunakan `@enforce_immutability`.
- Mengomposisikan fungsi satu argumen dari kiri ke kanan.
- Menggunakan `functools.reduce()`.
- Setiap langkah menerima output dari langkah sebelumnya.

#### 7. Pipeline Adapters

Implementasikan tiga adapter berikut:

- `make_filter_step(predicate)`
  - Membungkus operasi `filter()`.

- `make_map_step(transformer)`
  - Membungkus operasi `map()`.

- `make_reduce_step(reducer_fn, initializer=None)`
  - Membungkus operasi `reduce()`.

Ketiganya harus dapat dirangkai di dalam `run_pipeline()`.

## 5. Spesifikasi Lima Aplikasi Terapan

Setiap aplikasi wajib memenuhi ketentuan berikut:

1. Mengimpor dan menggunakan `fplib.py`.
2. Memiliki dataset dummy internal yang realistis.
3. Menggunakan minimal 6–10 record untuk setiap dataset utama.
4. Memiliki data bersarang (*nested data*) apabila relevan dengan studi kasus.
5. Melakukan pembuktian immutability menggunakan `assert`.
6. Menampilkan output terstruktur dan informatif di terminal.
7. Mengisolasi seluruh I/O di dalam blok `if __name__ == "__main__":`.
8. Menunjukkan penerapan konsep Functional Programming secara nyata.

### Aplikasi 1 — `app1.py`

**E-Commerce Dynamic Pricing & Order Pipeline**

**Domain:** Pemrosesan transaksi pesanan toko elektronik.

Alur implementasi:

1. Menyaring pesanan berstatus `"paid"` menggunakan:

   ```python
   curry_filter_by("status")(COMPARATORS["eq"])("paid")
   ```

2. Menyaring pesanan berdasarkan subtotal minimal menggunakan comparator `gte`.

3. Menghitung harga setelah diskon member sebesar 10% menggunakan:

   ```python
   curry_rate_adjuster(-10)
   ```

4. Menambahkan PPN sebesar 11% menggunakan:

   ```python
   curry_rate_adjuster(11)
   ```

5. Menggunakan `curry_transform_field()` untuk menambahkan field harga hasil perhitungan tanpa mengubah record asli.

6. Merangkai seluruh proses menggunakan `run_pipeline()`.

7. Membungkus eksekusi pipeline menggunakan `@measure_time`.

8. Menghitung total omzet bersih secara rekursif menggunakan `recursive_sum_field()`.

9. Menghitung jumlah transaksi valid menggunakan `recursive_length()`.

**Output yang diharapkan:**

- Jumlah seluruh pesanan.
- Jumlah pesanan berstatus paid.
- Jumlah transaksi yang memenuhi batas subtotal.
- Rincian harga sebelum dan sesudah diskon.
- Rincian PPN.
- Total omzet bersih.
- Durasi eksekusi pipeline.

### Aplikasi 2 — `app2.py`

**IoT Telemetry & Sensor Anomaly Stream Analyzer**

**Domain:** Analisis aliran data sensor mikrokontroler, meliputi suhu, intensitas cahaya LDR, dan getaran atau akselerasi.

Alur implementasi:

1. Memproses stream pembacaan sensor mentah menggunakan `lazy_filter_stream()` untuk menyaring pembacaan di atas ambang batas anomali.

2. Menggunakan `lazy_transform_stream()` untuk menambahkan klasifikasi tingkat bahaya secara immutable.

3. Menggunakan *Generator Expression* untuk mengekstrak nilai numerik sebelum dikonsumsi.

4. Mengambil N anomali pertama tanpa harus memproses seluruh stream.

5. Menguji ketahanan terhadap data sensor korup atau hilang menggunakan `safe_execute()`.

**Output yang diharapkan:**

- Data sensor mentah.
- Data sensor yang terindikasi anomali.
- Klasifikasi tingkat bahaya.
- N data anomali pertama.
- Hasil pengujian penanganan data korup.
- Bukti bahwa dataset asli tidak berubah.

### Aplikasi 3 — `app3.py`

**Academic Gradebook & Scholarship Eligibility Evaluator**

**Domain:** Evaluasi nilai akademik mahasiswa dan seleksi kelayakan beasiswa.

Alur implementasi:

1. Menyimpan daftar bobot atau rumus konversi nilai sebagai *First-Class Functions* dalam struktur data.

2. Menggunakan `run_pipeline()` dan `make_map_step()` untuk menghitung IPK atau skor akhir setiap mahasiswa secara immutable.

3. Menggunakan `curry_filter_by()` untuk menyaring kandidat dengan:
   - IPK minimal 3.50.
   - Status mahasiswa aktif.

4. Menghitung rata-rata skor kandidat yang lolos menggunakan:

   ```python
   recursive_sum_field()
   ```

   Dibagi dengan:

   ```python
   recursive_length()
   ```

5. Memvalidasi dataset kosong menggunakan `@validate_non_empty`.

**Output yang diharapkan:**

- Daftar mahasiswa dan nilai akademik.
- Hasil perhitungan IPK.
- Daftar kandidat yang memenuhi syarat beasiswa.
- Jumlah kandidat yang lolos.
- Rata-rata IPK kandidat.
- Hasil validasi dataset kosong.

### Aplikasi 4 — `app4.py`

**Server Log Audit & Security Incident Filter**

**Domain:** Audit log HTTP server berdasarkan status code, endpoint, IP address, dan latensi dalam milidetik.

Alur implementasi:

1. Menyaring insiden error menggunakan kondisi:

   ```python
   status_code >= 400
   ```

2. Menyaring endpoint sensitif menggunakan:

   ```python
   COMPARATORS["contains"]
   ```

3. Menggunakan komposisi *Curried Predicates* untuk membangun filter insiden.

4. Melakukan masking atau anonimisasi sebagian oktet IP address secara immutable menggunakan:

   ```python
   immutable_update_record()
   ```

5. Menghitung total waktu latensi insiden menggunakan:

   ```python
   make_reduce_step(add_values, 0)
   ```

   di dalam `run_pipeline()`.

**Output yang diharapkan:**

- Data log HTTP.
- Daftar log dengan status error.
- Daftar endpoint sensitif.
- Hasil masking IP address.
- Total latensi insiden.
- Bukti bahwa log asli tidak berubah.

### Aplikasi 5 — `app5.py`

**Nested Inventory & Warehouse Valuation Engine**

**Domain:** Audit stok gudang multi-rak dengan struktur daftar bersarang, mulai dari kategori, sub-rak, hingga item barang.

Alur implementasi:

1. Meratakan struktur hierarki stok bersarang menjadi daftar datar menggunakan:

   ```python
   recursive_flatten()
   ```

2. Memperkaya setiap item dengan total valuasi aset menggunakan:

   ```python
   stok * harga_satuan
   ```

3. Menggunakan `make_map_step()` untuk melakukan transformasi data secara immutable.

4. Menyaring item dengan stok menipis menggunakan comparator `lt`.

5. Menghasilkan rekomendasi restock.

6. Menghitung total valuasi seluruh aset gudang menggunakan:

   ```python
   recursive_sum_field()
   ```

7. Membuktikan bahwa struktur nested awal tetap utuh:

   ```python
   assert original_data == backup_copy
   ```

**Output yang diharapkan:**

- Struktur inventaris awal.
- Hasil flatten inventaris.
- Daftar item dengan valuasi aset.
- Daftar item yang memerlukan restock.
- Total valuasi seluruh aset gudang.
- Bukti immutability terhadap struktur data nested.

## 6. Instruksi Eksekusi untuk AI Agent

Implementasikan proyek secara bertahap dan jangan melewati tahapan sebelum tahap sebelumnya berhasil.

### Tahap 1 — Implementasi Library Inti

Buat file `fplib.py` terlebih dahulu.

Pastikan seluruh fungsi sesuai kontrak pada Bagian 4, termasuk:

- Pure Functions.
- Deep-copy immutability.
- Pure recursion.
- Exception handling.
- Lazy evaluation.
- Currying dan closures.
- Higher-Order Functions.
- Declarative pipeline.
- Decorators.

### Tahap 2 — Implementasi Aplikasi

Setelah `fplib.py` selesai, buat aplikasi secara berurutan:

1. `app1.py`
2. `app2.py`
3. `app3.py`
4. `app4.py`
5. `app5.py`

Setiap aplikasi harus menggunakan fungsi dari library inti, bukan membuat ulang seluruh fungsi yang sudah tersedia di `fplib.py`.

### Tahap 3 — Pengujian

Jalankan seluruh aplikasi melalui terminal:

```bash
python3 app1.py
python3 app2.py
python3 app3.py
python3 app4.py
python3 app5.py
```

Pastikan:

- Tidak ada syntax error.
- Tidak ada runtime exception yang tidak tertangani.
- Semua assertion berhasil.
- Seluruh dataset asli tidak berubah setelah pemrosesan.
- Semua output sesuai dengan studi kasus.
- Seluruh fungsi rekursif mematuhi larangan penggunaan loop, `len()`, dan `sum()` bawaan Python.

### Tahap 4 — Dokumentasi

Buat `README.md` yang memuat:

1. Deskripsi proyek.
2. Tujuan dan ruang lingkup.
3. Struktur direktori.
4. Penjelasan arsitektur `fplib.py`.
5. Penjelasan masing-masing aplikasi.
6. Cara menjalankan seluruh aplikasi.
7. Contoh output terminal.
8. Penjelasan konsep Functional Programming yang diterapkan.
9. Matriks pemetaan konsep Modul 1–4 ke fungsi `fplib.py` dan aplikasi `app1.py`–`app5.py`.

### Tahap 5 — Final Verification

Lakukan pemeriksaan akhir terhadap seluruh file.

Jangan menyatakan proyek selesai sebelum seluruh aplikasi berhasil dijalankan dan seluruh assertion berhasil.

Jika ditemukan kesalahan, perbaiki kode dan ulangi pengujian sampai seluruh aplikasi berjalan sesuai spesifikasi.

## 7. Standar Kualitas Implementasi

AI Agent harus memastikan hasil akhir memenuhi standar berikut:

- Kode bersih, konsisten, modular, dan mudah dipahami.
- Penamaan fungsi dan variabel deskriptif.
- Setiap fungsi library memiliki docstring lengkap.
- Tidak terdapat duplikasi logika yang tidak diperlukan.
- Tidak terdapat dependency eksternal.
- Seluruh aplikasi benar-benar mengimpor `fplib.py`.
- Konsep Modul 1–4 terlihat jelas dalam implementasi.
- Setiap aplikasi memiliki studi kasus dan dataset yang realistis.
- Output terminal mudah dibaca dan informatif.
- Pengujian immutability dilakukan secara eksplisit.

**Prioritas utama proyek adalah menunjukkan pemahaman dan penerapan konsep Functional Programming secara benar, bukan sekadar menghasilkan program yang berjalan.**
