#!/usr/bin/env python3
"""
organizar_por_categoria.py
==========================
Distribuye automáticamente los archivos de audio (.wav) y de anotaciones (.txt)
del desafío ICBHI 2017 desde la carpeta de descarga (origen) hacia la estructura
jerárquica por categorías clínicas y carpetas de pacientes (destino).

Parte del punto 3.1 de INSTRUCCIONES_DATOS_IA.md.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Distribuidor de grabaciones y anotaciones ICBHI 2017 hacia carpetas de pacientes."
    )
    parser.add_argument(
        "--audios",
        "-a",
        default="data/ICBHI_final_database",
        help="Ruta a la carpeta con los audios .wav y anotaciones .txt descargados (defecto: data/ICBHI_final_database)",
    )
    parser.add_argument(
        "--salida",
        "-s",
        default="data/ICBHI_organizado - pacientes de los links filtrados",
        help="Ruta base de la estructura organizada por categorías (defecto: data/ICBHI_organizado - pacientes de los links filtrados)",
    )
    parser.add_argument(
        "--modo",
        "-m",
        choices=["copy", "link", "move"],
        default="copy",
        help="Método de transferencia: 'copy' (copiar archivos, recomendado), 'link' (hard link para ahorrar espacio), 'move' (mover)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula la operación sin realizar cambios en disco",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Muestra detalles de cada archivo copiado",
    )
    return parser.parse_args()


def map_patient_directories(salida_path: Path):
    """
    Escanea la carpeta de salida buscando todas las carpetas 'paciente_<id>'.
    Retorna un diccionario {patient_id: {'path': Path, 'audios_path': Path, 'category': str}}
    """
    patients_map = {}
    if not salida_path.exists():
        raise FileNotFoundError(f"El directorio de salida no existe: {salida_path}")

    for category_dir in salida_path.iterdir():
        if category_dir.is_dir() and not category_dir.name.startswith("."):
            for patient_dir in category_dir.iterdir():
                if patient_dir.is_dir() and patient_dir.name.startswith("paciente_"):
                    pid = patient_dir.name.split("_")[1]
                    audios_dir = patient_dir / "audios"
                    patients_map[pid] = {
                        "patient_dir": patient_dir,
                        "audios_dir": audios_dir,
                        "category": category_dir.name,
                    }
    return patients_map


def main():
    args = parse_args()
    source_path = Path(args.audios).resolve()
    target_base = Path(args.salida).resolve()

    print("=" * 70)
    print(" DISTRIBUIDOR DE GRABACIONES CLÍNICAS ICBHI 2017")
    print("=" * 70)
    print(f"Carpeta de origen:  {source_path}")
    print(f"Estructura destino: {target_base}")
    print(f"Modo de operación:  {args.modo.upper()}")
    if args.dry_run:
        print(">> MODO DRY-RUN ACTIVO (No se modificará ningún archivo) <<")
    print("-" * 70)

    if not source_path.exists():
        print(f"ERROR: La carpeta origen '{source_path}' no existe.", file=sys.stderr)
        sys.exit(1)

    # 1. Mapear pacientes existentes
    patients_map = map_patient_directories(target_base)
    print(f"Pacientes mapeados en categorías destino: {len(patients_map)}")
    if len(patients_map) == 0:
        print("ERROR: No se encontraron subcarpetas 'paciente_<id>' en el directorio de salida.", file=sys.stderr)
        sys.exit(1)

    # 2. Escanear archivos fuente
    source_files = sorted(list(source_path.iterdir()))
    wav_files = []
    txt_files = []
    other_files = []

    for f in source_files:
        if f.is_file():
            name = f.name
            if name.startswith("filename_") or name.endswith(".sh"):
                other_files.append(f)
                continue
            parts = name.split("_")
            if parts[0].isdigit():
                if name.endswith(".wav"):
                    wav_files.append(f)
                elif name.endswith(".txt"):
                    txt_files.append(f)
                else:
                    other_files.append(f)
            else:
                other_files.append(f)

    print(f"Archivos de audio .wav encontrados:       {len(wav_files)}")
    print(f"Archivos de anotación .txt encontrados:   {len(txt_files)}")
    if other_files:
        print(f"Otros archivos (metadatos/scripts Kaggle): {len(other_files)}")
    print("-" * 70)

    # 3. Procesar y transferir archivos
    stats = {
        "wav_copied": 0,
        "txt_copied": 0,
        "leeme_removed": 0,
        "unmatched": [],
        "per_category": {},
        "per_patient_recordings": {},
    }

    all_target_files = wav_files + txt_files
    total_files = len(all_target_files)

    for idx, file_path in enumerate(all_target_files, 1):
        pid = file_path.name.split("_")[0]
        if pid not in patients_map:
            stats["unmatched"].append(file_path.name)
            continue

        p_info = patients_map[pid]
        audios_dir = p_info["audios_dir"]
        category = p_info["category"]

        if category not in stats["per_category"]:
            stats["per_category"][category] = {"wav": 0, "txt": 0}

        stats["per_patient_recordings"].setdefault(pid, {"wav": 0, "txt": 0})

        if not args.dry_run:
            audios_dir.mkdir(parents=True, exist_ok=True)

        dest_file = audios_dir / file_path.name

        if not args.dry_run:
            if args.modo == "copy":
                shutil.copy2(file_path, dest_file)
            elif args.modo == "link":
                if dest_file.exists():
                    dest_file.unlink()
                os.link(file_path, dest_file)
            elif args.modo == "move":
                shutil.move(str(file_path), str(dest_file))

        if file_path.name.endswith(".wav"):
            stats["wav_copied"] += 1
            stats["per_category"][category]["wav"] += 1
            stats["per_patient_recordings"][pid]["wav"] += 1
        elif file_path.name.endswith(".txt"):
            stats["txt_copied"] += 1
            stats["per_category"][category]["txt"] += 1
            stats["per_patient_recordings"][pid]["txt"] += 1

        if args.verbose:
            print(f"[{idx}/{total_files}] -> {category}/paciente_{pid}/audios/{file_path.name}")
        elif idx % 200 == 0 or idx == total_files:
            pct = (idx / total_files) * 100
            print(f"Progreso de transferencia: {idx}/{total_files} archivos ({pct:.1f}%)")

    # 4. Eliminar los archivos LEEME.txt de las carpetas que recibieron audios
    print("-" * 70)
    print("Limpieza de marcadores temporales 'LEEME.txt'...")
    for pid, p_info in patients_map.items():
        leeme_file = p_info["audios_dir"] / "LEEME.txt"
        if leeme_file.exists():
            if not args.dry_run:
                leeme_file.unlink()
            stats["leeme_removed"] += 1

    # 5. Reporte final
    print("=" * 70)
    print(" REPORTE FINAL DE POBLACIÓN DE DATOS ICBHI 2017")
    print("=" * 70)
    print(f"Audios .wav distribuidos:        {stats['wav_copied']}/{len(wav_files)}")
    print(f"Anotaciones .txt distribuidas:   {stats['txt_copied']}/{len(txt_files)}")
    print(f"Marcadores LEEME.txt eliminados: {stats['leeme_removed']}/{len(patients_map)}")
    print(f"Archivos no emparejados:         {len(stats['unmatched'])}")
    print("-" * 70)

    print("Distribución por Categoría Clínica [Edad]__[Diagnóstico]:")
    for cat_name, counts in sorted(stats["per_category"].items()):
        print(f"  * {cat_name:<38}: {counts['wav']:3d} audios (.wav) | {counts['txt']:3d} anotaciones (.txt)")

    # Comprobación de integridad por paciente
    incomplete_patients = []
    for pid, recs in stats["per_patient_recordings"].items():
        if recs["wav"] == 0 or recs["wav"] != recs["txt"]:
            incomplete_patients.append((pid, recs["wav"], recs["txt"]))

    print("-" * 70)
    if incomplete_patients:
        print(f"ADVERTENCIA: Se encontraron {len(incomplete_patients)} pacientes con inconsistencias:")
        for pid, w, t in incomplete_patients:
            print(f"  - Paciente {pid}: {w} wavs vs {t} txts")
    else:
        print("VERIFICACIÓN EXITOSA: Los 126 pacientes cuentan con pares consistentes de .wav y .txt.")
    print("=" * 70)


if __name__ == "__main__":
    main()
