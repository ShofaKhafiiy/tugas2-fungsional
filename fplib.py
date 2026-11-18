"""Core Functional Programming library for Modul 1-4 praktikum UMM."""

from copy import deepcopy
from functools import reduce, wraps
from time import perf_counter


def measure_time(func):
    """
    desc:
        Mengukur durasi eksekusi fungsi yang dibungkus dan mengembalikan
        pasangan hasil fungsi serta durasi dalam milidetik.

    pre-cond:
        func harus berupa callable yang dapat dipanggil dengan argumen
        yang diberikan pemanggil.

    post-cond:
        Mengembalikan tuple (hasil_fungsi, durasi_ms) dengan durasi_ms
        bernilai float dan metadata fungsi asli tetap terjaga.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        desc:
            Menjalankan fungsi asli sambil mencatat waktu sebelum dan sesudah
            eksekusi menggunakan time.perf_counter().

        pre-cond:
            Argumen diteruskan apa adanya dari pemanggil decorator.

        post-cond:
            Mengembalikan tuple berisi hasil fungsi asli dan durasi milidetik.
        """
        start = perf_counter()
        result = func(*args, **kwargs)
        duration_ms = (perf_counter() - start) * 1000
        return result, duration_ms

    return wrapper


def enforce_immutability(func):
    """
    desc:
        Melindungi data pemanggil dengan melakukan deepcopy terhadap seluruh
        argumen posisional dan keyword sebelum diteruskan ke fungsi asli.

    pre-cond:
        func harus berupa callable dan seluruh argumen harus dapat di-deepcopy.

    post-cond:
        Fungsi hasil pembungkus tidak dapat mengubah objek asli pemanggil
        melalui argumen yang diterimanya.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        desc:
            Membuat salinan mendalam dari args dan kwargs, lalu memanggil
            fungsi asli dengan salinan tersebut.

        pre-cond:
            Argumen berasal dari pemanggil decorator.

        post-cond:
            Objek asli pemanggil tidak berubah setelah fungsi asli dijalankan.
        """
        copied_args = deepcopy(args)
        copied_kwargs = deepcopy(kwargs)
        return func(*copied_args, **copied_kwargs)

    return wrapper


def validate_non_empty(func):
    """
    desc:
        Memvalidasi bahwa argumen pertama pemanggil tidak kosong sebelum
        menjalankan fungsi asli.

    pre-cond:
        func menerima minimal satu argumen dan argumen pertama dapat
        dievaluasi kebenarannya (truthiness).

    post-cond:
        ValueError dengan pesan informatif dimunculkan untuk argumen kosong;
        jika tidak kosong, fungsi asli dijalankan sebagaimana mestinya.
    """

    @wraps(func)
    def wrapper(first_arg, *args, **kwargs):
        """
        desc:
            Memeriksa argumen pertama lalu meneruskannya ke fungsi asli
            apabila tidak kosong.

        pre-cond:
            first_arg merupakan argumen wajib pertama dari fungsi asli.

        post-cond:
            Fungsi asli hanya dipanggil untuk first_arg yang tidak kosong.
        """
        if not first_arg:
            raise ValueError(
                f"{func.__name__} menolak argumen pertama yang kosong: {first_arg!r}"
            )
        return func(first_arg, *args, **kwargs)

    return wrapper


def recursive_length(seq, index=0):
    """
    desc:
        Menghitung panjang sequence secara rekursif dengan pendekatan
        head and tail melalui indeks yang naik satu pada setiap pemanggilan.

    pre-cond:
        seq merupakan sequence yang dapat diindeks dan index bilangan bulat
        non-negatif.

    post-cond:
        Mengembalikan jumlah elemen seq tanpa menggunakan len(), for, atau while.
    """
    try:
        seq[index]
    except IndexError:
        return index
    else:
        return recursive_length(seq, index + 1)


