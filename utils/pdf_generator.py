"""
Générateur de documents PDF.

Auteur: Alsény Camara
Version: 2.0
"""

import os
from datetime import datetime
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SALE_CONFIG, BASE_DIR

# Import reportlab
try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.units import mm, cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PDFGenerator:
    """
    Générateur de documents PDF pour les tickets et rapports.
    Utilise reportlab pour la génération PDF.
    """
    
    # Répertoire de sortie
    OUTPUT_DIR = os.path.join(BASE_DIR, 'receipts')
    
    # Dimensions ticket (80mm de large)
    TICKET_WIDTH = 80 * mm
    TICKET_MARGIN = 5 * mm
    
    def __init__(self):
        """Initialise le générateur."""
        self._ensure_output_dir()
    
    @classmethod
    def _ensure_output_dir(cls) -> None:
        """Crée le répertoire de sortie si nécessaire."""
        if not os.path.exists(cls.OUTPUT_DIR):
            os.makedirs(cls.OUTPUT_DIR)
    
    @classmethod
    def generate_receipt(cls, sale_data: Dict[str, Any]) -> str:
        """
        Génère un ticket de caisse en PDF.
        
        Args:
            sale_data: Données de la vente
            
        Returns:
            str: Chemin du fichier PDF généré
        """
        cls._ensure_output_dir()
        
        if not REPORTLAB_AVAILABLE:
            # Fallback vers texte si reportlab non disponible
            return cls._generate_receipt_txt(sale_data)
        
        # Nom du fichier
        sale_number = sale_data.get('sale_number', 'ticket')
        timestamp = datetime.now().strftime('%H%M%S')
        filename = f"{sale_number}_{timestamp}.pdf"
        filepath = os.path.join(cls.OUTPUT_DIR, filename)
        
        # Créer le PDF
        cls._create_receipt_pdf(filepath, sale_data)
        
        return filepath
    
    @classmethod
    def _create_receipt_pdf(cls, filepath: str, data: Dict[str, Any]) -> None:
        """
        Crée le fichier PDF du ticket.
        
        Args:
            filepath: Chemin du fichier de sortie
            data: Données de la vente
        """
        # Configuration de la page (format ticket)
        page_width = 80 * mm
        page_height = 200 * mm  # Hauteur dynamique serait idéale
        
        c = canvas.Canvas(filepath, pagesize=(page_width, page_height))
        
        # Configuration des polices
        y = page_height - 10 * mm
        left_margin = 5 * mm
        right_margin = page_width - 5 * mm
        center = page_width / 2
        line_height = 4 * mm
        
        # Titre pharmacie
        c.setFont("Helvetica-Bold", 12)
        pharmacy_name = SALE_CONFIG.get('receipt_title', 'PHARMACIE')
        c.drawCentredString(center, y, pharmacy_name)
        y -= line_height * 1.5
        
        c.setFont("Helvetica", 9)
        c.drawCentredString(center, y, "Ticket de caisse")
        y -= line_height * 1.5
        
        # Ligne de séparation
        c.setLineWidth(0.5)
        c.line(left_margin, y, right_margin, y)
        y -= line_height
        
        # Informations vente
        c.setFont("Helvetica", 8)
        c.drawString(left_margin, y, f"N° Vente: {data.get('sale_number', '')}")
        y -= line_height
        
        c.drawString(left_margin, y, f"Date: {data.get('sale_date', '')}")
        y -= line_height
        
        c.drawString(left_margin, y, f"Vendeur: {data.get('seller_name', '')}")
        y -= line_height
        
        if data.get('client_name'):
            c.drawString(left_margin, y, f"Client: {data.get('client_name')}")
            y -= line_height
        
        # Ligne de séparation
        y -= 2 * mm
        c.line(left_margin, y, right_margin, y)
        y -= line_height
        
        # En-tête articles
        c.setFont("Helvetica-Bold", 8)
        c.drawString(left_margin, y, "Article")
        c.drawRightString(right_margin, y, "Total")
        y -= line_height
        
        c.setLineWidth(0.3)
        c.line(left_margin, y + 1 * mm, right_margin, y + 1 * mm)
        y -= 2 * mm
        
        # Articles
        c.setFont("Helvetica", 7)
        for item in data.get('lines', []):
            name = str(item.get('name', ''))[:28]
            qty = item.get('quantity', 0)
            unit_price = item.get('unit_price', 0)
            total = item.get('line_total', 0)
            
            # Nom du produit
            c.drawString(left_margin, y, name)
            y -= line_height * 0.8
            
            # Détails quantité x prix
            detail = f"  {qty} x {unit_price:,.0f}"
            c.drawString(left_margin, y, detail)
            c.drawRightString(right_margin, y, f"{total:,.0f}")
            y -= line_height
        
        # Ligne de séparation
        y -= 2 * mm
        c.line(left_margin, y, right_margin, y)
        y -= line_height
        
        # Totaux
        currency = SALE_CONFIG.get('currency_symbol', 'GNF')
        
        c.setFont("Helvetica", 8)
        subtotal = data.get('subtotal', 0)
        c.drawString(left_margin, y, "Sous-total:")
        c.drawRightString(right_margin, y, f"{subtotal:,.0f} {currency}")
        y -= line_height
        
        discount = data.get('discount_amount', 0)
        if discount > 0:
            discount_pct = data.get('discount_percentage', 0)
            c.drawString(left_margin, y, f"Remise ({discount_pct:.0f}%):")
            c.drawRightString(right_margin, y, f"-{discount:,.0f} {currency}")
            y -= line_height
        
        # Ligne double pour le total
        y -= 2 * mm
        c.setLineWidth(1)
        c.line(left_margin, y, right_margin, y)
        y -= line_height
        
        # Total
        c.setFont("Helvetica-Bold", 11)
        total = data.get('total', 0)
        c.drawString(left_margin, y, "TOTAL:")
        c.drawRightString(right_margin, y, f"{total:,.0f} {currency}")
        y -= line_height * 1.5
        
        c.setLineWidth(1)
        c.line(left_margin, y, right_margin, y)
        y -= line_height
        
        # Points de fidélité
        points = data.get('loyalty_points_earned', 0)
        if points > 0:
            c.setFont("Helvetica", 8)
            c.drawString(left_margin, y, f"Points gagnés: +{points}")
            y -= line_height
            
            client_points = data.get('client_points')
            if client_points is not None:
                c.drawString(left_margin, y, f"Solde points: {client_points}")
                y -= line_height
            
            y -= 2 * mm
            c.setLineWidth(0.3)
            c.line(left_margin, y, right_margin, y)
            y -= line_height
        
        # Pied de page
        y -= 5 * mm
        c.setFont("Helvetica", 9)
        c.drawCentredString(center, y, "Merci de votre visite !")
        y -= line_height
        c.drawCentredString(center, y, "À bientôt")
        y -= line_height * 2
        
        c.setLineWidth(0.5)
        c.line(left_margin, y, right_margin, y)
        
        # Sauvegarder
        c.save()
    
    @classmethod
    def _generate_receipt_txt(cls, sale_data: Dict[str, Any]) -> str:
        """
        Génère un ticket en texte (fallback si reportlab non disponible).
        
        Args:
            sale_data: Données de la vente
            
        Returns:
            str: Chemin du fichier généré
        """
        sale_number = sale_data.get('sale_number', 'ticket')
        filename = f"{sale_number}_{datetime.now().strftime('%H%M%S')}.txt"
        filepath = os.path.join(cls.OUTPUT_DIR, filename)
        
        content = cls._format_receipt_txt(sale_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    @classmethod
    def _format_receipt_txt(cls, data: Dict[str, Any]) -> str:
        """Formate le contenu du ticket en texte."""
        width = 42
        line = "=" * width
        dash = "-" * width
        
        def center(text):
            return text.center(width)
        
        def two_cols(left, right):
            space = width - len(left) - len(right)
            return left + " " * max(1, space) + right
        
        lines = []
        
        # En-tête
        lines.append(line)
        lines.append(center(SALE_CONFIG.get('receipt_title', 'PHARMACIE')))
        lines.append(center("Ticket de caisse"))
        lines.append(line)
        
        # Informations de la vente
        lines.append(f"N° Vente: {data.get('sale_number', '')}")
        lines.append(f"Date: {data.get('sale_date', '')}")
        lines.append(f"Vendeur: {data.get('seller_name', '')}")
        
        if data.get('client_name'):
            lines.append(f"Client: {data.get('client_name')}")
        
        lines.append(dash)
        lines.append(two_cols("Article", "Total"))
        lines.append(dash)
        
        # Articles
        for item in data.get('lines', []):
            name = item.get('name', '')[:25]
            qty = item.get('quantity', 0)
            total = item.get('line_total', 0)
            lines.append(f"{name}")
            lines.append(two_cols(f"  {qty} x {item.get('unit_price', 0):.0f}", f"{total:.0f}"))
        
        lines.append(dash)
        
        # Totaux
        currency = SALE_CONFIG.get('currency_symbol', 'GNF')
        
        subtotal = data.get('subtotal', 0)
        lines.append(two_cols("Sous-total:", f"{subtotal:.0f} {currency}"))
        
        discount = data.get('discount_amount', 0)
        if discount > 0:
            discount_pct = data.get('discount_percentage', 0)
            lines.append(two_cols(f"Remise ({discount_pct:.0f}%):", f"-{discount:.0f} {currency}"))
        
        lines.append(line)
        
        total = data.get('total', 0)
        lines.append(two_cols("TOTAL:", f"{total:.0f} {currency}"))
        
        lines.append(line)
        
        # Points fidélité
        points = data.get('loyalty_points_earned', 0)
        if points > 0:
            lines.append(f"Points gagnés: +{points}")
            client_points = data.get('client_points')
            if client_points is not None:
                lines.append(f"Solde points: {client_points}")
            lines.append(dash)
        
        # Pied de page
        lines.append("")
        lines.append(center("Merci de votre visite !"))
        lines.append(center("À bientôt"))
        lines.append("")
        lines.append(line)
        
        return "\n".join(lines)
    
    @classmethod
    def generate_stock_report(cls, report_data: Dict[str, Any], medicaments: List[Dict]) -> str:
        """
        Génère un rapport de stock en PDF.
        
        Args:
            report_data: Données du rapport
            medicaments: Liste des médicaments
            
        Returns:
            str: Chemin du fichier généré
        """
        cls._ensure_output_dir()
        
        filename = f"stock_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(cls.OUTPUT_DIR, filename)
        
        if not REPORTLAB_AVAILABLE:
            return cls._generate_stock_report_txt(report_data, medicaments)
        
        # Créer le document PDF
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        elements.append(Paragraph("RAPPORT DE STOCK", title_style))
        
        # Date
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        elements.append(Paragraph(
            f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            date_style
        ))
        
        # Tableau
        table_data = [['Code', 'Nom', 'Stock', 'Seuil', 'Valeur']]
        
        total_value = 0
        for med in medicaments:
            code = str(med.get('code', ''))[:12]
            name = str(med.get('name', ''))[:30]
            stock = med.get('quantity', 0)
            threshold = med.get('threshold', 0)
            value = med.get('value', 0)
            total_value += value
            
            table_data.append([
                code,
                name,
                str(stock),
                str(threshold),
                f"{value:,.0f}"
            ])
        
        # Ligne total
        table_data.append(['', '', '', 'TOTAL:', f"{total_value:,.0f}"])
        
        # Créer le tableau
        table = Table(table_data, colWidths=[2.5*cm, 7*cm, 2*cm, 2*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(table)
        
        # Générer le PDF
        doc.build(elements)
        
        return filepath
    
    @classmethod
    def _generate_stock_report_txt(cls, report_data: Dict[str, Any], medicaments: List[Dict]) -> str:
        """Génère un rapport de stock en texte (fallback)."""
        filename = f"stock_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(cls.OUTPUT_DIR, filename)
        
        lines = []
        lines.append("=" * 80)
        lines.append("RAPPORT DE STOCK".center(80))
        lines.append(f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M')}".center(80))
        lines.append("=" * 80)
        lines.append("")
        
        header = f"{'Code':<12} {'Nom':<30} {'Stock':>8} {'Seuil':>8} {'Valeur':>12}"
        lines.append(header)
        lines.append("-" * 80)
        
        total_value = 0
        for med in medicaments:
            code = str(med.get('code', ''))[:10]
            name = str(med.get('name', ''))[:28]
            stock = med.get('quantity', 0)
            threshold = med.get('threshold', 0)
            value = med.get('value', 0)
            total_value += value
            
            lines.append(f"{code:<12} {name:<30} {stock:>8} {threshold:>8} {value:>12,.0f}")
        
        lines.append("-" * 80)
        lines.append(f"{'TOTAL':>62} {total_value:>12,.0f}")
        lines.append("=" * 80)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        
        return filepath
    
    @classmethod
    def generate_sales_report(cls, report_data: Dict[str, Any], sales: List[Dict]) -> str:
        """
        Génère un rapport des ventes en PDF.
        
        Args:
            report_data: Données du rapport
            sales: Liste des ventes
            
        Returns:
            str: Chemin du fichier généré
        """
        cls._ensure_output_dir()
        
        filename = f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(cls.OUTPUT_DIR, filename)
        
        if not REPORTLAB_AVAILABLE:
            # Fallback texte
            return cls._generate_sales_report_txt(report_data, sales)
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        elements.append(Paragraph("RAPPORT DES VENTES", title_style))
        
        # Période
        period = report_data.get('period', '')
        elements.append(Paragraph(f"Période: {period}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Résumé
        summary_data = [
            ['Total ventes', str(report_data.get('total_sales', 0))],
            ['Chiffre d\'affaires', report_data.get('total_revenue_display', '0')],
            ['Remises accordées', report_data.get('total_discount_display', '0')],
        ]
        
        summary_table = Table(summary_data, colWidths=[8*cm, 5*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 30))
        
        # Tableau des ventes
        table_data = [['N° Vente', 'Date', 'Client', 'Vendeur', 'Total']]
        
        for sale in sales:
            table_data.append([
                sale.get('number', ''),
                sale.get('date', ''),
                sale.get('client', 'Anonyme')[:20],
                sale.get('seller', '')[:15],
                sale.get('total_display', '')
            ])
        
        table = Table(table_data, colWidths=[3*cm, 2.5*cm, 4*cm, 3*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        
        doc.build(elements)
        
        return filepath
    
    @classmethod
    def _generate_sales_report_txt(cls, report_data: Dict[str, Any], sales: List[Dict]) -> str:
        """Génère un rapport des ventes en texte (fallback)."""
        filename = f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(cls.OUTPUT_DIR, filename)
        
        lines = []
        lines.append("=" * 80)
        lines.append("RAPPORT DES VENTES".center(80))
        lines.append(f"Période: {report_data.get('period', '')}".center(80))
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Total ventes: {report_data.get('total_sales', 0)}")
        lines.append(f"Chiffre d'affaires: {report_data.get('total_revenue_display', '0')}")
        lines.append("")
        lines.append("-" * 80)
        
        for sale in sales:
            lines.append(f"{sale.get('number', '')} | {sale.get('date', '')} | {sale.get('client', 'Anonyme')} | {sale.get('total_display', '')}")
        
        lines.append("=" * 80)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        
        return filepath