import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
import hashlib
from datetime import datetime
import tempfile
import webbrowser


class ETicketGenerator:
    def __init__(self, output_dir=None):
        """Initialize the ticket generator with an optional output directory"""
        self.output_dir = output_dir or os.path.join(
            os.path.dirname(__file__), "tickets"
        )
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_ticket_id(self, ticket_data):
        """Generate a unique ticket ID based on ticket data"""
        timestamp = ticket_data.get("timestamp", str(datetime.now()))
        customer = ticket_data.get("customer_name", "")
        seat = ticket_data.get("seat_id", "")
        performance = ticket_data.get("performance_date", "")

        data_string = f"{timestamp}{customer}{seat}{performance}"
        return hashlib.md5(data_string.encode()).hexdigest()[:8].upper()

    def generate_text_ticket(self, ticket_data):
        """Generate a plain text e-ticket"""
        ticket_id = ticket_data.get("ticket_id") or self.generate_ticket_id(ticket_data)

        text = f"""
==========================================================
                THEATER PERFORMANCE TICKET
==========================================================

Performance Date: {ticket_data.get("performance_date", "N/A")}
Seat: {ticket_data.get("seat_id", "N/A")}

Customer: {ticket_data.get("customer_name", "N/A")}
Phone: {ticket_data.get("customer_phone", "N/A")}

Price Paid: £{ticket_data.get("price", "0.00")}

Ticket ID: {ticket_id}

Please present this ticket at the entrance.
Thank you for your support!
==========================================================
        """
        return text

    def generate_html_ticket(self, ticket_data):
        """Generate an HTML e-ticket that can be emailed"""
        ticket_id = ticket_data.get("ticket_id") or self.generate_ticket_id(ticket_data)

        # Create QR code with ticket info
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(
            f"TICKET:{ticket_id}|SEAT:{ticket_data.get('seat_id', 'N/A')}|DATE:{ticket_data.get('performance_date', 'N/A')}"
        )
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Save QR code to temporary file
        qr_path = os.path.join(self.output_dir, f"qr_{ticket_id}.png")
        qr_img.save(qr_path)

        # Generate HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Theater E-Ticket</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                }}
                .ticket {{
                    width: 650px;
                    margin: 20px auto;
                    background-color: white;
                    border: 1px solid #ddd;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    padding: 20px;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 2px solid #333;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }}
                .content {{
                    display: flex;
                }}
                .details {{
                    flex: 2;
                    padding-right: 20px;
                }}
                .qrcode {{
                    flex: 1;
                    text-align: center;
                }}
                .qrcode img {{
                    max-width: 150px;
                }}
                .field {{
                    margin-bottom: 15px;
                }}
                .label {{
                    font-weight: bold;
                    margin-right: 10px;
                }}
                .footer {{
                    margin-top: 20px;
                    text-align: center;
                    font-size: 0.8em;
                    color: #777;
                    border-top: 1px solid #ddd;
                    padding-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="ticket">
                <div class="header">
                    <h1>Theater Performance Ticket</h1>
                </div>
                <div class="content">
                    <div class="details">
                        <div class="field">
                            <span class="label">Performance Date:</span>
                            {ticket_data.get("performance_date", "N/A")}
                        </div>
                        <div class="field">
                            <span class="label">Seat:</span>
                            {ticket_data.get("seat_id", "N/A")}
                        </div>
                        <div class="field">
                            <span class="label">Customer:</span>
                            {ticket_data.get("customer_name", "N/A")}
                        </div>
                        <div class="field">
                            <span class="label">Phone:</span>
                            {ticket_data.get("customer_phone", "N/A")}
                        </div>
                        <div class="field">
                            <span class="label">Price Paid:</span>
                            £{ticket_data.get("price", "0.00")}
                        </div>
                        <div class="field">
                            <span class="label">Ticket ID:</span>
                            {ticket_id}
                        </div>
                    </div>
                    <div class="qrcode">
                        <img src="qr_{ticket_id}.png" alt="QR Code">
                        <p>Scan for verification</p>
                    </div>
                </div>
                <div class="footer">
                    <p>Please present this ticket at the entrance. Thank you for your support!</p>
                    <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Save HTML to file
        html_path = os.path.join(self.output_dir, f"ticket_{ticket_id}.html")
        with open(html_path, "w") as f:
            f.write(html)

        return html_path

    def generate_pdf_ticket(self, ticket_data):
        """Generate a PDF e-ticket (requires reportlab library)"""
        # Since reportlab might not be installed, we'll use HTML as a fallback
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            import io

            ticket_id = ticket_data.get("ticket_id") or self.generate_ticket_id(
                ticket_data
            )
            pdf_path = os.path.join(self.output_dir, f"ticket_{ticket_id}.pdf")

            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4

            # Title
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(width / 2, height - 50, "THEATER PERFORMANCE TICKET")

            c.line(50, height - 70, width - 50, height - 70)

            # Details
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, height - 100, "Performance Date:")
            c.drawString(50, height - 120, "Seat:")
            c.drawString(50, height - 140, "Customer:")
            c.drawString(50, height - 160, "Phone:")
            c.drawString(50, height - 180, "Price Paid:")
            c.drawString(50, height - 200, "Ticket ID:")

            c.setFont("Helvetica", 12)
            c.drawString(180, height - 100, ticket_data.get("performance_date", "N/A"))
            c.drawString(180, height - 120, ticket_data.get("seat_id", "N/A"))
            c.drawString(180, height - 140, ticket_data.get("customer_name", "N/A"))
            c.drawString(180, height - 160, ticket_data.get("customer_phone", "N/A"))
            c.drawString(180, height - 180, f"£{ticket_data.get('price', '0.00')}")
            c.drawString(180, height - 200, ticket_id)

            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(
                f"TICKET:{ticket_id}|SEAT:{ticket_data.get('seat_id', 'N/A')}|DATE:{ticket_data.get('performance_date', 'N/A')}"
            )
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")

            qr_path = os.path.join(self.output_dir, f"qr_{ticket_id}.png")
            qr_img.save(qr_path)

            # Add QR code to PDF
            c.drawImage(qr_path, width - 200, height - 220, width=150, height=150)

            # Footer
            c.line(50, 100, width - 50, 100)
            c.setFont("Helvetica", 10)
            c.drawCentredString(
                width / 2,
                80,
                "Please present this ticket at the entrance. Thank you for your support!",
            )
            c.drawCentredString(
                width / 2,
                60,
                f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            )

            c.save()
            return pdf_path

        except ImportError:
            print("ReportLab not installed. Falling back to HTML ticket.")
            return self.generate_html_ticket(ticket_data)

    def show_ticket(self, ticket_path):
        """Open the ticket in a web browser or PDF viewer"""
        if os.path.exists(ticket_path):
            webbrowser.open(f"file://{os.path.abspath(ticket_path)}")
            return True
        return False


# Utility function for the main application
def generate_and_show_ticket(ticket_data, format_type="html"):
    """Generate a ticket and display it"""
    generator = ETicketGenerator()

    if format_type.lower() == "text":
        ticket_text = generator.generate_text_ticket(ticket_data)
        # Return the text for display in the application
        return ticket_text
    elif format_type.lower() == "pdf":
        ticket_path = generator.generate_pdf_ticket(ticket_data)
        generator.show_ticket(ticket_path)
        return ticket_path
    else:  # Default to HTML
        ticket_path = generator.generate_html_ticket(ticket_data)
        generator.show_ticket(ticket_path)
        return ticket_path


if __name__ == "__main__":
    # Test the ticket generator
    test_ticket = {
        "performance_date": "2023-06-01",
        "seat_id": "A12",
        "customer_name": "John Smith",
        "customer_phone": "07700 900123",
        "price": "10.00",
        "timestamp": datetime.now().isoformat(),
    }

    generator = ETicketGenerator()

    # Generate text ticket
    text_ticket = generator.generate_text_ticket(test_ticket)
    print(text_ticket)

    # Generate HTML ticket
    html_path = generator.generate_html_ticket(test_ticket)
    print(f"HTML ticket saved to {html_path}")

    # Try to generate PDF ticket
    try:
        pdf_path = generator.generate_pdf_ticket(test_ticket)
        print(f"PDF ticket saved to {pdf_path}")
    except Exception as e:
        print(f"Error generating PDF ticket: {e}")

    # Show HTML ticket
    generator.show_ticket(html_path)
