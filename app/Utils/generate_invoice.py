from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime

async def generate_invoice_pdf(place_order):
    """
    Takes a PlaceOrder instance and returns a PDF invoice as BytesIO stream.
    """

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Invoice Receipt")

    # Order Info
    c.setFont("Helvetica", 12)
    y = height - 100
    c.drawString(50, y, f"Order ID: {place_order.id}")
    y -= 20
    c.drawString(50, y, f"Vendor: {place_order.vendor.name}")
    y -= 20
    c.drawString(50, y, f"Seller: {place_order.seller.name}")
    y -= 20
    c.drawString(50, y, f"Factory: {place_order.factory.name}")
    y -= 20
    c.drawString(50, y, f"Order Status: {place_order.order_status.value}")
    y -= 20
    c.drawString(50, y, f"Payment Method: {place_order.payment_method.value}")
    y -= 20
    c.drawString(50, y, f"Order OTP: {place_order.order_otp or 'N/A'}")
    y -= 20
    c.drawString(50, y, f"Delivery Date: {place_order.delivery_date.strftime('%Y-%m-%d') if place_order.delivery_date else 'N/A'}")
    y -= 20
    c.drawString(50, y, f"Created At: {place_order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

    # Product Table Header
    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Product Name")
    c.drawString(250, y, "Quantity")
    c.drawString(350, y, "Price")

    # Product List
    y -= 20
    c.setFont("Helvetica", 12)
    for product in place_order.products:
        if y < 100:
            c.showPage()
            y = height - 50

        c.drawString(50, y, product.name)
        c.drawString(250, y, str(product.quantity if hasattr(product, 'quantity') else 1))
        c.drawString(350, y, f"₹{product.price if hasattr(product, 'price') else 0.0:.2f}")
        y -= 20

    # Summary
    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Product Amount: ₹{place_order.product_ammount:.2f}")
    y -= 20
    c.drawString(50, y, f"Platform Fee: ₹{place_order.platform_fee:.2f}")
    y -= 20
    c.drawString(50, y, f"Total Amount: ₹{place_order.total_amount:.2f}")

    # Footer
    y -= 40
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, y, "Thank you for your order!")

    # Finalize PDF
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer
