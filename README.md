# Functional Programming Library & 5 Aplikasi Terapan

## 1. Deskripsi Proyek

Proyek ini adalah implementasi Pemrograman Fungsional UMM Modul 1–4 dalam satu library inti `fplib.py` dan lima aplikasi terapan independen `app1.py`–`app5.py`. Seluruh kode menggunakan Python 3 dan **hanya Python Standard Library**, tanpa dependency eksternal.

Library `fplib.py` menyediakan decorator, rekursi murni, immutability berbasis `deepcopy`, lazy stream, currying/closure, first-class function, lambda, serta declarative pipeline. Kelima aplikasi memakai komponen tersebut untuk studi kasus e-commerce, IoT, akademik, audit log, dan inventaris gudang.

Fokus utama proyek ini bukan sekadar program berjalan, melainkan pembuktian bahwa konsep fungsional diterapkan secara nyata: tidak ada mutasi input, tidak ada I/O di fungsi komputasi, rekursi tanpa loop/`len()`/`sum()`, dan setiap transformasi menghasilkan objek baru.

## 2. Tujuan dan Ruang Lingkup

Tujuan proyek:

1. Membangun `fplib.py` yang memenuhi seluruh kontrak fungsional Modul 1–4.
2. Membangun lima aplikasi dengan dataset realistis minimal 10 record utama.
3. Memastikan setiap aplikasi mengimpor dan memakai `fplib.py`, bukan menulis ulang logika library.
4. Membuktikan immutability secara eksplisit dengan `assert` pada setiap aplikasi.
5. Mengisolasi seluruh `print()` di dalam blok `if __name__ == "__main__":`.
6. Menyediakan dokumentasi arsitektur dan pemetaan konsep Modul 1–4.

Ruang lingkup mencakup library inti, lima aplikasi CLI, pengujian manual melalui terminal, serta dokumentasi ini. Tidak termasuk antarmuka web, basis data, atau paket pihak ketiga.

## 3. Struktur Direktori

```text
tugas2-fungsional/
├── fplib.py
├── app1.py
├── app2.py
├── app3.py
├── app4.py
├── app5.py
├── README.md
├── LAPORAN.md
├── LAPORAN.docx
├── bukti/
└── writing-block.md
```

Repository: https://github.com/ShofaKhafiiy/tugas2-fungsional (branch `main`). Folder ini adalah root repository.

Keterangan singkat:

| File | Fungsi |
|---|---|
| `fplib.py` | Core Functional Programming Library |
| `app1.py` | E-Commerce Dynamic Pricing & Order Pipeline |
| `app2.py` | IoT Telemetry & Sensor Anomaly Stream Analyzer |
| `app3.py` | Academic Gradebook & Scholarship Eligibility Evaluator |
| `app4.py` | Server Log Audit & Security Incident Filter |
| `app5.py` | Nested Inventory & Warehouse Valuation Engine |
| `README.md` | Dokumentasi arsitektur dan pemetaan konsep |

## 4. Arsitektur `fplib.py`

`fplib.py` dirancang sebagai satu lapisan utilitas murni yang dikonsumsi oleh kelima aplikasi.

### 4.1 Decorator (Modul 4)

| Fungsi | Peran |
|---|---|
| `@measure_time` | Mengukur durasi eksekusi dengan `time.perf_counter()` dan mengembalikan `(hasil, durasi_ms)`; memakai `functools.wraps`. |
| `@enforce_immutability` | Melakukan `deepcopy()` pada seluruh `*args` dan `**kwargs` sebelum fungsi dipanggil. |
| `@validate_non_empty` | Menolak argumen pertama yang kosong dengan `ValueError` informatif. |

### 4.2 Rekursi dan Penanganan Kesalahan (Modul 1 & 3)

