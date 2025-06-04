from flask import Flask, render_template, request, send_file
import requests

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Compose PO number
        po_number = "EP/2025-26/" + request.form["po_number_suffix"]

        # Compose Supplier Block
        supplier_details = f"""{request.form["supplier_name"]}
{request.form["supplier_address1"]}
{request.form["supplier_address2"]}
{request.form["supplier_city"]}, {request.form["supplier_state"]}
GSTIN: {request.form["supplier_gstin"]}"""

        # Product Details
        product_name = request.form["product_name"]
        cas_number = request.form["cas_number"]
        hsn_code = request.form["hsn_code"]
        unit = request.form["unit"]
        quantity = int(request.form["quantity"])
        rate = float(request.form["rate_per_unit"])
        basic_amount = quantity * rate
        sgst = basic_amount * 0.09
        cgst = basic_amount * 0.09
        igst = 0
        tax_total = sgst + cgst
        grand_total = basic_amount + tax_total

        # Convert to string to pass
        data = {
            "po_number": po_number,
            "supplier_details": supplier_details,
            "purchase_type": request.form["purchase_type"],
            "delivery_schedule": request.form["delivery_schedule"],
            "transport": request.form["transport"],
            "payment_terms": request.form["payment_terms"],
            "product_name": product_name,
            "cas_number": cas_number,
            "hsn_code": hsn_code,
            "unit": unit,
            "quantity": quantity,
            "rate": rate,
            "basic_amount": basic_amount,
            "sgst": sgst,
            "cgst": cgst,
            "igst": igst,
            "tax_total": tax_total,
            "grand_total": grand_total,
        }

        response = requests.post("http://localhost:8000/generate-po", data=data)
        with open("static/generated_po.pdf", "wb") as f:
            f.write(response.content)

        return send_file("static/generated_po.pdf", as_attachment=True)

    return render_template("form.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
