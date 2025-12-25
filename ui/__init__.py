"""
Module UI - Interface utilisateur Tkinter.

Auteur: Alsény Camara
Version: 1.0
"""

from .login_view import LoginView
from .main_window import MainWindow
from .dashboard_view import DashboardView
from .medicament_view import MedicamentView
from .client_view import ClientView
from .sale_view import SaleView
from .user_view import UserView
from .report_view import ReportView

__all__ = [
    'LoginView',
    'MainWindow',
    'DashboardView',
    'MedicamentView',
    'ClientView',
    'SaleView',
    'UserView',
    'ReportView'
]