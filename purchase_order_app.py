from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
import num2words
from babel.numbers import format_currency

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def inr_format(amount):
    return format_currency(amount, 'INR', locale='en_IN').replace('\u20b9', '').strip()

COMPANY_DETAILS = """<b>Company Address:</b><br/>
ELIXIR PHARMACEUTICALS<br/>
Flat No-304, Sri Sai Apartments<br/>
Opp. Anuradha Timbers<br/>
Chinnathokatta, New Bowenapally<br/>
Secunderabad-500011, Telangana, India<br/>
Mobile No: 9069063399<br/>
GSTIN: 36AJHPG4769J1ZT"""

SHIPPING_DETAILS = COMPANY_DETAILS

@app.get("/")
def form_page(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/generate-po")
async def generate_po(
    po_number: str = Form(...),
    supplier_company: str = Form(...),
    supplier_address1: str = Form(...),
    supplier_address2: str = Form(...),
    supplier_city: str = Form(...),
    supplier_state: str = Form(...),
    supplier_gstin: str = Form(...),
    purchase_type: str = Form(...),
    delivery_schedule: str = Form(...),
    transport: str = Form(...),
    payment_terms: str = Form(...),
    product_name: str = Form(...),
    cas_number: str = Form(...),
    hsn_code: str = Form(...),
    unit: str = Form(...),
    quantity: int = Form(...),
    rate: float = Form(...),
    basic_amount: float = Form(...),
    sgst: float = Form(...),
    cgst: float = Form(...),
    igst: float = Form(...),
    tax_total: float = Form(...),
    grand_total: float = Form(...)
):
    supplier_details = f"""{supplier_company}
{supplier_address1}
{supplier_address2}
{supplier_city}, {supplier_state},
GSTIN : {supplier_gstin}"""

    filename = "static/generated_po.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30)
    styles = getSampleStyleSheet()
    centered_title = ParagraphStyle(name='CenterTitle', parent=styles['Title'], alignment=TA_CENTER)

    elements = []
    elements.append(Paragraph("PURCHASE ORDER", centered_title))
    elements.append(Spacer(1, 20))

    po_info = f"<b>PO Number:</b> EP/2025-26/{po_number}<br/><b>Date:</b> {date.today().strftime('%d-%m-%Y')}"
    table1 = Table([
        [Paragraph(COMPANY_DETAILS, styles['Normal']),
         Paragraph(SHIPPING_DETAILS, styles['Normal']),
         Paragraph(po_info, styles['Normal'])]
    ], colWidths=[180, 180, 150])
    table1.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, colors.grey),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))
    elements.append(table1)
    elements.append(Spacer(1, 10))

    formatted_supplier = supplier_details.replace('\n', '<br/>')
    purchase_info = f"""<b>Type of Purchase:</b> {purchase_type}<br/>
<b>Delivery Schedule:</b> {delivery_schedule}<br/>
<b>Transport:</b> {transport}<br/>
<b>Payment Terms:</b> {payment_terms}"""
    table2 = Table([
        [Paragraph(f"<b>Supplier Details:</b><br/>{formatted_supplier}", styles['Normal']),
         Paragraph(purchase_info, styles['Normal'])]
    ], colWidths=[270, 240])
    table2.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, colors.grey),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elements.append(table2)
    elements.append(Spacer(1, 10))

    product_data = [
        ['S.NO', 'PRODUCT NAME', 'HSN CODE', 'UNIT', 'QTY', 'RATE / UNIT(INR)', 'Total (INR)'],
        ['1', Paragraph(f"<b>{product_name}</b><br/>(CAS No-{cas_number})", styles['Normal']), hsn_code, unit, str(quantity), f"{rate:,.2f}", f"{basic_amount:,.2f}"]
    ]
    product_table = Table(product_data, colWidths=[40, 180, 70, 50, 40, 80, 80])
    product_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.7, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (4,1), (-1,-1), 'RIGHT')
    ]))
    elements.append(product_table)
    elements.append(Spacer(1, 10))

    totals_data = [
        ["", "", "BASIC AMOUNT", f"{basic_amount:,.2f}"],
        ["", "", "SGST", f"{sgst:,.2f}"],
        ["", "", "CGST", f"{cgst:,.2f}"],
        ["", "", "IGST", f"{igst:,.2f}" if igst else "-"],
        ["", "", "TAX AMOUNT", f"{tax_total:,.2f}"],
        ["", "", "GRAND TOTAL AMOUNT", f"{grand_total:,.2f}"]
    ]
    totals_table = Table(totals_data, colWidths=[100, 150, 150, 100])
    totals_table.setStyle(TableStyle([
        ('GRID', (2,0), (-1,-1), 0.6, colors.black),
        ('FONTNAME', (2,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (3,0), (-1,-1), 'RIGHT'),
        ('BACKGROUND', (2,-1), (-1,-1), colors.lightgrey)
    ]))
    elements.append(totals_table)

    amount_words = num2words.num2words(grand_total, to='currency', lang='en_IN').replace('euro', 'Rupees').replace('cents', 'paise')
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Rupees (In Words):</b> {amount_words.title()} Only", styles['Normal']))

    terms = [
        "Kindly send COA, MOA, MSDS along with Material",
        "Pl.Acknowledge the receipt of the order & confirm supplies",
        "Pl.send the copy of the bill as advance information",
        "Pl.Ensure all duties & taxes under GST are paid in time & Upload the invoices timely and with correct GSTIN, otherwise we shall deduct the GST amount from the bill",
        "The quality of supplies is to be approved by our end user and approval or rejection will be final",
        "If the material is rejected, TO & fro charges (from start to final destination) should be in your account.",
        "GST invoice should bear Purchase order No & Date"
    ]

    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<b>TERMS & CONDITION:</b>", styles["Heading4"]))
    for idx, term in enumerate(terms, start=1):
        elements.append(Paragraph(f"{idx}. {term}", styles["Normal"]))

    elements.append(Spacer(1, 50))
    elements.append(Paragraph("<para alignment='right'><b>For ELIXIR PHARMACEUTICALS</b></para>", styles["Normal"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<para alignment='right'>Authorised Signatory</para>", styles["Normal"]))

    doc.build(elements)
    return FileResponse(filename, media_type='application/pdf', filename="purchase_order.pdf")
