"""
Service de gestion des alertes.

Auteur: Alsény Camara
Version: 1.0
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.medicament import Medicament
from database.medicament_repository import MedicamentRepository
from config import STOCK_CONFIG


class AlertType(Enum):
    """Types d'alertes."""
    LOW_STOCK = "low_stock"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    OUT_OF_STOCK = "out_of_stock"


class AlertSeverity(Enum):
    """Niveaux de sévérité des alertes."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Représente une alerte."""
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    medicament: Medicament
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            'type': self.alert_type.value,
            'severity': self.severity.value,
            'title': self.title,
            'message': self.message,
            'medicament_id': self.medicament.id,
            'medicament_code': self.medicament.code,
            'medicament_name': self.medicament.name
        }


class AlertService:
    """
    Service de détection et gestion des alertes.
    
    Responsabilités:
    - Détection des stocks faibles
    - Détection des péremptions proches
    - Génération des alertes
    """
    
    def __init__(self):
        """Initialise le service."""
        self._medicament_repo = MedicamentRepository()
    
    def get_all_alerts(self) -> List[Alert]:
        """
        Récupère toutes les alertes actives.
        
        Returns:
            List[Alert]: Liste des alertes triées par sévérité
        """
        alerts = []
        
        # Alertes de stock
        alerts.extend(self._get_stock_alerts())
        
        # Alertes de péremption
        alerts.extend(self._get_expiration_alerts())
        
        # Trier par sévérité (critical first)
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.WARNING: 1,
            AlertSeverity.INFO: 2
        }
        
        alerts.sort(key=lambda a: severity_order.get(a.severity, 99))
        
        return alerts
    
    def _get_stock_alerts(self) -> List[Alert]:
        """Génère les alertes de stock."""
        alerts = []
        
        low_stock_meds = self._medicament_repo.get_low_stock()
        critical_threshold = STOCK_CONFIG.get("low_stock_critical_threshold", 5)
        
        for med in low_stock_meds:
            if med.quantity_in_stock == 0:
                # Rupture de stock
                alerts.append(Alert(
                    alert_type=AlertType.OUT_OF_STOCK,
                    severity=AlertSeverity.CRITICAL,
                    title="Rupture de stock",
                    message=f"{med.name} est en rupture de stock",
                    medicament=med
                ))
            elif med.quantity_in_stock <= critical_threshold:
                # Stock critique
                alerts.append(Alert(
                    alert_type=AlertType.LOW_STOCK,
                    severity=AlertSeverity.CRITICAL,
                    title="Stock critique",
                    message=f"{med.name}: seulement {med.quantity_in_stock} unité(s)",
                    medicament=med
                ))
            else:
                # Stock faible
                alerts.append(Alert(
                    alert_type=AlertType.LOW_STOCK,
                    severity=AlertSeverity.WARNING,
                    title="Stock faible",
                    message=f"{med.name}: {med.quantity_in_stock} unité(s) (seuil: {med.stock_threshold})",
                    medicament=med
                ))
        
        return alerts
    
    def _get_expiration_alerts(self) -> List[Alert]:
        """Génère les alertes de péremption."""
        alerts = []
        
        # Médicaments expirés
        expired = self._medicament_repo.get_expired()
        for med in expired:
            alerts.append(Alert(
                alert_type=AlertType.EXPIRED,
                severity=AlertSeverity.CRITICAL,
                title="Produit périmé",
                message=f"{med.name} est périmé depuis le {med.expiration_date}",
                medicament=med
            ))
        
        # Médicaments expirant bientôt
        expiring_days = STOCK_CONFIG.get("expiry_alert_days", 30)
        expiring = self._medicament_repo.get_expiring_soon(expiring_days)
        
        for med in expiring:
            days = med.days_until_expiry()
            
            if days <= 7:
                severity = AlertSeverity.CRITICAL
                title = "Péremption imminente"
            elif days <= 15:
                severity = AlertSeverity.WARNING
                title = "Péremption proche"
            else:
                severity = AlertSeverity.INFO
                title = "Péremption à surveiller"
            
            alerts.append(Alert(
                alert_type=AlertType.EXPIRING_SOON,
                severity=severity,
                title=title,
                message=f"{med.name} expire dans {days} jour(s) ({med.expiration_date})",
                medicament=med
            ))
        
        return alerts
    
    def get_alerts_count(self) -> Dict[str, int]:
        """
        Retourne le compte des alertes par type.
        
        Returns:
            dict: Compteurs par type et total
        """
        alerts = self.get_all_alerts()
        
        counts = {
            'total': len(alerts),
            'critical': 0,
            'warning': 0,
            'info': 0,
            'low_stock': 0,
            'expiring': 0,
            'expired': 0,
            'out_of_stock': 0
        }
        
        for alert in alerts:
            # Par sévérité
            if alert.severity == AlertSeverity.CRITICAL:
                counts['critical'] += 1
            elif alert.severity == AlertSeverity.WARNING:
                counts['warning'] += 1
            else:
                counts['info'] += 1
            
            # Par type
            if alert.alert_type == AlertType.LOW_STOCK:
                counts['low_stock'] += 1
            elif alert.alert_type == AlertType.EXPIRING_SOON:
                counts['expiring'] += 1
            elif alert.alert_type == AlertType.EXPIRED:
                counts['expired'] += 1
            elif alert.alert_type == AlertType.OUT_OF_STOCK:
                counts['out_of_stock'] += 1
        
        return counts
    
    def get_low_stock_medicaments(self) -> List[Medicament]:
        """Retourne les médicaments avec stock faible."""
        return self._medicament_repo.get_low_stock()
    
    def get_expiring_medicaments(self, days: int = None) -> List[Medicament]:
        """Retourne les médicaments expirant bientôt."""
        if days is None:
            days = STOCK_CONFIG.get("expiry_alert_days", 30)
        return self._medicament_repo.get_expiring_soon(days)
    
    def get_expired_medicaments(self) -> List[Medicament]:
        """Retourne les médicaments périmés."""
        return self._medicament_repo.get_expired()