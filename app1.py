"""Aplikasi 1: E-Commerce Dynamic Pricing & Order Pipeline."""

from copy import deepcopy

from fplib import (
    COMPARATORS,
    curry_filter_by,
    curry_rate_adjuster,
    curry_transform_field,
    make_filter_step,
    make_map_step,
    measure_time,
    recursive_length,
    recursive_sum_field,
    run_pipeline,
)

MIN_SUBTOTAL = 700000.0

ORDERS = (
    {
        "id": "ORD-1001",
        "status": "paid",
        "subtotal": 1250000.0,
        "items": [{"sku": "LAP-01", "qty": 1}, {"sku": "MOUSE-02", "qty": 2}],
    },
    {
        "id": "ORD-1002",
        "status": "paid",
        "subtotal": 980000.0,
        "items": [{"sku": "KEY-01", "qty": 1}],
    },
    {
        "id": "ORD-1003",
        "status": "pending",
        "subtotal": 2000000.0,
        "items": [{"sku": "MON-27", "qty": 1}],
    },
    {
        "id": "ORD-1004",
        "status": "paid",
        "subtotal": 450000.0,
        "items": [{"sku": "HDD-01", "qty": 1}],
    },
    {
        "id": "ORD-1005",
        "status": "paid",
        "subtotal": 3100000.0,
        "items": [{"sku": "PC-01", "qty": 1}, {"sku": "SSD-01", "qty": 2}],
    },
    {
        "id": "ORD-1006",
        "status": "cancelled",
        "subtotal": 1800000.0,
        "items": [{"sku": "PRN-01", "qty": 1}],
    },
    {
        "id": "ORD-1007",
        "status": "paid",
        "subtotal": 1750000.0,
        "items": [{"sku": "TAB-01", "qty": 1}],
    },
    {
        "id": "ORD-1008",
        "status": "refunded",
        "subtotal": 2400000.0,
        "items": [{"sku": "CAM-01", "qty": 2}],
    },
    {
        "id": "ORD-1009",
        "status": "paid",
        "subtotal": 720000.0,
        "items": [{"sku": "RAM-01", "qty": 2}],
    },
    {
        "id": "ORD-1010",
        "status": "paid",
        "subtotal": 5000000.0,
        "items": [{"sku": "SRV-01", "qty": 1}, {"sku": "UPS-01", "qty": 1}],
    },
)

is_paid = curry_filter_by("status")(COMPARATORS["eq"])("paid")
has_min_subtotal = curry_filter_by("subtotal")(COMPARATORS["gte"])(MIN_SUBTOTAL)
apply_member_discount = curry_transform_field("subtotal")("harga_diskon")(
    curry_rate_adjuster(-10)
)
add_ppn = curry_transform_field("harga_diskon")("ppn")(
    lambda discounted: round(discounted * 0.11, 2)
)
add_net_total = curry_transform_field("harga_diskon")("total_bersih")(
    curry_rate_adjuster(11)
)


def calculate_discounted_price(subtotal):
    """
    desc:
        Menghitung harga setelah diskon member 10 persen.

    pre-cond:
        subtotal berupa bilangan non-negatif.

    post-cond:
        Mengembalikan harga diskon yang dibulatkan dua angka desimal.
    """
    return round(curry_rate_adjuster(-10)(subtotal), 2)


@measure_time
def build_order_report(orders, min_subtotal):
    """
    desc:
        Menjalankan pipeline pesanan paid yang memenuhi ambang subtotal,
        menghitung harga diskon, PPN, total bersih, dan ringkasan omzet.

    pre-cond:
        orders berupa sequence record pesanan; min_subtotal bilangan.

    post-cond:
        Mengembalikan dictionary laporan tanpa mengubah dataset sumber.
    """
    eligible_filter = curry_filter_by("subtotal")(COMPARATORS["gte"])(min_subtotal)
    results = run_pipeline(
        orders,
        make_filter_step(is_paid),
        make_filter_step(eligible_filter),
        make_map_step(apply_member_discount),
        make_map_step(add_ppn),
        make_map_step(add_net_total),
    )
    paid_rows = make_filter_step(is_paid)(orders)
    return {
        "total_orders": recursive_length(orders),
        "paid_orders": recursive_length(paid_rows),
        "eligible_orders": recursive_length(results),
        "rows": results,
        "net_revenue": round(recursive_sum_field(results, "total_bersih"), 2),
    }


def verify_immutability(original, backup):
    """
    desc:
        Membuktikan dataset awal tidak berubah setelah pipeline dijalankan.

    pre-cond:
        original dan backup berupa struktur data yang dapat dibandingkan.

    post-cond:
        Mengembalikan True apabila keduanya memiliki nilai yang sama.
    """
    return original == backup


def format_report(report, duration_ms):
    """
    desc:
        Menyusun laporan terminal terstruktur dari hasil pipeline.

    pre-cond:
        report berisi kunci required dari build_order_report.

    post-cond:
        Mengembalikan string laporan lengkap tanpa melakukan I/O.
    """
    lines = [
        "=== APP 1: E-COMMERCE DYNAMIC PRICING & ORDER PIPELINE ===",
        f"Jumlah seluruh pesanan      : {report['total_orders']}",
        f"Jumlah pesanan paid         : {report['paid_orders']}",
        f"Transaksi lolos subtotal    : {report['eligible_orders']}",
        "",
        "Rincian harga (subtotal -> diskon 10% -> PPN 11%):",
    ]
    for row in report["rows"]:
        lines.append(
            f"  {row['id']}: {row['subtotal']:,.2f} -> "
            f"{row['harga_diskon']:,.2f} | PPN {row['ppn']:,.2f} | "
            f"Total {row['total_bersih']:,.2f}"
        )
    lines.extend(
        [
            "",
            f"Total omzet bersih          : {report['net_revenue']:,.2f}",
            f"Durasi eksekusi pipeline    : {duration_ms:.4f} ms",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    orders_backup = deepcopy(ORDERS)
    report_result, elapsed_ms = build_order_report(ORDERS, MIN_SUBTOTAL)

    assert verify_immutability(ORDERS, orders_backup)
    assert report_result["total_orders"] == 10
    assert report_result["paid_orders"] == 7
    assert report_result["eligible_orders"] == 6
    assert report_result["net_revenue"] == 12787200.0
    assert calculate_discounted_price(100000.0) == 90000.0

    print(format_report(report_result, elapsed_ms))
    print("Bukti immutability : assert ORDERS == orders_backup berhasil")
