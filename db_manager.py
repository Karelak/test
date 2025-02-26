import sqlite3
import os
from datetime import datetime
from enum import Enum


class DBManager:
    def __init__(self, db_file="theater.db"):
        self.db_file = db_file
        self.conn = None
        self.cursor = None

        # Create the database if it doesn't exist
        self.create_database()

    def create_database(self):
        """Create the database and tables if they don't exist"""
        create_tables = not os.path.exists(self.db_file)

        # Connect to database
        self.connect()

        if create_tables:
            # Create tables
            self.cursor.execute("""
            CREATE TABLE performances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL
            )
            """)

            self.cursor.execute("""
            CREATE TABLE seats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                performance_id INTEGER NOT NULL,
                seat_id TEXT NOT NULL,
                status INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (performance_id) REFERENCES performances(id),
                UNIQUE (performance_id, seat_id)
            )
            """)

            self.cursor.execute("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                customer_type TEXT NOT NULL
            )
            """)

            self.cursor.execute("""
            CREATE TABLE tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                performance_id INTEGER NOT NULL,
                seat_id TEXT NOT NULL,
                price REAL NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (performance_id) REFERENCES performances(id)
            )
            """)

            # Initialize with default performances
            dates = ["2023-06-01", "2023-06-02", "2023-06-03"]
            for date in dates:
                self.add_performance(date)

            self.conn.commit()

    def connect(self):
        """Connect to the database"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()

    def close(self):
        """Close the database connection"""
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def commit(self):
        """Commit changes to the database"""
        if self.conn is not None:
            self.conn.commit()

    # Performance operations
    def add_performance(self, date):
        """Add a new performance to the database"""
        self.connect()
        self.cursor.execute(
            """
        INSERT INTO performances (date) VALUES (?)
        """,
            (date,),
        )

        performance_id = self.cursor.lastrowid

        # Initialize all seats for this performance
        for row in range(10):
            for col in range(20):
                seat_id = f"{chr(65 + row)}{col + 1}"
                self.cursor.execute(
                    """
                INSERT INTO seats (performance_id, seat_id, status)
                VALUES (?, ?, 0)
                """,
                    (performance_id, seat_id),
                )

        self.conn.commit()
        return performance_id

    def get_performances(self):
        """Get all performances from the database"""
        self.connect()
        self.cursor.execute("SELECT * FROM performances ORDER BY date")
        performances = self.cursor.fetchall()
        return performances

    def get_performance_by_date(self, date):
        """Get a performance by its date"""
        self.connect()
        self.cursor.execute("SELECT * FROM performances WHERE date = ?", (date,))
        return self.cursor.fetchone()

    def get_performance_by_id(self, performance_id):
        """Get a performance by its ID"""
        self.connect()
        self.cursor.execute(
            "SELECT * FROM performances WHERE id = ?", (performance_id,)
        )
        return self.cursor.fetchone()

    # Seat operations
    def get_seat_status(self, performance_id, seat_id):
        """Get the status of a seat for a performance"""
        self.connect()
        self.cursor.execute(
            """
        SELECT status FROM seats 
        WHERE performance_id = ? AND seat_id = ?
        """,
            (performance_id, seat_id),
        )
        result = self.cursor.fetchone()
        return result["status"] if result else 0  # Default to AVAILABLE (0)

    def set_seat_status(self, performance_id, seat_id, status):
        """Set the status of a seat for a performance"""
        self.connect()
        self.cursor.execute(
            """
        UPDATE seats SET status = ?
        WHERE performance_id = ? AND seat_id = ?
        """,
            (status, performance_id, seat_id),
        )
        self.conn.commit()

    def book_seat(self, performance_id, seat_id):
        """Book a seat for a performance"""
        current_status = self.get_seat_status(performance_id, seat_id)
        if current_status == 0:  # AVAILABLE
            self.set_seat_status(performance_id, seat_id, 1)  # BOOKED
            return True
        return False

    def block_seat(self, performance_id, seat_id):
        """Block a seat for a performance"""
        current_status = self.get_seat_status(performance_id, seat_id)
        if current_status != 1:  # Not BOOKED
            self.set_seat_status(performance_id, seat_id, 2)  # BLOCKED
            return True
        return False

    def get_available_seats(self, performance_id):
        """Get all available seats for a performance"""
        self.connect()
        self.cursor.execute(
            """
        SELECT seat_id FROM seats 
        WHERE performance_id = ? AND status = 0
        ORDER BY seat_id
        """,
            (performance_id,),
        )
        return [row["seat_id"] for row in self.cursor.fetchall()]

    def get_seat_counts(self, performance_id):
        """Get counts of available, booked, and blocked seats for a performance"""
        self.connect()
        self.cursor.execute(
            """
        SELECT status, COUNT(*) as count 
        FROM seats 
        WHERE performance_id = ? 
        GROUP BY status
        """,
            (performance_id,),
        )

        results = self.cursor.fetchall()
        counts = {0: 0, 1: 0, 2: 0}  # Default counts (AVAILABLE, BOOKED, BLOCKED)

        for row in results:
            counts[row["status"]] = row["count"]

        return counts

    # Customer operations
    def add_customer(self, name, phone, customer_type):
        """Add a new customer to the database"""
        self.connect()

        # Check if customer already exists
        self.cursor.execute(
            """
        SELECT id FROM customers 
        WHERE name = ? AND phone = ?
        """,
            (name, phone),
        )
        existing = self.cursor.fetchone()

        if existing:
            return existing["id"]

        # Add new customer
        self.cursor.execute(
            """
        INSERT INTO customers (name, phone, customer_type)
        VALUES (?, ?, ?)
        """,
            (name, phone, customer_type),
        )

        self.conn.commit()
        return self.cursor.lastrowid

    def get_customer(self, customer_id):
        """Get a customer by their ID"""
        self.connect()
        self.cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        return self.cursor.fetchone()

    # Ticket operations
    def add_ticket(self, customer_id, performance_id, seat_id, price):
        """Add a new ticket to the database"""
        self.connect()
        timestamp = datetime.now().isoformat()

        self.cursor.execute(
            """
        INSERT INTO tickets (customer_id, performance_id, seat_id, price, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """,
            (customer_id, performance_id, seat_id, price, timestamp),
        )

        self.conn.commit()
        return self.cursor.lastrowid

    def get_tickets_by_customer_name(self, name):
        """Get all tickets for a customer with matching name"""
        self.connect()
        self.cursor.execute(
            """
        SELECT t.*, c.name, c.phone, c.customer_type, p.date
        FROM tickets t
        JOIN customers c ON t.customer_id = c.id
        JOIN performances p ON t.performance_id = p.id
        WHERE LOWER(c.name) LIKE LOWER(?)
        ORDER BY p.date, t.seat_id
        """,
            (f"%{name}%",),
        )

        return self.cursor.fetchall()

    def get_tickets_by_performance(self, performance_id):
        """Get all tickets for a performance"""
        self.connect()
        self.cursor.execute(
            """
        SELECT t.*, c.name, c.phone, c.customer_type
        FROM tickets t
        JOIN customers c ON t.customer_id = c.id
        WHERE t.performance_id = ?
        ORDER BY c.name
        """,
            (performance_id,),
        )

        return self.cursor.fetchall()

    def get_total_revenue_by_performance(self, performance_id):
        """Get the total revenue for a performance"""
        self.connect()
        self.cursor.execute(
            """
        SELECT SUM(price) as total_revenue
        FROM tickets
        WHERE performance_id = ?
        """,
            (performance_id,),
        )

        result = self.cursor.fetchone()
        return (
            result["total_revenue"]
            if result and result["total_revenue"] is not None
            else 0
        )

    def get_ticket_counts_by_type(self, performance_id):
        """Get counts of tickets sold by customer type for a performance"""
        self.connect()
        self.cursor.execute(
            """
        SELECT c.customer_type, COUNT(*) as count
        FROM tickets t
        JOIN customers c ON t.customer_id = c.id
        WHERE t.performance_id = ?
        GROUP BY c.customer_type
        """,
            (performance_id,),
        )

        results = self.cursor.fetchall()
        counts = {"Regular": 0, "Under 18": 0, "Over 65": 0, "Special Guest": 0}

        for row in results:
            counts[row["customer_type"]] = row["count"]

        return counts
