"""
Utilitaires pour la manipulation des dates.

Auteur: Alsény Camara
Version: 1.0
"""

from datetime import datetime, date, timedelta
from typing import Optional, Tuple


class DateUtils:
    """
    Classe utilitaire pour la manipulation des dates.
    
    Fournit des méthodes pour formater, parser et calculer des dates.
    """
    
    # Formats de date standards
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    DISPLAY_DATE_FORMAT = "%d/%m/%Y"
    DISPLAY_DATETIME_FORMAT = "%d/%m/%Y %H:%M"
    
    @staticmethod
    def now() -> datetime:
        """Retourne la date et heure actuelles."""
        return datetime.now()
    
    @staticmethod
    def today() -> date:
        """Retourne la date du jour."""
        return date.today()
    
    @staticmethod
    def format_date(d: date, display: bool = True) -> str:
        """
        Formate une date en chaîne.
        
        Args:
            d: Date à formater
            display: True pour format affichage (dd/mm/yyyy)
            
        Returns:
            str: Date formatée
        """
        if d is None:
            return ""
        
        format_str = DateUtils.DISPLAY_DATE_FORMAT if display else DateUtils.DATE_FORMAT
        return d.strftime(format_str)
    
    @staticmethod
    def format_datetime(dt: datetime, display: bool = True) -> str:
        """
        Formate une date/heure en chaîne.
        
        Args:
            dt: DateTime à formater
            display: True pour format affichage
            
        Returns:
            str: DateTime formatée
        """
        if dt is None:
            return ""
        
        format_str = DateUtils.DISPLAY_DATETIME_FORMAT if display else DateUtils.DATETIME_FORMAT
        return dt.strftime(format_str)
    
    @staticmethod
    def parse_date(date_str: str) -> Optional[date]:
        """
        Parse une chaîne en date.
        
        Args:
            date_str: Chaîne de date (dd/mm/yyyy ou yyyy-mm-dd)
            
        Returns:
            Optional[date]: Date parsée ou None
        """
        if not date_str:
            return None
        
        # Essayer différents formats
        formats = [
            DateUtils.DATE_FORMAT,
            DateUtils.DISPLAY_DATE_FORMAT,
            "%d-%m-%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def parse_datetime(datetime_str: str) -> Optional[datetime]:
        """
        Parse une chaîne en datetime.
        
        Args:
            datetime_str: Chaîne de datetime
            
        Returns:
            Optional[datetime]: DateTime parsée ou None
        """
        if not datetime_str:
            return None
        
        formats = [
            DateUtils.DATETIME_FORMAT,
            DateUtils.DISPLAY_DATETIME_FORMAT,
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def days_between(date1: date, date2: date) -> int:
        """
        Calcule le nombre de jours entre deux dates.
        
        Args:
            date1: Première date
            date2: Deuxième date
            
        Returns:
            int: Nombre de jours (positif si date2 > date1)
        """
        if date1 is None or date2 is None:
            return 0
        
        delta = date2 - date1
        return delta.days
    
    @staticmethod
    def days_until(target_date: date) -> int:
        """
        Calcule le nombre de jours jusqu'à une date.
        
        Args:
            target_date: Date cible
            
        Returns:
            int: Nombre de jours (négatif si passée)
        """
        if target_date is None:
            return 0
        
        return DateUtils.days_between(date.today(), target_date)
    
    @staticmethod
    def add_days(d: date, days: int) -> date:
        """
        Ajoute des jours à une date.
        
        Args:
            d: Date de base
            days: Nombre de jours à ajouter
            
        Returns:
            date: Nouvelle date
        """
        return d + timedelta(days=days)
    
    @staticmethod
    def start_of_day(d: date) -> datetime:
        """Retourne le début d'une journée (00:00:00)."""
        return datetime.combine(d, datetime.min.time())
    
    @staticmethod
    def end_of_day(d: date) -> datetime:
        """Retourne la fin d'une journée (23:59:59)."""
        return datetime.combine(d, datetime.max.time())
    
    @staticmethod
    def get_date_range(period: str) -> Tuple[date, date]:
        """
        Retourne une plage de dates selon une période.
        
        Args:
            period: 'today', 'week', 'month', 'year'
            
        Returns:
            Tuple[date, date]: (date_début, date_fin)
        """
        today = date.today()
        
        if period == 'today':
            return today, today
        
        elif period == 'week':
            start = today - timedelta(days=today.weekday())
            return start, today
        
        elif period == 'month':
            start = today.replace(day=1)
            return start, today
        
        elif period == 'year':
            start = today.replace(month=1, day=1)
            return start, today
        
        else:
            return today, today
    
    @staticmethod
    def is_expired(expiration_date: date) -> bool:
        """Vérifie si une date est expirée."""
        if expiration_date is None:
            return False
        return expiration_date < date.today()
    
    @staticmethod
    def is_expiring_soon(expiration_date: date, days: int = 30) -> bool:
        """Vérifie si une date expire bientôt."""
        if expiration_date is None:
            return False
        
        days_until = DateUtils.days_until(expiration_date)
        return 0 <= days_until <= days