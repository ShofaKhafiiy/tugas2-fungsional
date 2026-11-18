"""Aplikasi 5: Nested Inventory & Warehouse Valuation Engine."""

from copy import deepcopy

from fplib import (
    COMPARATORS,
    curry_filter_by,
    immutable_update_record,
    make_filter_step,
    make_map_step,
    recursive_flatten,
    recursive_length,
    recursive_sum_field,
    run_pipeline,
)

RESTOCK_THRESHOLD = 5
RESTOCK_TARGET = 10
MIN_STOCK_LIMIT = RESTOCK_THRESHOLD

INVENTORY = [
    {
        "kategori": "Elektronik",
        "raks": [
            {
                "kode": "A1",
                "items": [
                    {
                        "sku": "E-01",
                        "nama": "Laptop Lenovo IdeaPad",
                        "stok": 4,
                        "harga_satuan": 12500000,
                    },
                    {
                        "sku": "E-02",
                        "nama": "Mouse Wireless",
                        "stok": 24,
                        "harga_satuan": 185000,
                    },
                    {
                        "sku": "E-03",
                        "nama": "Keyboard Mechanical",
                        "stok": 7,
                        "harga_satuan": 850000,
                    },
                ],
            },
            {
                "kode": "A2",
                "items": [
                    {
                        "sku": "E-04",
                        "nama": 'Monitor 27" IPS',
                        "stok": 3,
                        "harga_satuan": 3200000,
                    },
                    {
                        "sku": "E-05",
                        "nama": "SSD NVMe 1TB",
                        "stok": 15,
                        "harga_satuan": 1100000,
                    },
                ],
            },
        ],
    },
    {
        "kategori": "Furniture",
        "raks": [
            {
                "kode": "B1",
                "items": [
                    {
                        "sku": "F-01",
                        "nama": "Kursi Kantor Ergonomis",
                        "stok": 9,
                        "harga_satuan": 1450000,
                    },
                    {
                        "sku": "F-02",
                        "nama": "Meja Kerja Kayu",
                        "stok": 2,
                        "harga_satuan": 2750000,
                    },
                    {
                        "sku": "F-03",
                        "nama": "Lemari Arsip Besi",
                        "stok": 6,
                        "harga_satuan": 3100000,
                    },
                ],
            },
            {
                "kode": "B2",
                "items": [
                    {
                        "sku": "F-04",
                        "nama": "Rak Buku Minimalis",
                        "stok": 12,
                        "harga_satuan": 920000,
                    },
                    {
                        "sku": "F-05",
                        "nama": "Lampu Meja LED",
                        "stok": 18,
                        "harga_satuan": 275000,
                    },
                ],
            },
        ],
    },
    {
        "kategori": "Stationery",
        "raks": [
            {
                "kode": "C1",
                "items": [
                    {
                        "sku": "S-01",
                        "nama": "Kertas A4 80 gram",
                        "stok": 40,
                        "harga_satuan": 48000,
                    },
                    {
                        "sku": "S-02",
                        "nama": "Pensil Grafit 2B",
                        "stok": 4,
                        "harga_satuan": 12000,
                    },
                    {
                        "sku": "S-03",
                        "nama": "Penggaris Besi 30 cm",
                        "stok": 30,
                        "harga_satuan": 15000,
                    },
                ],
            }
        ],
    },
]

is_low_stock = curry_filter_by("stok")(COMPARATORS["lt"])(MIN_STOCK_LIMIT)


def enrich_valuation(item):
    """
    desc:
        Menambahkan valuasi aset kepada salinan item gudang.

    pre-cond:
        item memiliki field stok dan harga_satuan bernilai numerik.

    post-cond:
        Mengembalikan dictionary baru dengan field valuasi tanpa mutasi.
    """
    return immutable_update_record(
        item, {"valuasi": item["stok"] * item["harga_satuan"]}
    )


def add_restock_recommendation(item):
    """
    desc:
        Menambahkan jumlah rekomendasi restock hingga mencapai target stok.

    pre-cond:
        item memiliki stok di bawah ambang restock.

    post-cond:
        Mengembalikan salinan item dengan field rekomendasi_restock.
    """
    return immutable_update_record(
        item, {"rekomendasi_restock": RESTOCK_TARGET - item["stok"]}
    )