| Fungsi | Peran |
|---|---|
| `recursive_length(seq)` | Menghitung panjang sequence tanpa `len()`/`for`/`while`; pola `try-except-else` pada `IndexError`. |
| `recursive_sum(numbers)` | Menjumlahkan sequence datar tanpa `sum()`. |
| `recursive_sum_field(records, field_name)` | Menjumlahkan field pada list of dict secara head-and-tail. |
| `recursive_flatten(nested_list)` | Meratakan nested list berkedalaman bebas. |
| `safe_execute(func, *args, fallback=None, **kwargs)` | Menjalankan fungsi dalam `try-except-else` dan mengembalikan `{"ok", "data", "error"}`. |

### 4.3 Immutability dan Lazy Evaluation (Modul 2)

| Fungsi | Peran |
|---|---|
| `immutable_update_record(record, updates)` | Menggabungkan record dan updates menjadi dictionary baru, termasuk nested dict. |
| `lazy_filter_stream(iterable, predicate)` | Generator `yield` yang menyaring item dan menghasilkan `deepcopy(item)`. |
| `lazy_transform_stream(iterable, transformer)` | Generator `yield` yang mentransformasi item tanpa mutasi. |

### 4.4 Currying, Closure, Lambda, dan Pipeline (Modul 3 & 4)