def recursive_sum(numbers):
    """
    desc:
        Menjumlahkan seluruh elemen numerik pada sequence datar secara
        rekursif dengan memisahkan elemen pertama dan sisanya.

    pre-cond:
        numbers merupakan sequence datar berisi nilai numerik.

    post-cond:
        Mengembalikan total numerik tanpa menggunakan sum(), for, atau while.
    """
    try:
        head = numbers[0]
    except IndexError:
        return 0
    else:
        return head + recursive_sum(numbers[1:])


def recursive_sum_field(records, field_name):
    """
    desc:
        Menjumlahkan nilai suatu field pada seluruh record list[dict]
        menggunakan rekursi head and tail.

    pre-cond:
        records berupa sequence dictionary dan setiap record memiliki field_name
        bernilai numerik.

    post-cond:
        Mengembalikan total nilai field tanpa perulangan, len(), atau sum().
    """
    try:
        head = records[0]
    except IndexError:
        return 0
    else:
        return head[field_name] + recursive_sum_field(records[1:], field_name)


def recursive_flatten(nested_list):
    """
    desc:
        Meratakan nested list dengan kedalaman bebas menjadi satu list datar
        melalui rekursi pada elemen pertama dan sisa list.

    pre-cond:
        nested_list berupa list yang elemennya dapat berupa list lain atau nilai.

    post-cond:
        Mengembalikan list datar baru; list asli tidak dimodifikasi.
    """
    try:
        head = nested_list[0]
    except IndexError:
        return []
    else:
        head_part = recursive_flatten(head) if isinstance(head, list) else [head]
        return head_part + recursive_flatten(nested_list[1:])


def safe_execute(func, *args, fallback=None, **kwargs):
    """
    desc:
        Menjalankan fungsi di dalam blok try-except-else dan mengembalikan
        hasil terstruktur beserta informasi keberhasilan atau kesalahan.

    pre-cond:
        func merupakan callable; argumen dan keyword diteruskan apa adanya.

    post-cond:
        Mengembalikan dictionary dengan kunci ok, data, dan error; fallback
        disalin mendalam agar tidak menjadi referensi objek pemanggil.
    """
    try:
        result = func(*args, **kwargs)
    except Exception as error:
        return {"ok": False, "data": deepcopy(fallback), "error": str(error)}
    else:
        return {"ok": True, "data": result, "error": None}


def _merge_items(base, items):
    """
    desc:
        Menggabungkan pasangan kunci-nilai ke dalam dictionary baru secara
        rekursif, termasuk penggabungan dictionary bersarang.

    pre-cond:
        base berupa dictionary dan items berupa list pasangan (key, value).

    post-cond:
        Mengembalikan dictionary baru tanpa mengubah base maupun items.
    """
    try:
        key, value = items[0]
    except IndexError:
        return deepcopy(base)
    else:
        current = base.get(key)
        if isinstance(value, dict) and isinstance(current, dict):
            merged_value = _merge_items(current, list(value.items()))
        else:
            merged_value = deepcopy(value)
        merged_base = {**deepcopy(base), key: merged_value}
        return _merge_items(merged_base, items[1:])


def immutable_update_record(record, updates):
    """
    desc:
        Menghasilkan dictionary baru dari penggabungan record dan updates
        dengan dukungan penuh terhadap data bersarang.

    pre-cond:
        record dan updates berupa dictionary.

    post-cond:
        Mengembalikan dictionary baru; record dan updates asli tidak berubah.
    """
    return _merge_items(record, list(updates.items()))


def lazy_filter_stream(iterable, predicate):
    """
    desc:
        Menyaring item satu per satu secara lazy menggunakan generator dan
        menghasilkan salinan mendalam setiap item yang lolos predikat.

    pre-cond:
        iterable dapat diiterasi dan predicate berupa callable yang
        mengembalikan nilai truthy atau falsy.

    post-cond:
        Menghasilkan generator; item sumber tidak pernah dikonsumsi sebagai
        referensi langsung oleh konsumen generator.
    """
    for item in iterable:
        if predicate(item):
            yield deepcopy(item)


