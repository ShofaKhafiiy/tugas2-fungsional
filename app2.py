"""Aplikasi 2: IoT Telemetry & Sensor Anomaly Stream Analyzer."""

from copy import deepcopy
from itertools import islice

from fplib import (
    immutable_update_record,
    lazy_filter_stream,
    lazy_transform_stream,
    recursive_length,
    safe_execute,
)

THRESHOLDS = {"suhu": 37.5, "ldr": 800.0, "getaran": 0.6}
CRITICAL_FACTOR = 1.1
FIRST_N = 4

SENSOR_READINGS = (
    {
        "id": "R01",
        "sensor": "suhu",
        "nilai": 38.7,
        "satuan": "C",
        "info": {"node": "ESP-01", "rack": "A"},
    },
    {
        "id": "R02",
        "sensor": "suhu",
        "nilai": 36.4,
        "satuan": "C",
        "info": {"node": "ESP-01", "rack": "A"},
    },
    {
        "id": "R03",
        "sensor": "suhu",
        "nilai": 46.2,
        "satuan": "C",
        "info": {"node": "ESP-02", "rack": "B"},
    },
    {
        "id": "R04",
        "sensor": "ldr",
        "nilai": 950.0,
        "satuan": "lux",
        "info": {"node": "ESP-02", "rack": "B"},
    },
    {
        "id": "R05",
        "sensor": "ldr",
        "nilai": 320.0,
        "satuan": "lux",
        "info": {"node": "ESP-03", "rack": "C"},
    },
    {
        "id": "R06",
        "sensor": "getaran",
        "nilai": 0.82,
        "satuan": "g",
        "info": {"node": "ESP-03", "rack": "C"},
    },
    {
        "id": "R07",
        "sensor": "getaran",
        "nilai": 0.31,
        "satuan": "g",
        "info": {"node": "ESP-04", "rack": "D"},
    },
    {
        "id": "R08",
        "sensor": "suhu",
        "nilai": 39.1,
        "satuan": "C",
        "info": {"node": "ESP-04", "rack": "D"},
    },
    {
        "id": "R09",
        "sensor": "ldr",
        "nilai": 1200.0,
        "satuan": "lux",
        "info": {"node": "ESP-05", "rack": "E"},
    },
    {
        "id": "R10",
        "sensor": "getaran",
        "nilai": 0.55,
        "satuan": "g",
        "info": {"node": "ESP-05", "rack": "E"},
    },
    {
        "id": "R11",
        "sensor": "suhu",
        "nilai": None,
        "satuan": "C",
        "info": {"node": "ESP-06", "rack": "F"},
    },
    {
        "id": "R12",
        "sensor": "ldr",
        "satuan": "lux",
        "info": {"node": "ESP-06", "rack": "F"},
    },
    {
        "id": "R13",
        "sensor": "getaran",
        "nilai": "TINGGI",
        "satuan": "g",
        "info": {"node": "ESP-07", "rack": "G"},
    },
)

def is_above_threshold(reading):
    """
    desc:
        Menentukan apakah nilai pembacaan melebihi ambang untuk jenis sensor.

    pre-cond:
        reading memiliki kunci sensor dan nilai yang dapat dibandingkan.

    post-cond:
        Mengembalikan True jika nilai di atas ambang, False jika tidak.
    """
    return reading["nilai"] > THRESHOLDS[reading["sensor"]]


def is_valid_reading(reading):
    """
    desc:
        Menilai kelayakan pembacaan dengan menangkap kesalahan melalui safe_execute.

    pre-cond:
        reading berupa dictionary sensor.

    post-cond:
        Mengembalikan True hanya jika perbandingan ambang berhasil dijalankan.
    """
    return safe_execute(is_above_threshold, reading)["ok"]


def is_anomaly(reading):
    """
    desc:
        Predikat anomali yang aman terhadap data sensor korup atau hilang.

    pre-cond:
        reading berupa dictionary sensor.

    post-cond:
        Mengembalikan True hanya untuk pembacaan valid di atas ambang.
    """
    result = safe_execute(is_above_threshold, reading)
    return result["ok"] and result["data"] is True


