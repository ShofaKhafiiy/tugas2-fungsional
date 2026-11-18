"""Aplikasi 4: Server Log Audit & Security Incident Filter."""

from copy import deepcopy

from fplib import (
    COMPARATORS,
    add_values,
    curry_filter_by,
    immutable_update_record,
    make_filter_step,
    make_map_step,
    make_reduce_step,
    run_pipeline,
)

SENSITIVE_PATHS = ("/admin", "/internal", "/config")

HTTP_LOGS = (
    {
        "id": "L01",
        "ip": "192.168.1.10",
        "method": "GET",
        "path": "/api/products",
        "status": 200,
        "latency_ms": 45,
        "headers": {"user_agent": "Mozilla/5.0", "referer": "-"},
    },
    {
        "id": "L02",
        "ip": "10.0.0.21",
        "method": "POST",
        "path": "/api/orders",
        "status": 201,
        "latency_ms": 120,
        "headers": {"user_agent": "MobileApp/2.1", "referer": "-"},
    },
    {
        "id": "L03",
        "ip": "172.16.4.7",
        "method": "GET",
        "path": "/admin/dashboard",
        "status": 403,
        "latency_ms": 310,
        "headers": {"user_agent": "curl/8.0", "referer": "/login"},
    },
    {
        "id": "L04",
        "ip": "192.168.1.44",
        "method": "GET",
        "path": "/api/users",
        "status": 200,
        "latency_ms": 88,
        "headers": {"user_agent": "Mozilla/5.0", "referer": "-"},
    },
    {
        "id": "L05",
        "ip": "172.16.4.9",
        "method": "DELETE",
        "path": "/admin/users/12",
        "status": 401,
        "latency_ms": 240,
        "headers": {"user_agent": "python-requests", "referer": "/admin"},
    },
    {
        "id": "L06",
        "ip": "203.0.113.55",
        "method": "GET",
        "path": "/internal/config",
        "status": 500,
        "latency_ms": 980,
        "headers": {"user_agent": "curl/8.0", "referer": "-"},
    },
    {
        "id": "L07",
        "ip": "10.0.0.77",
        "method": "POST",
        "path": "/api/login",
        "status": 400,
        "latency_ms": 65,
        "headers": {"user_agent": "MobileApp/2.1", "referer": "/login"},
    },
    {
        "id": "L08",
        "ip": "192.168.1.90",
        "method": "GET",
        "path": "/public/home",
        "status": 200,
        "latency_ms": 33,
        "headers": {"user_agent": "Mozilla/5.0", "referer": "-"},
    },
    {
        "id": "L09",
        "ip": "172.16.4.11",
        "method": "GET",
        "path": "/admin/reports",
        "status": 200,
        "latency_ms": 410,
        "headers": {"user_agent": "Mozilla/5.0", "referer": "/admin"},
    },
    {
        "id": "L10",
        "ip": "203.0.113.80",
        "method": "PUT",
        "path": "/api/orders/9",
        "status": 502,
        "latency_ms": 760,
        "headers": {"user_agent": "curl/8.0", "referer": "-"},
    },
    {
        "id": "L11",
        "ip": "192.0.2.14",
        "method": "GET",
        "path": "/config/secrets",
        "status": 404,
        "latency_ms": 190,
        "headers": {"user_agent": "python-requests", "referer": "/"},
    },
    {
        "id": "L12",
        "ip": "10.0.0.99",
        "method": "GET",
        "path": "/api/health",
        "status": 200,
        "latency_ms": 12,
        "headers": {"user_agent": "Monitoring/1.0", "referer": "-"},
    },
)

is_error = curry_filter_by("status")(COMPARATORS["gte"])(400)
sensitive_predicates = tuple(
    curry_filter_by("path")(COMPARATORS["contains"])(path) for path in SENSITIVE_PATHS
)


def and_predicates(left):
    """
    desc:
        Menyusun dua predikat curried menjadi satu predikat AND.

    pre-cond:
        left dan right berupa fungsi predikat record -> bool.

    post-cond:
        Mengembalikan predikat baru yang bernilai True jika keduanya benar.
    """

    def right_stage(right):
        """
        desc:
            Menyimpan predikat kanan ke dalam closure.

        pre-cond:
            right berupa callable satu argumen.

        post-cond:
            Mengembalikan fungsi predikat gabungan.
        """

        def combined(record):
            """
            desc:
                Menggabungkan hasil kedua predikat dengan operator AND.

            pre-cond:
                record berupa dictionary log.

            post-cond:
                Mengembalikan boolean tanpa mengubah record.
            """
            return left(record) and right(record)

        return combined

    return right_stage


def or_predicates(left):
    """
    desc:
        Menyusun dua predikat curried menjadi satu predikat OR.

    pre-cond:
        left dan right berupa fungsi predikat record -> bool.

    post-cond:
        Mengembalikan predikat baru yang bernilai True jika salah satu benar.
    """

    def right_stage(right):
        """
        desc:
            Menyimpan predikat kanan ke dalam closure.

        pre-cond:
            right berupa callable satu argumen.

        post-cond:
            Mengembalikan fungsi predikat gabungan.
        """

        def combined(record):
            """
            desc:
                Menggabungkan hasil kedua predikat dengan operator OR.

            pre-cond:
                record berupa dictionary log.

            post-cond:
                Mengembalikan boolean tanpa mengubah record.
            """
            return left(record) or right(record)

        return combined

    return right_stage