def lazy_transform_stream(iterable, transformer):
    """
    desc:
        Mentransformasi item satu per satu secara lazy menggunakan generator,
        dengan deepcopy pada input transformer maupun hasilnya.

    pre-cond:
        iterable dapat diiterasi dan transformer berupa callable satu argumen.

    post-cond:
        Menghasilkan generator berisi objek baru yang terlepas dari sumber.
    """
    for item in iterable:
        yield deepcopy(transformer(deepcopy(item)))


def curry_filter_by(key):
    """
    desc:
        Membangun predikat penyaring dictionary secara curried berdasarkan
        field, comparator, dan nilai ambang.

    pre-cond:
        key merupakan kunci dictionary yang akan dibaca dari setiap record.

    post-cond:
        Mengembalikan closure bertingkat yang akhirnya menghasilkan fungsi
        predikat record -> bool.
    """

    def comparator_stage(comparator):
        """
        desc:
            Menyimpan comparator ke dalam closure untuk tahap ambang nilai.

        pre-cond:
            comparator menerima dua argumen dan mengembalikan boolean.

        post-cond:
            Mengembalikan fungsi yang menunggu nilai ambang.
        """

        def threshold_stage(threshold):
            """
            desc:
                Menyimpan nilai ambang ke dalam closure untuk membuat predikat.

            pre-cond:
                threshold dapat dibandingkan oleh comparator.

            post-cond:
                Mengembalikan fungsi predikat untuk satu record.
            """

            def predicate(record):
                """
                desc:
                    Membandingkan nilai field record dengan nilai ambang.

                pre-cond:
                    record berupa dictionary yang mungkin memiliki kunci key.

                post-cond:
                    Mengembalikan hasil comparator tanpa mengubah record.
                """
                return comparator(record.get(key), threshold)

            return predicate

        return threshold_stage

    return comparator_stage


def curry_transform_field(source_key):
    """
    desc:
        Membangun mapper curried yang menurunkan field baru dari field sumber
        menggunakan fungsi kalkulasi tertentu.

    pre-cond:
        source_key merupakan kunci dictionary yang nilainya dapat dihitung.

    post-cond:
        Mengembalikan closure bertingkat yang akhirnya menghasilkan mapper
        record -> dictionary baru.
    """

    def target_stage(target_key):
        """
        desc:
            Menyimpan kunci tujuan ke dalam closure untuk tahap kalkulasi.

        pre-cond:
            target_key berupa string kunci dictionary.

        post-cond:
            Mengembalikan fungsi yang menunggu fungsi kalkulasi.
        """

        def calc_stage(calc_fn):
            """
            desc:
                Menyimpan fungsi kalkulasi ke dalam closure untuk membuat mapper.

            pre-cond:
                calc_fn menerima satu nilai dari source_key.

            post-cond:
                Mengembalikan fungsi mapper yang menghasilkan record baru.
            """

            def mapper(record):
                """
                desc:
                    Menambahkan target_key ke salinan record tanpa mutasi.

                pre-cond:
                    record memiliki source_key dan calc_fn dapat
                    memproses nilainya.

                post-cond:
                    Mengembalikan dictionary baru dengan field tambahan.
                """
                calculated = calc_fn(deepcopy(record[source_key]))
                return immutable_update_record(record, {target_key: calculated})

            return mapper

        return calc_stage

    return target_stage


def curry_rate_adjuster(rate_percent):
    """
    desc:
        Membuat closure penyesuaian nilai berdasarkan persentase tertentu.

    pre-cond:
        rate_percent berupa bilangan; nilai negatif berarti diskon.

    post-cond:
        Mengembalikan fungsi yang menghitung base_amount * (1 + rate_percent/100).
    """

    def adjust(base_amount):
        """
        desc:
            Menghitung nilai akhir setelah penyesuaian persentase.

        pre-cond:
            base_amount berupa bilangan.

        post-cond:
            Mengembalikan bilangan hasil penyesuaian tanpa efek samping.
        """
        return base_amount * (1 + rate_percent / 100)

    return adjust