def flatten_inventory(inventory):
    """
    desc:
        Mengumpulkan item dari semua kategori dan rak ke dalam struktur
        nested list, lalu meratakannya dengan recursive_flatten.

    pre-cond:
        inventory berupa daftar kategori yang setiap elemennya memiliki raks
        dan setiap rak memiliki items.

    post-cond:
        Mengembalikan list datar berisi item tanpa mengubah struktur awal.
    """
    nested_items = [
        [list(rak["items"]) for rak in category["raks"]]
        for category in inventory
    ]
    return recursive_flatten(nested_items)


def build_inventory_report(inventory):
    """
    desc:
        Membangun laporan valuasi gudang dari struktur nested: flatten,
        enrich valuasi, filtrasi stok menipis, rekomendasi restock, dan
        total valuasi rekursif.

    pre-cond:
        inventory berupa struktur rak bertingkat yang valid.

    post-cond:
        Mengembalikan dictionary laporan; inventory asli tidak diubah.
    """
    flat_items = flatten_inventory(inventory)
    valued_items = run_pipeline(flat_items, make_map_step(enrich_valuation))
    low_stock_items = run_pipeline(valued_items, make_filter_step(is_low_stock))
    restock_items = run_pipeline(
        low_stock_items, make_map_step(add_restock_recommendation)
    )
    return {
        "inventory": inventory,
        "flat_items": flat_items,
        "valued_items": valued_items,
        "restock_items": restock_items,
        "item_count": recursive_length(valued_items),
        "restock_count": recursive_length(restock_items),
        "total_valuation": recursive_sum_field(valued_items, "valuasi"),
    }


def verify_immutability(original, backup):
    """
    desc:
        Membuktikan struktur nested awal tetap utuh setelah diproses.

    pre-cond:
        original dan backup dapat dibandingkan nilainya secara deep.

    post-cond:
        Mengembalikan True apabila kedua struktur identik.
    """
    return original == backup


def format_inventory_structure(inventory):
    """
    desc:
        Menyusun representasi teks dari struktur inventaris bertingkat.

    pre-cond:
        inventory berupa daftar kategori dengan rak dan item.

    post-cond:
        Mengembalikan string struktur tanpa I/O.
    """
    lines = []
    for category in inventory:
        lines.append(f"  {category['kategori']}")
        for rack in category["raks"]:
            lines.append(f"    Rak {rack['kode']}")
            for item in rack["items"]:
                lines.append(
                    f"      {item['sku']} | {item['nama']} | stok={item['stok']}"
                )
    return "\n".join(lines)


def format_report(report):
    """
    desc:
        Menyusun tampilan terminal untuk hasil audit inventaris gudang.

    pre-cond:
        report berasal dari build_inventory_report.

    post-cond:
        Mengembalikan string laporan tanpa efek samping.
    """
    lines = [
        "=== APP 5: NESTED INVENTORY & WAREHOUSE VALUATION ENGINE ===",
        "Struktur inventaris awal:",
        format_inventory_structure(report["inventory"]),
        "",
        f"Hasil recursive_flatten ({report['item_count']} item):",
    ]
    for item in report["flat_items"]:
        lines.append(f"  {item['sku']} | {item['nama']}")
    lines.extend(["", "Daftar item dengan valuasi aset:"])
    for item in report["valued_items"]:
        lines.append(
            f"  {item['sku']} | {item['nama']:<24} | stok={item['stok']:>3} "
            f"| harga={item['harga_satuan']:>11,} | valuasi={item['valuasi']:>13,}"
        )
    lines.extend(["", "Item memerlukan restock (stok < 5):"])
    for item in report["restock_items"]:
        lines.append(
            f"  {item['sku']} | {item['nama']} | sisa={item['stok']} "
            f"| tambah={item['rekomendasi_restock']} unit"
        )
    lines.extend(
        [
            "",
            f"Jumlah item perlu restock          : {report['restock_count']}",
            f"Total valuasi seluruh aset gudang  : {report['total_valuation']:,}",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    inventory_backup = deepcopy(INVENTORY)
    inventory_report = build_inventory_report(INVENTORY)

    assert verify_immutability(INVENTORY, inventory_backup)
    assert inventory_report["item_count"] == 13
    assert inventory_report["restock_count"] == 4
    assert [item["sku"] for item in inventory_report["restock_items"]] == [
        "E-01",
        "E-04",
        "F-02",
        "S-02",
    ]
    assert inventory_report["total_valuation"] == 142048000
    assert INVENTORY[0]["raks"][0]["items"][0].get("valuasi") is None

    print(format_report(inventory_report))
    print("Bukti immutability : assert INVENTORY == inventory_backup berhasil")
