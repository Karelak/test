import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
from datetime import datetime
from db_manager import DBManager
from models_sql import Performance, Customer, Ticket, SEAT_STATUS
from ticket_generator import generate_and_show_ticket
import os
from tkinter import filedialog


class TheaterTicketSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Theater Ticket Management System (SQL)")
        self.root.geometry("1000x600")

        # Initialize database
        self.db = DBManager("theater.db")

        # Create UI
        self.create_notebook()
        self.create_booking_tab()
        self.create_search_tab()
        self.create_reports_tab()
        self.create_seating_tab()

    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

    def create_booking_tab(self):
        booking_frame = ttk.Frame(self.notebook)
        self.notebook.add(booking_frame, text="Book Tickets")

        # Performance selection
        ttk.Label(booking_frame, text="Select Performance:").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        self.performance_var = tk.StringVar()
        self.performance_combo = ttk.Combobox(
            booking_frame, textvariable=self.performance_var
        )
        self.update_performance_list()
        self.performance_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.performance_combo.bind("<<ComboboxSelected>>", self.update_available_seats)

        # Customer details
        ttk.Label(booking_frame, text="Customer Name:").grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )
        self.customer_name_var = tk.StringVar()
        ttk.Entry(booking_frame, textvariable=self.customer_name_var).grid(
            row=1, column=1, padx=10, pady=10, sticky="w"
        )

        ttk.Label(booking_frame, text="Phone Number:").grid(
            row=2, column=0, padx=10, pady=10, sticky="w"
        )
        self.phone_var = tk.StringVar()
        ttk.Entry(booking_frame, textvariable=self.phone_var).grid(
            row=2, column=1, padx=10, pady=10, sticky="w"
        )

        ttk.Label(booking_frame, text="Customer Type:").grid(
            row=3, column=0, padx=10, pady=10, sticky="w"
        )
        self.customer_type_var = tk.StringVar(value="Regular")
        customer_type_combo = ttk.Combobox(
            booking_frame, textvariable=self.customer_type_var
        )
        customer_type_combo["values"] = [
            "Regular",
            "Under 18",
            "Over 65",
            "Special Guest",
        ]
        customer_type_combo.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        # Seat selection
        ttk.Label(booking_frame, text="Select Seat:").grid(
            row=4, column=0, padx=10, pady=10, sticky="w"
        )
        self.seat_var = tk.StringVar()
        self.seat_combo = ttk.Combobox(booking_frame, textvariable=self.seat_var)
        self.seat_combo.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        # Buttons
        ttk.Button(booking_frame, text="Book Ticket", command=self.book_ticket).grid(
            row=5, column=0, padx=10, pady=10
        )
        ttk.Button(booking_frame, text="Block Seat", command=self.block_seat).grid(
            row=5, column=1, padx=10, pady=10
        )
        ttk.Button(
            booking_frame, text="Generate E-Ticket", command=self.generate_eticket
        ).grid(row=5, column=2, padx=10, pady=10)

    def create_search_tab(self):
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="Search")

        # Search by customer
        ttk.Label(search_frame, text="Customer Search:").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        self.search_name_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_name_var).grid(
            row=0, column=1, padx=10, pady=10, sticky="w"
        )
        ttk.Button(search_frame, text="Search", command=self.search_customer).grid(
            row=0, column=2, padx=10, pady=10
        )

        # Search results
        ttk.Label(search_frame, text="Search Results:").grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )
        self.search_results = ttk.Treeview(
            search_frame, columns=("Name", "Phone", "Performance", "Seat", "Price")
        )
        self.search_results.heading("Name", text="Name")
        self.search_results.heading("Phone", text="Phone")
        self.search_results.heading("Performance", text="Performance")
        self.search_results.heading("Seat", text="Seat")
        self.search_results.heading("Price", text="Price")
        self.search_results.column("#0", width=0, stretch=tk.NO)
        self.search_results.grid(
            row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew"
        )

        # View ticket holders for performance
        ttk.Label(search_frame, text="View Ticket Holders:").grid(
            row=3, column=0, padx=10, pady=10, sticky="w"
        )
        self.ticket_holders_var = tk.StringVar()
        self.ticket_holders_combo = ttk.Combobox(
            search_frame, textvariable=self.ticket_holders_var
        )
        self.update_performance_list(self.ticket_holders_combo)
        self.ticket_holders_combo.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        ttk.Button(search_frame, text="View", command=self.view_ticket_holders).grid(
            row=3, column=2, padx=10, pady=10
        )

    def create_reports_tab(self):
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Reports")

        ttk.Label(reports_frame, text="Select Performance:").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        self.report_performance_var = tk.StringVar()
        self.report_performance_combo = ttk.Combobox(
            reports_frame, textvariable=self.report_performance_var
        )
        self.update_performance_list(self.report_performance_combo)
        self.report_performance_combo.grid(
            row=0, column=1, padx=10, pady=10, sticky="w"
        )
        ttk.Button(
            reports_frame, text="Generate Report", command=self.generate_report
        ).grid(row=0, column=2, padx=10, pady=10)

        # Report results
        self.report_text = tk.Text(reports_frame, height=15, width=60)
        self.report_text.grid(
            row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew"
        )

    def create_seating_tab(self):
        seating_frame = ttk.Frame(self.notebook)
        self.notebook.add(seating_frame, text="Seating Layout")

        ttk.Label(seating_frame, text="Select Performance:").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        self.seating_performance_var = tk.StringVar()
        self.seating_performance_combo = ttk.Combobox(
            seating_frame, textvariable=self.seating_performance_var
        )
        self.update_performance_list(self.seating_performance_combo)
        self.seating_performance_combo.grid(
            row=0, column=1, padx=10, pady=10, sticky="w"
        )
        ttk.Button(seating_frame, text="View Seating", command=self.view_seating).grid(
            row=0, column=2, padx=10, pady=10
        )

        # Seating layout canvas
        self.seating_canvas = tk.Canvas(
            seating_frame, bg="white", height=400, width=800
        )
        self.seating_canvas.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        self.seating_canvas.bind("<Button-1>", self.seat_clicked)

    def update_performance_list(self, combobox=None):
        """Update the list of performances in the combobox"""
        performances = self.db.get_performances()
        dates = [p["date"] for p in performances]

        if combobox is None:
            combobox = self.performance_combo

        combobox["values"] = dates

    def update_available_seats(self, event=None):
        """Update the list of available seats for the selected performance"""
        selected_date = self.performance_var.get()
        if not selected_date:
            return

        performance = self.get_performance_by_date(selected_date)
        if not performance:
            return

        available_seats = performance.get_available_seats()
        self.seat_combo["values"] = available_seats

    def book_ticket(self):
        """Book a ticket for the selected performance and seat"""
        performance_date = self.performance_var.get()
        customer_name = self.customer_name_var.get()
        phone = self.phone_var.get()
        customer_type = self.customer_type_var.get()
        seat_id = self.seat_var.get()

        if not all([performance_date, customer_name, phone, customer_type, seat_id]):
            messagebox.showerror("Error", "All fields are required")
            return

        performance = self.get_performance_by_date(performance_date)
        if not performance:
            messagebox.showerror("Error", "Invalid performance selected")
            return

        # Calculate price based on customer type
        price = 0
        if customer_type == "Regular":
            price = 10
        elif customer_type in ["Under 18", "Over 65"]:
            price = 5
        # Special guests pay nothing (price=0)

        # Check for single seats
        if performance.check_middle_seat(seat_id):
            response = messagebox.askyesno(
                "Warning",
                "This booking will leave a single seat in the middle of a row. Proceed anyway?",
            )
            if not response:
                return

        # Create customer and ticket
        customer = Customer.create(self.db, customer_name, phone, customer_type)

        # Update seat status
        if performance.book_seat(seat_id):
            # Create the ticket
            ticket = Ticket.create(self.db, customer, performance, seat_id, price)

            messagebox.showinfo(
                "Success",
                f"Ticket booked for {customer_name}, Seat: {seat_id}, Price: £{price}",
            )

            # Clear form
            self.customer_name_var.set("")
            self.phone_var.set("")
            self.seat_var.set("")
            self.update_available_seats()

            # Generate e-ticket option
            response = messagebox.askyesno(
                "E-Ticket", "Would you like to generate an e-ticket?"
            )
            if response:
                ticket_text = ticket.generate_e_ticket()
                self.show_eticket(ticket_text)
        else:
            messagebox.showerror("Error", "Seat is not available")

    def block_seat(self):
        """Block a seat for the selected performance"""
        performance_date = self.performance_var.get()
        seat_id = self.seat_var.get()

        if not performance_date or not seat_id:
            messagebox.showerror("Error", "Performance and seat must be selected")
            return

        performance = self.get_performance_by_date(performance_date)
        if not performance:
            messagebox.showerror("Error", "Invalid performance selected")
            return

        if performance.block_seat(seat_id):
            messagebox.showinfo("Success", f"Seat {seat_id} has been blocked")
            self.update_available_seats()
        else:
            messagebox.showerror("Error", "Seat cannot be blocked")

    def generate_eticket(self):
        """Generate an e-ticket for a previously booked ticket"""
        # Ask for customer name
        customer_name = simpledialog.askstring("E-Ticket", "Enter customer name:")
        if not customer_name:
            return

        # Search for tickets by this customer
        tickets = self.db.get_tickets_by_customer_name(customer_name)

        if not tickets:
            messagebox.showerror("Error", "No tickets found for this customer")
            return

        # If multiple tickets found, ask which one to generate e-ticket for
        selected_ticket = None
        if len(tickets) == 1:
            selected_ticket = tickets[0]
        else:
            ticket_selection = []
            for idx, t in enumerate(tickets):
                ticket_selection.append(f"{idx + 1}: {t['date']} - Seat {t['seat_id']}")

            ticket_idx = simpledialog.askinteger(
                "Select Ticket",
                f"Multiple tickets found for {customer_name}. Select one:\n"
                + "\n".join(ticket_selection),
                minvalue=1,
                maxvalue=len(tickets),
            )

            if not ticket_idx:
                return

            selected_ticket = tickets[ticket_idx - 1]

        # Ask for ticket format
        formats = ["HTML", "PDF", "Text"]
        format_idx = simpledialog.askinteger(
            "E-Ticket Format",
            "Select ticket format:\n1: HTML\n2: PDF\n3: Text",
            minvalue=1,
            maxvalue=3,
        )

        if not format_idx:
            return

        format_type = formats[format_idx - 1].lower()

        # Prepare ticket data
        ticket_data = {
            "performance_date": selected_ticket["date"],
            "seat_id": selected_ticket["seat_id"],
            "customer_name": selected_ticket["name"],
            "customer_phone": selected_ticket["phone"],
            "price": str(selected_ticket["price"]),
            "timestamp": selected_ticket["timestamp"],
        }

        # Generate ticket
        result = generate_and_show_ticket(ticket_data, format_type)

        # For text format, show in dialog
        if format_type == "text":
            self.show_eticket(result)
        else:
            messagebox.showinfo(
                "E-Ticket", f"E-Ticket generated and saved to:\n{result}"
            )

            # Ask if user wants to email the ticket
            if messagebox.askyesno(
                "Email Ticket", "Would you like to email this ticket?"
            ):
                self.email_ticket(result, ticket_data["customer_name"])

    def email_ticket(self, ticket_path, customer_name):
        """Simulate emailing a ticket to a customer"""
        # In a real app, this would connect to an email service
        # For now, we'll just show a dialog
        messagebox.showinfo(
            "Email Sent",
            f"E-Ticket would be emailed to {customer_name}.\n\n"
            "In a production system, this would connect to an email service like "
            "SMTP, SendGrid, or Mailgun to send the actual email with the ticket attached.",
        )

    def show_eticket(self, ticket_text):
        """Show an e-ticket in a new window"""
        ticket_window = tk.Toplevel(self.root)
        ticket_window.title("E-Ticket")
        ticket_window.geometry("500x400")

        ticket_display = tk.Text(
            ticket_window, height=20, width=60, font=("Courier", 10)
        )
        ticket_display.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        ticket_display.insert(tk.END, ticket_text)

        # Add buttons for saving and printing
        button_frame = tk.Frame(ticket_window)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Save",
            command=lambda: self.save_text_ticket(ticket_text),
        ).pack(side=tk.LEFT, padx=10)

        ttk.Button(
            button_frame,
            text="Print",
            command=lambda: messagebox.showinfo(
                "Print", "Printing functionality would be implemented here"
            ),
        ).pack(side=tk.LEFT, padx=10)

        ttk.Button(
            button_frame,
            text="Email",
            command=lambda: messagebox.showinfo(
                "Email", "Email functionality would be implemented here"
            ),
        ).pack(side=tk.LEFT, padx=10)

    def save_text_ticket(self, ticket_text):
        """Save text ticket to a file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save E-Ticket",
        )

        if file_path:
            with open(file_path, "w") as f:
                f.write(ticket_text)
            messagebox.showinfo("Saved", f"Ticket saved to {file_path}")

    def search_customer(self):
        """Search for tickets by customer name"""
        search_name = self.search_name_var.get()

        if not search_name:
            messagebox.showerror("Error", "Enter a name to search")
            return

        # Clear previous results
        for item in self.search_results.get_children():
            self.search_results.delete(item)

        # Search for tickets by customer name
        tickets = self.db.get_tickets_by_customer_name(search_name)

        found = len(tickets) > 0
        for ticket in tickets:
            self.search_results.insert(
                "",
                "end",
                values=(
                    ticket["name"],
                    ticket["phone"],
                    ticket["date"],
                    ticket["seat_id"],
                    f"£{ticket['price']}",
                ),
            )

        if not found:
            messagebox.showinfo("Search Results", "No tickets found for this customer")

    def view_ticket_holders(self):
        """View all ticket holders for a performance"""
        performance_date = self.ticket_holders_var.get()

        if not performance_date:
            messagebox.showerror("Error", "Select a performance")
            return

        # Get performance ID
        performance = self.db.get_performance_by_date(performance_date)
        if not performance:
            messagebox.showerror("Error", "Invalid performance selected")
            return

        # Clear previous results
        for item in self.search_results.get_children():
            self.search_results.delete(item)

        # Get all tickets for this performance
        tickets = self.db.get_tickets_by_performance(performance["id"])

        # Sort by surname (we'll do this in Python since sqlite doesn't have easy last name extraction)
        # This converts to a list so we can sort it
        ticket_list = list(tickets)
        ticket_list.sort(
            key=lambda t: t["name"].split()[-1]
        )  # Sort by last word in name

        for ticket in ticket_list:
            self.search_results.insert(
                "",
                "end",
                values=(
                    ticket["name"],
                    ticket["phone"],
                    performance_date,
                    ticket["seat_id"],
                    f"£{ticket['price']}",
                ),
            )

    def generate_report(self):
        """Generate a report for a specific performance"""
        performance_date = self.report_performance_var.get()

        if not performance_date:
            messagebox.showerror("Error", "Select a performance")
            return

        # Get performance ID
        performance_data = self.db.get_performance_by_date(performance_date)
        if not performance_data:
            messagebox.showerror("Error", "Invalid performance selected")
            return

        performance_id = performance_data["id"]

        # Create a Performance object to access its methods
        performance = Performance(self.db, performance_id, performance_date)

        # Get ticket counts
        seat_counts = self.db.get_seat_counts(performance_id)
        total_tickets = seat_counts.get(1, 0)  # BOOKED = 1
        available_seats = seat_counts.get(0, 0)  # AVAILABLE = 0
        blocked_seats = seat_counts.get(2, 0)  # BLOCKED = 2

        # Calculate revenue
        total_revenue = self.db.get_total_revenue_by_performance(performance_id)

        # Get ticket counts by type
        type_counts = self.db.get_ticket_counts_by_type(performance_id)

        # Generate report
        report = f"Performance Report: {performance_date}\n"
        report += "=" * 50 + "\n\n"
        report += f"Tickets Sold/Allocated: {total_tickets}\n"
        report += f"Available Seats: {available_seats}\n"
        report += f"Blocked Seats: {blocked_seats}\n"
        report += f"Total Revenue: £{total_revenue:.2f}\n\n"
        report += "Ticket Type Breakdown:\n"
        report += f"Regular (£10): {type_counts['Regular']}\n"
        report += f"Under 18 (£5): {type_counts['Under 18']}\n"
        report += f"Over 65 (£5): {type_counts['Over 65']}\n"
        report += f"Special Guest (£0): {type_counts['Special Guest']}\n"

        # Display report
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, report)

    def view_seating(self):
        """View the seating layout for a performance"""
        performance_date = self.seating_performance_var.get()

        if not performance_date:
            messagebox.showerror("Error", "Select a performance")
            return

        # Get performance ID
        performance_data = self.db.get_performance_by_date(performance_date)
        if not performance_data:
            messagebox.showerror("Error", "Invalid performance selected")
            return

        performance_id = performance_data["id"]

        # Create a Performance object
        performance = Performance(self.db, performance_id, performance_date)

        # Clear canvas
        self.seating_canvas.delete("all")

        # Draw stage
        self.seating_canvas.create_rectangle(250, 20, 550, 60, fill="brown")
        self.seating_canvas.create_text(
            400, 40, text="STAGE", fill="white", font=("Arial", 12, "bold")
        )

        # Draw seats
        seat_width = 30
        seat_height = 30
        start_x = 100
        start_y = 100

        for row in range(10):
            for col in range(20):
                seat_id = f"{chr(65 + row)}{col + 1}"
                x = start_x + col * (seat_width + 5)
                y = start_y + row * (seat_height + 5)

                status = performance.get_seat_status(seat_id)

                if status == SEAT_STATUS.AVAILABLE:
                    color = "green"
                elif status == SEAT_STATUS.BOOKED:
                    color = "red"
                else:  # BLOCKED
                    color = "gray"

                self.seating_canvas.create_rectangle(
                    x,
                    y,
                    x + seat_width,
                    y + seat_height,
                    fill=color,
                    tags=f"seat_{seat_id}",
                )
                self.seating_canvas.create_text(
                    x + seat_width // 2,
                    y + seat_height // 2,
                    text=seat_id,
                    fill="white",
                    font=("Arial", 7),
                )

    def seat_clicked(self, event):
        """Handle click on a seat in the seating layout"""
        # Get clicked seat
        x, y = event.x, event.y

        # Check if click is on a seat
        for row in range(10):
            for col in range(20):
                seat_id = f"{chr(65 + row)}{col + 1}"
                seat_x = 100 + col * 35
                seat_y = 100 + row * 35

                if seat_x <= x <= seat_x + 30 and seat_y <= y <= seat_y + 30:
                    performance_date = self.seating_performance_var.get()
                    if not performance_date:
                        messagebox.showerror("Error", "Select a performance first")
                        return

                    # Get performance info
                    performance_data = self.db.get_performance_by_date(performance_date)
                    if not performance_data:
                        return

                    performance = Performance(
                        self.db, performance_data["id"], performance_date
                    )
                    status = performance.get_seat_status(seat_id)

                    if status == SEAT_STATUS.AVAILABLE:
                        # Set the selected performance and seat in booking tab
                        self.performance_var.set(performance_date)
                        self.seat_var.set(seat_id)
                        self.notebook.select(0)  # Switch to booking tab
                        return
                    elif status == SEAT_STATUS.BOOKED:
                        messagebox.showinfo(
                            "Seat Information", f"Seat {seat_id} is already booked"
                        )
                    else:
                        messagebox.showinfo(
                            "Seat Information", f"Seat {seat_id} is blocked"
                        )

    def get_performance_by_date(self, date):
        """Get a performance object by date"""
        performance_data = self.db.get_performance_by_date(date)
        if not performance_data:
            return None

        return Performance(self.db, performance_data["id"], date)


if __name__ == "__main__":
    root = tk.Tk()
    app = TheaterTicketSystem(root)
    root.mainloop()