| Komponen | Peran |
|---|---|
| `curry_filter_by(key)(comparator)(threshold)` | Membangun predikat dictionary secara bertahap. |
| `curry_transform_field(source_key)(target_key)(calc_fn)` | Membangun mapper field turunan. |
| `curry_rate_adjuster(rate_percent)` | Membuat fungsi `base_amount * (1 + rate_percent / 100)`. |
| `COMPARATORS` | First-class lambda: `eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `contains`. |
| `add_values` | Lambda agregasi `acc + val` untuk `reduce()`. |
| `run_pipeline(dataset, *steps)` | Mengomposisi step satu argumen dengan `reduce()` dan `@enforce_immutability`. |
| `make_filter_step`, `make_map_step`, `make_reduce_step` | Adapter `filter()`, `map()`, dan `reduce()` agar dapat dirangkai. |

Semua fungsi di `fplib.py` memiliki docstring dengan format `desc:`, `pre-cond:`, dan `post-cond:`.

## 5. Penjelasan Masing-Masing Aplikasi

### 5.1 `app1.py` — E-Commerce Dynamic Pricing & Order Pipeline

Dataset: 10 pesanan elektronik dengan nested `items`.

Alur:

1. Filter `status == "paid"` dengan `curry_filter_by` + `COMPARATORS["eq"]`.
2. Filter subtotal minimal dengan `gte`.
3. Diskon member 10% via `curry_rate_adjuster(-10)`.
4. PPN 11% via `curry_rate_adjuster(11)`.
5. Tambah field harga dengan `curry_transform_field`.
6. Rangkai pipeline dengan `run_pipeline()` dan bungkus `@measure_time`.
7. Hitung omzet bersih via `recursive_sum_field()` dan jumlah transaksi via `recursive_length()`.

Angka kunci: 10 total pesanan, 7 paid, 6 lolos subtotal, omzet bersih `12,787,200.00`.

### 5.2 `app2.py` — IoT Telemetry & Sensor Anomaly Stream Analyzer

Dataset: 13 pembacaan sensor suhu, LDR, dan getaran dengan nested `info`.

Alur:

1. `lazy_filter_stream()` menyaring pembacaan di atas ambang.
2. `lazy_transform_stream()` menambahkan klasifikasi `PERINGATAN`/`KRITIS` secara immutable.
3. Generator expression mengekstrak nilai numerik sebelum dikonsumsi.
4. `itertools.islice()` mengambil 4 anomali pertama tanpa menghabiskan stream.
5. `safe_execute()` menguji 3 data korup/hilang.

Angka kunci: 4 anomali pertama `R01`, `R03`, `R04`, `R06`; 3 data korup tertangani.

### 5.3 `app3.py` — Academic Gradebook & Scholarship Eligibility Evaluator

Dataset: 10 mahasiswa dengan nested `nilai` (tugas, UTS, UAS).

Alur:

1. `WEIGHTS` menyimpan rumus konversi sebagai first-class function.
2. `make_map_step(enrich_with_ipk)` menghitung IPK secara immutable.
3. `curry_filter_by` menyaring IPK `>= 3.50` dan status `aktif`.
4. Rata-rata IPK dihitung dengan `recursive_sum_field()` / `recursive_length()`.
5. `@validate_non_empty` diuji terhadap dataset kosong melalui `safe_execute()`.

Angka kunci: 3 kandidat lolos, rata-rata IPK `3.66`.

### 5.4 `app4.py` — Server Log Audit & Security Incident Filter

Dataset: 12 log HTTP dengan nested `headers`.

Alur:

1. Filter `status >= 400` dengan `curry_filter_by` + `gte`.
2. Filter endpoint sensitif `/admin`, `/internal`, `/config` dengan `COMPARATORS["contains"]`.
3. Komposisi predikat curried `and_predicates` dan `or_predicates` membentuk filter insiden.
4. Masking IP dengan `immutable_update_record()`.
5. Total latensi insiden dihitung dengan `make_reduce_step(add_values, 0)` di dalam `run_pipeline()`.

Angka kunci: 6 log error, 5 endpoint sensitif, 4 insiden, total latensi `1720 ms`.

### 5.5 `app5.py` — Nested Inventory & Warehouse Valuation Engine

Dataset: 13 item dalam 3 kategori dan 5 rak bersarang.

Alur:

1. `recursive_flatten()` meratakan struktur kategori → rak → item.
2. `make_map_step(enrich_valuation)` menambahkan `valuasi = stok * harga_satuan`.
3. `curry_filter_by("stok")(COMPARATORS["lt"])(5)` menyaring stok menipis.
4. `make_map_step(add_restock_recommendation)` menghasilkan rekomendasi restock.
5. `recursive_sum_field()` menghitung total valuasi aset.
6. `assert INVENTORY == inventory_backup` membuktikan struktur nested tetap utuh.

Angka kunci: 13 item, 4 item restock, total valuasi `142,048,000`.

## 6. Cara Menjalankan Seluruh Aplikasi

Dari repository `tugas2-fungsional`:

```bash
git clone -b main https://github.com/ShofaKhafiiy/tugas2-fungsional.git
cd tugas2-fungsional
python3 -m py_compile fplib.py app1.py app2.py app3.py app4.py app5.py
python3 app1.py
python3 app2.py
python3 app3.py
python3 app4.py
python3 app5.py
```

Jika repository sudah di-clone, cukup jalankan `git pull origin main` lalu masuk ke folder `tugas2-fungsional`. Setiap aplikasi mencetak bagian akhir `Bukti immutability : assert ... berhasil`. Jika ada assertion yang gagal, jangan nyatakan proyek selesai; perbaiki kode dan ulangi dari `fplib.py`.

## 7. Contoh Output Terminal

Cuplikan `python3 app1.py`:

```text
=== APP 1: E-COMMERCE DYNAMIC PRICING & ORDER PIPELINE ===
Jumlah seluruh pesanan      : 10
Jumlah pesanan paid         : 7
Transaksi lolos subtotal    : 6

Rincian harga (subtotal -> diskon 10% -> PPN 11%):
  ORD-1001: 1,250,000.00 -> 1,125,000.00 | PPN 123,750.00 | Total 1,248,750.00
  ...
Total omzet bersih          : 12,787,200.00
Durasi eksekusi pipeline    : 0.4173 ms
Bukti immutability : assert ORDERS == orders_backup berhasil
```

Cuplikan `python3 app5.py`:

```text
=== APP 5: NESTED INVENTORY & WAREHOUSE VALUATION ENGINE ===
Hasil recursive_flatten (13 item):
  E-01 | Laptop Lenovo IdeaPad
  ...
Item memerlukan restock (stok < 5):
  E-01 | Laptop Lenovo IdeaPad | sisa=4 | tambah=6 unit
  ...