def classify_severity(reading):
    """
    desc:
        Menambahkan klasifikasi tingkat bahaya secara immutable berdasarkan
        rasio nilai terhadap ambang sensor.

    pre-cond:
        reading merupakan pembacaan valid yang sudah terindikasi anomali.

    post-cond:
        Mengembalikan dictionary baru dengan field klasifikasi.
    """
    threshold = THRESHOLDS[reading["sensor"]]
    level = "KRITIS" if reading["nilai"] >= threshold * CRITICAL_FACTOR else "PERINGATAN"
    return immutable_update_record(reading, {"klasifikasi": level})


def corruption_report(readings):
    """
    desc:
        Mengumpulkan hasil safe_execute untuk seluruh pembacaan yang korup.

    pre-cond:
        readings berupa sequence dictionary sensor.

    post-cond:
        Mengembalikan list dictionary berisi status, error, dan fallback.
    """
    return [
        {
            "id": reading.get("id"),
            "ok": result["ok"],
            "error": result["error"],
            "fallback": result["data"],
        }
        for reading in readings
        if not is_valid_reading(reading)
        for result in [safe_execute(is_above_threshold, reading, fallback="TIDAK_VALID")]
    ]


def build_anomaly_report(readings, limit):
    """
    desc:
        Membangun laporan stream anomali secara lazy, mengambil hanya N data
        pertama, serta memeriksa data korup dengan safe_execute.

    pre-cond:
        readings berupa iterable dictionary; limit bilangan bulat positif.

    post-cond:
        Mengembalikan dictionary laporan tanpa mengubah dataset sumber.
    """
    anomaly_stream = lazy_filter_stream(readings, is_anomaly)
    classified_stream = lazy_transform_stream(anomaly_stream, classify_severity)
    first_anomalies = list(islice(classified_stream, limit))
    numeric_values = (row["nilai"] for row in first_anomalies)
    return {
        "raw_count": recursive_length(readings),
        "raw": list(readings),
        "anomalies": first_anomalies,
        "numeric_values": list(numeric_values),
        "corrupt": corruption_report(readings),
        "limit": limit,
    }


def verify_immutability(original, backup):
    """
    desc:
        Membuktikan dataset sensor awal tidak berubah setelah analisis stream.

    pre-cond:
        original dan backup dapat dibandingkan nilai.

    post-cond:
        Mengembalikan True apabila keduanya identik dalam nilai.
    """
    return original == backup


def format_report(report):
    """
    desc:
        Menyusun tampilan terminal untuk hasil analisis sensor.

    pre-cond:
        report berasal dari build_anomaly_report.

    post-cond:
        Mengembalikan string laporan tanpa efek I/O.
    """
    lines = [
        "=== APP 2: IOT TELEMETRY & SENSOR ANOMALY STREAM ANALYZER ===",
        f"Jumlah pembacaan mentah       : {report['raw_count']}",
        "Data sensor mentah:",
    ]
    for row in report["raw"]:
        lines.append(f"  {row['id']:>5} | {row['sensor']:<8} | nilai={row.get('nilai')!r}")
    lines.extend(
        [
            "",
            f"Anomali pertama (N={report['limit']}, stream tidak dihabiskan):",
        ]
    )
    for row in report["anomalies"]:
        lines.append(
            f"  {row['id']} | {row['sensor']} | {row['nilai']} {row['satuan']} "
            f"| {row['klasifikasi']} | node={row['info']['node']}"
        )
    lines.append(f"Generator expression -> nilai numerik: {report['numeric_values']}")
    lines.extend(["", "Pengujian data korup / hilang dengan safe_execute():"])
    for row in report["corrupt"]:
        lines.append(f"  {row['id']}: ok={row['ok']} | error={row['error']} | fallback={row['fallback']!r}")
    return "\n".join(lines)


if __name__ == "__main__":
    readings_backup = deepcopy(SENSOR_READINGS)
    sensor_report = build_anomaly_report(SENSOR_READINGS, FIRST_N)

    assert verify_immutability(SENSOR_READINGS, readings_backup)
    assert sensor_report["raw_count"] == 13
    assert [row["id"] for row in sensor_report["anomalies"]] == ["R01", "R03", "R04", "R06"]
    assert sensor_report["numeric_values"] == [38.7, 46.2, 950.0, 0.82]
    assert len(sensor_report["corrupt"]) == 3
    assert all(row["ok"] is False for row in sensor_report["corrupt"])

    print(format_report(sensor_report))
    print("Bukti immutability : assert SENSOR_READINGS == readings_backup berhasil")
