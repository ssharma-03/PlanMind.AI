import io
import datetime

# Try to import FPDF, but provide fallback if not available
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
    
    class StrategyPDF(FPDF):
        def header(self):
            # Arial bold 15
            self.set_font('Arial', 'B', 15)
            # Move to the right
            self.cell(80)
            # Title
            self.cell(30, 10, 'Business Strategy Plan', 0, 0, 'C')
            # Line break
            self.ln(20)

        def footer(self):
            # Position at 1.5 cm from bottom
            self.set_y(-15)
            # Arial italic 8
            self.set_font('Arial', 'I', 8)
            # Add date
            current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cell(0, 10, f'Generated on {current_date} - Powered by PlanMind AI', 0, 0, 'C')
            # Page number
            self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'R')
            
except ImportError:
    FPDF_AVAILABLE = False
    print("FPDF package not available. PDF export will be disabled.")

def export_to_pdf(business_problem, context, strategy_response):
    """Export the strategy to PDF"""
    if not FPDF_AVAILABLE:
        return b"PDF export is not available because the FPDF package is not installed."
    
    pdf = StrategyPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Add business problem
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Business Problem:', 0, 1)
    pdf.set_font('Arial', '', 11)
    
    # Format the business problem text to fit on the page
    pdf.multi_cell(0, 10, business_problem)
    pdf.ln(5)
    
    # Add context if provided
    if context:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Additional Context:', 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(0, 10, context)
        pdf.ln(5)
    
    # Add a divider
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    # Add the strategy response
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Strategic Plan', 0, 1, 'C')
    pdf.ln(5)
    
    # Process and add the strategy text
    # This is a simplified approach - for a production app,
    # you would parse and format the markdown more carefully
    pdf.set_font('Arial', '', 11)
    
    # Split the response into lines
    lines = strategy_response.split('\n')
    for line in lines:
        # Handle headers
        if line.startswith('# '):
            pdf.set_font('Arial', 'B', 14)
            pdf.multi_cell(0, 10, line[2:])
            pdf.set_font('Arial', '', 11)
        elif line.startswith('## '):
            pdf.set_font('Arial', 'B', 12)
            pdf.multi_cell(0, 10, line[3:])
            pdf.set_font('Arial', '', 11)
        elif line.startswith('### '):
            pdf.set_font('Arial', 'BI', 11)
            pdf.multi_cell(0, 10, line[4:])
            pdf.set_font('Arial', '', 11)
        elif line.startswith('- '):
            # Bullet points
            pdf.cell(5, 10, '', 0, 0)
            pdf.multi_cell(0, 10, '• ' + line[2:])
        elif line.strip() == '':
            # Empty line
            pdf.ln(5)
        else:
            # Regular text
            pdf.multi_cell(0, 10, line)
    
    # Return the PDF as bytes
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    
    return pdf_buffer.getvalue() 