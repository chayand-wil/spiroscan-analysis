"""
Módulo de Evaluación Clínica de Modelos Biomédicos
Proyecto: Sistema Embebido para Captura y Análisis de Señales Cardiorrespiratorias (f tecno 2026)
"""

from typing import Dict, List, Optional, Union
import numpy as np


def compute_icbhi_metrics(
    y_true: Union[np.ndarray, List[int]],
    y_pred: Union[np.ndarray, List[int]],
    class_names: Optional[List[str]] = None
) -> Dict[str, Union[float, np.ndarray, str]]:
    """
    Calcula las métricas clínicas obligatorias de acuerdo con la convención del desafío ICBHI:
    1. Sensibilidad (Sensitivity / Recall): Capacidad de detectar la presencia de anomalías.
    2. Especificidad (Specificity): Capacidad de confirmar ciclos respiratorios normales.
    3. Score ICBHI: Media aritmética entre Sensibilidad y Especificidad:
       Score = (Se + Sp) / 2
    4. Matriz de confusión y F1-Score Macro.
    """
    from sklearn.metrics import confusion_matrix, classification_report, f1_score
    
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    unique_classes = np.unique(np.concatenate([y_true, y_pred]))
    cm = confusion_matrix(y_true, y_pred, labels=unique_classes)
    
    # Caso Binario (0: Normal, 1: Patológico)
    if len(unique_classes) == 2 and 0 in unique_classes and 1 in unique_classes:
        tn, fp, fn, tp = cm.ravel()
        se = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        sp = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
        icbhi_score = float((se + sp) / 2.0)
        f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
        
        return {
            "sensitivity": se,
            "specificity": sp,
            "icbhi_score": icbhi_score,
            "f1_macro": f1_macro,
            "confusion_matrix": cm,
            "classification_report": classification_report(y_true, y_pred, zero_division=0)
        }
        
    # Caso Multiclase (ej. 4 clases: 0: Normal, 1: Crackles, 2: Wheezes, 3: Both)
    # En multiclase ICBHI:
    # - Clase 0 se considera 'Normal'
    # - Clases 1, 2, 3 se consideran 'Anormales'
    is_true_abnormal = (y_true > 0).astype(int)
    is_pred_abnormal = (y_pred > 0).astype(int)
    
    bin_cm = confusion_matrix(is_true_abnormal, is_pred_abnormal, labels=[0, 1])
    tn, fp, fn, tp = bin_cm.ravel()
    
    se = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    sp = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    icbhi_score = float((se + sp) / 2.0)
    f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    
    return {
        "sensitivity": se,
        "specificity": sp,
        "icbhi_score": icbhi_score,
        "f1_macro": f1_macro,
        "confusion_matrix": cm,
        "binary_confusion_matrix": bin_cm,
        "classification_report": classification_report(y_true, y_pred, target_names=class_names, zero_division=0)
    }


def print_clinical_report(metrics: Dict[str, Union[float, np.ndarray, str]], title: str = "RESULTADOS CLÍNICOS DEL MODELO"):
    """
    Imprime un informe formateado con las métricas médicas requeridas para la materia.
    """
    print("=" * 65)
    print(f"   {title}")
    print("=" * 65)
    print(f"• Sensibilidad (Se / Recall Anomalías): {metrics['sensitivity'] * 100:6.2f}%")
    print(f"• Especificidad (Sp / Detección Sano):  {metrics['specificity'] * 100:6.2f}%")
    print(f"• SCORE OFICIAL ICBHI ((Se + Sp) / 2):  {metrics['icbhi_score'] * 100:6.2f}%")
    print(f"• F1-Score Macro:                       {metrics['f1_macro'] * 100:6.2f}%")
    print("-" * 65)
    print("MATRIZ DE CONFUSIÓN:")
    print(metrics["confusion_matrix"])
    print("-" * 65)
    print("REPORTE DETALLADO POR CLASE:")
    print(metrics["classification_report"])
    print("=" * 65)