COMPARATORS = {
    "eq": lambda left, right: left == right,
    "neq": lambda left, right: left != right,
    "gt": lambda left, right: left > right,
    "gte": lambda left, right: left >= right,
    "lt": lambda left, right: left < right,
    "lte": lambda left, right: left <= right,
    "contains": lambda container, candidate: candidate in container,
}

add_values = lambda acc, val: acc + val


def _apply_step(accumulator, step):
    """
    desc:
        Menerapkan satu langkah pipeline terhadap akumulator saat ini.

    pre-cond:
        step berupa callable satu argumen.

    post-cond:
        Mengembalikan hasil penerapan step pada accumulator.
    """
    return step(accumulator)


@enforce_immutability
def run_pipeline(dataset, *steps):
    """
    desc:
        Menjalankan deretan fungsi satu argumen dari kiri ke kanan menggunakan
        functools.reduce dengan dataset sebagai nilai awal.

    pre-cond:
        dataset dapat di-deepcopy dan setiap step menerima satu argumen
        berupa hasil step sebelumnya.

    post-cond:
        Mengembalikan hasil akhir pipeline tanpa mengubah dataset pemanggil.
    """
    return reduce(_apply_step, steps, dataset)


def make_filter_step(predicate):
    """
    desc:
        Membuat adapter pipeline yang membungkus operasi filter(), dengan
        deepcopy pada setiap item yang lolos.

    pre-cond:
        predicate berupa callable satu argumen yang menghasilkan boolean.

    post-cond:
        Mengembalikan fungsi step yang menghasilkan list item baru.
    """

    def filter_step(data):
        """
        desc:
            Menyaring data dan mengembalikan list hasil yang terpisah dari sumber.

        pre-cond:
            data berupa iterable.

        post-cond:
            Mengembalikan list berisi deepcopy dari item yang lolos predicate.
        """
        return [deepcopy(item) for item in filter(predicate, data)]

    return filter_step


def make_map_step(transformer):
    """
    desc:
        Membuat adapter pipeline yang membungkus operasi map() secara immutable.

    pre-cond:
        transformer berupa callable satu argumen.

    post-cond:
        Mengembalikan fungsi step yang menghasilkan list hasil transformasi baru.
    """

    def transform(item):
        """
        desc:
            Mentransformasi salinan item lalu menyalin kembali hasilnya.

        pre-cond:
            item dapat di-deepcopy.

        post-cond:
            Mengembalikan objek hasil yang tidak berbagi referensi dengan item.
        """
        return deepcopy(transformer(deepcopy(item)))

    def map_step(data):
        """
        desc:
            Memetakan seluruh item data menggunakan transformer.

        pre-cond:
            data berupa iterable.

        post-cond:
            Mengembalikan list hasil map tanpa mengubah data asli.
        """
        return list(map(transform, data))

    return map_step


def make_reduce_step(reducer_fn, initializer=None):
    """
    desc:
        Membuat adapter pipeline yang membungkus functools.reduce() dengan
        initializer opsional.

    pre-cond:
        reducer_fn menerima dua argumen; tanpa initializer, data tidak kosong.

    post-cond:
        Mengembalikan fungsi step yang menghasilkan satu nilai agregat.
    """

    def reduce_step(data):
        """
        desc:
            Mereduksi salinan data menjadi satu nilai agregat.

        pre-cond:
            data dapat di-deepcopy dan sesuai dengan reducer_fn.

        post-cond:
            Mengembalikan nilai agregat akhir tanpa mengubah data sumber.
        """
        copied_data = deepcopy(data)
        if initializer is None:
            return reduce(reducer_fn, copied_data)
        return reduce(reducer_fn, copied_data, deepcopy(initializer))

    return reduce_step