def combine_any(predicates):
    """
    desc:
        Menggabungkan banyak predikat menjadi satu predikat OR secara rekursif
        melalui komposisi curried or_predicates.

    pre-cond:
        predicates berupa sequence predikat nonempty.

    post-cond:
        Mengembalikan satu predikat gabungan.
    """

    def combine(remaining, accumulator):
        """
        desc:
            Melipat sisa predikat ke dalam akumulator predikat OR.

        pre-cond:
            remaining berupa sequence predikat; accumulator berupa predikat.

        post-cond:
            Mengembalikan predikat akhir hasil komposisi.
        """
        try:
            head = remaining[0]
        except IndexError:
            return accumulator
        else:
            return combine(remaining[1:], or_predicates(accumulator)(head))

    return combine(predicates[1:], predicates[0])


is_sensitive = combine_any(sensitive_predicates)
is_incident = and_predicates(is_error)(is_sensitive)


def mask_ip_address(log):
    """
    desc:
        Menyembunyikan dua oktet terakhir alamat IP secara immutable.

    pre-cond:
        log memiliki field ip berformat IPv4 empat oktet.

    post-cond:
        Mengembalikan dictionary baru dengan ip termasker dan flag masked.
    """
    octets = log["ip"].split(".")
    masked_ip = ".".join([octets[0], octets[1], "xxx", "xxx"])
    return immutable_update_record(log, {"ip": masked_ip, "masked": True})


def extract_latency(log):
    """
    desc:
        Mengambil nilai latency_ms dari sebuah log.

    pre-cond:
        log memiliki kunci latency_ms bernilai numerik.

    post-cond:
        Mengembalikan nilai latensi tanpa efek samping.
    """
    return log["latency_ms"]


def build_audit_report(logs):
    """
    desc:
        Menyusun audit log error, endpoint sensitif, insiden, hasil masking,
        dan total latensi insiden dengan pipeline deklaratif.

    pre-cond:
        logs berupa sequence dictionary log HTTP.

    post-cond:
        Mengembalikan dictionary laporan tanpa mengubah data log asli.
    """
    error_logs = run_pipeline(logs, make_filter_step(is_error))
    sensitive_logs = run_pipeline(logs, make_filter_step(is_sensitive))
    incident_logs = run_pipeline(logs, make_filter_step(is_incident))
    masked_logs = run_pipeline(incident_logs, make_map_step(mask_ip_address))
    total_latency = run_pipeline(
        logs,
        make_filter_step(is_error),
        make_filter_step(is_sensitive),
        make_map_step(extract_latency),
        make_reduce_step(add_values, 0),
    )
    return {
        "logs": logs,
        "error_logs": error_logs,
        "sensitive_logs": sensitive_logs,
        "incident_logs": incident_logs,
        "masked_logs": masked_logs,
        "total_latency": total_latency,
    }


def verify_immutability(original, backup):
    """
    desc:
        Membuktikan log asli tidak berubah setelah audit dan masking.

    pre-cond:
        original dan backup dapat dibandingkan nilainya.

    post-cond:
        Mengembalikan True apabila kedua dataset identik.
    """
    return original == backup


def format_report(report):
    """
    desc:
        Menyusun tampilan terminal untuk hasil audit log.

    pre-cond:
        report berasal dari build_audit_report.

    post-cond:
        Mengembalikan string laporan tanpa I/O.
    """
    lines = [
        "=== APP 4: SERVER LOG AUDIT & SECURITY INCIDENT FILTER ===",
        f"Data log HTTP ({len(report['logs'])} entri):",
    ]
    for log in report["logs"]:
        lines.append(
            f"  {log['id']} | {log['method']:<6} {log['path']:<22} "
            f"| {log['status']} | {log['latency_ms']} ms"
        )
    lines.extend(
        [
            "",
            f"Log dengan status error (>=400): {len(report['error_logs'])} entri",
        ]
    )
    for log in report["error_logs"]:
        lines.append(f"  {log['id']} | {log['status']} | {log['path']}")
    lines.extend(
        [
            "",
            f"Endpoint sensitif: {len(report['sensitive_logs'])} entri",
        ]
    )
    for log in report["sensitive_logs"]:
        lines.append(f"  {log['id']} | {log['path']}")
    lines.extend(["", "Hasil masking IP pada insiden (error DAN sensitif):"])
    for log in report["masked_logs"]:
        lines.append(
            f"  {log['id']} | {log['ip']:<18} | {log['path']} "
            f"| masked={log['masked']}"
        )
    lines.extend(
        [
            "",
            f"Total latensi insiden (reduce + add_values) : {report['total_latency']} ms",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    logs_backup = deepcopy(HTTP_LOGS)
    audit_report = build_audit_report(HTTP_LOGS)

    assert verify_immutability(HTTP_LOGS, logs_backup)
    assert len(audit_report["error_logs"]) == 6
    assert len(audit_report["sensitive_logs"]) == 5
    assert [row["id"] for row in audit_report["incident_logs"]] == ["L03", "L05", "L06", "L11"]
    assert all(row["masked"] for row in audit_report["masked_logs"])
    assert audit_report["total_latency"] == 1720
    assert HTTP_LOGS[2]["ip"] == "172.16.4.7"

    print(format_report(audit_report))
    print("Bukti immutability : assert HTTP_LOGS == logs_backup berhasil")
