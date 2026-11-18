"""Aplikasi 3: Academic Gradebook & Scholarship Eligibility Evaluator."""

from copy import deepcopy

from fplib import (
    COMPARATORS,
    curry_filter_by,
    immutable_update_record,
    make_filter_step,
    make_map_step,
    recursive_length,
    recursive_sum,
    recursive_sum_field,
    run_pipeline,
    safe_execute,
    validate_non_empty,
)

MIN_IPK = 3.5
ACTIVE_STATUS = "aktif"

WEIGHTS = {
    "tugas": lambda score: (score / 25) * 0.30,
    "uts": lambda score: (score / 25) * 0.30,
    "uas": lambda score: (score / 25) * 0.40,
}

STUDENTS = (
    {
        "nim": "202410370110276",
        "nama": "Shofa Khafidin",
        "status": "aktif",
        "nilai": {"tugas": 92, "uts": 88, "uas": 94},
    },
    {
        "nim": "202410370110249",
        "nama": "Istigfaro Choirul Rijal",
        "status": "aktif",
        "nilai": {"tugas": 85, "uts": 90, "uas": 86},
    },
    {
        "nim": "202410370110253",
        "nama": "Dafa Setya Oriendra",
        "status": "aktif",
        "nilai": {"tugas": 90, "uts": 92, "uas": 95},
    },
    {
        "nim": "202410370110231",
        "nama": "Muhammad Iqbal Habibi",
        "status": "aktif",
        "nilai": {"tugas": 78, "uts": 80, "uas": 82},
    },
    {
        "nim": "202410370110631",
        "nama": "Azril Maulana Azhar",
        "status": "nonaktif",
        "nilai": {"tugas": 95, "uts": 94, "uas": 96},
    },
    {
        "nim": "202410370110226",
        "nama": "Chraitong Pranadipa Mardjun",
        "status": "aktif",
        "nilai": {"tugas": 88, "uts": 85, "uas": 87},
    },
    {
        "nim": "202410370110301",
        "nama": "Dewi Anggraini",
        "status": "aktif",
        "nilai": {"tugas": 91, "uts": 89, "uas": 92},
    },
    {
        "nim": "202410370110302",
        "nama": "Eko Prasetyo",
        "status": "aktif",
        "nilai": {"tugas": 70, "uts": 75, "uas": 72},
    },
    {
        "nim": "202410370110303",
        "nama": "Fajar Ramadhan",
        "status": "nonaktif",
        "nilai": {"tugas": 89, "uts": 91, "uas": 90},
    },
    {
        "nim": "202410370110304",
        "nama": "Gita Permata",
        "status": "aktif",
        "nilai": {"tugas": 84, "uts": 83, "uas": 85},
    },
)

has_min_ipk = curry_filter_by("ipk")(COMPARATORS["gte"])(MIN_IPK)
is_active = curry_filter_by("status")(COMPARATORS["eq"])(ACTIVE_STATUS)


def calculate_ipk(student):
    """
    desc:
        Menghitung IPK dari bobot first-class function yang tersimpan
        di WEIGHTS, lalu menjumlahkannya secara rekursif.

    pre-cond:
        student memiliki field nilai dengan kunci tugas, uts, dan uas.

    post-cond:
        Mengembalikan IPK dua angka desimal dalam skala 0.00 sampai 4.00.
    """
    weighted_scores = [
        WEIGHTS[component](student["nilai"][component])
        for component in ("tugas", "uts", "uas")
    ]
    return round(recursive_sum(weighted_scores), 2)


def enrich_with_ipk(student):
    """
    desc:
        Menambahkan field ipk ke salinan record mahasiswa.

    pre-cond:
        student memiliki data nilai yang valid.

    post-cond:
        Mengembalikan dictionary baru tanpa mengubah record asli.
    """
    return immutable_update_record(student, {"ipk": calculate_ipk(student)})


@validate_non_empty
def build_scholarship_report(students):
    """
    desc:
        Menghitung IPK seluruh mahasiswa, menyaring kandidat aktif dengan
        IPK minimal, lalu menghitung rata-rata IPK kandidat secara rekursif.

    pre-cond:
        students berupa sequence mahasiswa yang tidak kosong.

    post-cond:
        Mengembalikan dictionary laporan; dataset asli tidak dimodifikasi.
    """
    scored = run_pipeline(students, make_map_step(enrich_with_ipk))
    candidates = run_pipeline(
        scored,
        make_filter_step(has_min_ipk),
        make_filter_step(is_active),
    )
    candidate_count = recursive_length(candidates)
    total_ipk = recursive_sum_field(candidates, "ipk")
    return {
        "students": scored,
        "candidates": candidates,
        "candidate_count": candidate_count,
        "average_ipk": round(total_ipk / candidate_count, 2) if candidate_count else 0.0,
    }


def verify_immutability(original, backup):
    """
    desc:
        Membuktikan dataset mahasiswa tidak berubah setelah evaluasi.

    pre-cond:
        original dan backup dapat dibandingkan nilainya.

    post-cond:
        Mengembalikan True apabila kedua dataset identik.
    """
    return original == backup


def format_report(report, empty_check):
    """
    desc:
        Menyusun keluaran terminal untuk gradebook dan seleksi beasiswa.

    pre-cond:
        report berasal dari build_scholarship_report dan empty_check dari
        safe_execute terhadap dataset kosong.

    post-cond:
        Mengembalikan string laporan tanpa I/O.
    """
    lines = [
        "=== APP 3: ACADEMIC GRADEBOOK & SCHOLARSHIP ELIGIBILITY ===",
        "Daftar mahasiswa dan nilai akademik:",
    ]
    for student in report["students"]:
        nilai = student["nilai"]
        lines.append(
            f"  {student['nim']} | {student['nama']:<28} | "
            f"T={nilai['tugas']} UTS={nilai['uts']} UAS={nilai['uas']} "
            f"-> IPK {student['ipk']:.2f} | {student['status']}"
        )
    lines.extend(["", "Kandidat beasiswa (IPK >= 3.50 dan status aktif):"])
    for student in report["candidates"]:
        lines.append(f"  {student['nim']} | {student['nama']} | IPK {student['ipk']:.2f}")
    lines.extend(
        [
            "",
            f"Jumlah kandidat lolos          : {report['candidate_count']}",
            f"Rata-rata IPK kandidat         : {report['average_ipk']:.2f}",
            "",
            f"Validasi dataset kosong        : ok={empty_check['ok']}",
            f"Pesan error validator          : {empty_check['error']}",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    students_backup = deepcopy(STUDENTS)
    scholarship_report = build_scholarship_report(STUDENTS)
    empty_dataset_check = safe_execute(build_scholarship_report, ())

    assert verify_immutability(STUDENTS, students_backup)
    assert scholarship_report["candidate_count"] == 3
    assert scholarship_report["average_ipk"] == 3.66
    assert [row["nim"] for row in scholarship_report["candidates"]] == [
        "202410370110276",
        "202410370110253",
        "202410370110301",
    ]
    assert empty_dataset_check["ok"] is False
    assert "kosong" in empty_dataset_check["error"]

    print(format_report(scholarship_report, empty_dataset_check))
    print("Bukti immutability : assert STUDENTS == students_backup berhasil")