Jumlah item perlu restock          : 4
Total valuasi seluruh aset gudang  : 142,048,000
Bukti immutability : assert INVENTORY == inventory_backup berhasil
```

Durasi pada `app1.py` bersifat dinamis sehingga angka milidetik dapat berbeda pada setiap eksekusi.

## 8. Konsep Functional Programming yang Diterapkan

| Konsep | Implementasi Nyata |
|---|---|
| Pure function | Fungsi komputasi tidak memakai `print()`, `input()`, atau mutasi global. |
| Referential transparency | Input sama menghasilkan output sama; hasil tidak bergantung state tersembunyi. |
| Immutability | `deepcopy()` + konstruksi dictionary/list baru; tidak ada `.append()`, `.pop()`, `.sort()`, atau `dict[key] = value` pada input. |
| Pure recursion | Head-and-tail, `try-except-else`, tanpa `for`, `while`, `len()`, `sum()` pada fungsi rekursif. |
| Exception handling | `safe_execute()` dan `@validate_non_empty`. |
| Lazy evaluation | Generator `yield` pada `lazy_filter_stream()` dan `lazy_transform_stream()`. |
| Higher-order function | Fungsi menerima/mengembalikan fungsi: decorator, adapter pipeline, curry. |
| First-class function | `COMPARATORS`, `add_values`, `WEIGHTS`, dan fungsi predikat disimpan sebagai nilai. |
| Lambda/closure | `lambda` pada comparator dan adjuster; closure pada curry stages. |
| Currying | `curry_filter_by`, `curry_transform_field`, `curry_rate_adjuster`. |
| Composition/pipeline | `run_pipeline()` + `make_filter_step()` + `make_map_step()` + `make_reduce_step()`. |
| Decorator | `@measure_time`, `@enforce_immutability`, `@validate_non_empty`. |
| Effect isolation | Semua I/O berada di `if __name__ == "__main__":`. |

## 9. Matriks Pemetaan Modul 1–4

| Modul | Konsep | `fplib.py` | Aplikasi |
|---|---|---|---|
| Modul 1 | Pure function & dekomposisi | Semua fungsi komputasi | Semua fungsi logika di `app1.py`–`app5.py` |
| Modul 1 | Rekursi head-and-tail | `recursive_length`, `recursive_sum` | `app1` omzet, `app2` jumlah pembacaan, `app3` rata-rata IPK, `app5` flatten & valuasi |
| Modul 2 | Immutability / deep copy | `immutable_update_record`, `enforce_immutability`, `run_pipeline` | `assert` immutability di kelima aplikasi |
| Modul 2 | Lazy evaluation / `yield` | `lazy_filter_stream`, `lazy_transform_stream` | `app2` stream sensor; generator expression nilai numerik |
| Modul 3 | Exception handling | `safe_execute`, `validate_non_empty` | `app2` sensor korup; `app3` dataset kosong |
| Modul 3 | First-class function & lambda | `COMPARATORS`, `add_values`, curry functions | `app1` comparator paid/subtotal; `app3` `WEIGHTS`; `app4` `contains` |
| Modul 3 | Rekursi lanjutan | `recursive_sum_field`, `recursive_flatten` | `app5` struktur nested dan total valuasi |
| Modul 4 | Decorator | `measure_time`, `enforce_immutability`, `validate_non_empty` | `app1` durasi pipeline; `app3` validator |
| Modul 4 | Currying & closure | `curry_filter_by`, `curry_transform_field`, `curry_rate_adjuster` | `app1` diskon/PPN; `app3` IPK/status; `app4` filter insiden; `app5` stok menipis |
| Modul 4 | Declarative pipeline | `run_pipeline`, `make_filter_step`, `make_map_step`, `make_reduce_step` | `app1`, `app3`, `app4`, `app5` |

## Referensi

- `writing-block.md` — spesifikasi proyek Pemrograman Fungsional UMM.
- Modul 1–4 Pemrograman Fungsional UMM.
- Python Software Foundation. *Python 3 Standard Library: functools, itertools, copy, time*. https://docs.python.org/3/
