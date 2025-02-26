from enum import Enum
from datetime import datetime
import hashlib


class SEAT_STATUS(Enum):
    AVAILABLE = 0
    BOOKED = 1
    BLOCKED = 2


class Performance:
    def __init__(self, db_manager, performance_id=None, date=None):
        self.db_manager = db_manager
        self.id = performance_id
        self.date = date

        if self.id is not None and not self.date:
            # Load from database
            perf = self.db_manager.get_performance_by_id(self.id)
            if perf:
                self.date = perf["date"]

    def get_seat_status(self, seat_id):
        return SEAT_STATUS(self.db_manager.get_seat_status(self.id, seat_id))

    def book_seat(self, seat_id):
        return self.db_manager.book_seat(self.id, seat_id)

    def block_seat(self, seat_id):
        return self.db_manager.block_seat(self.id, seat_id)

    def get_available_seats(self):
        return self.db_manager.get_available_seats(self.id)

    def get_available_seats_count(self):
        counts = self.db_manager.get_seat_counts(self.id)
        return counts.get(0, 0)  # AVAILABLE = 0

    def get_booked_seats_count(self):
        counts = self.db_manager.get_seat_counts(self.id)
        return counts.get(1, 0)  # BOOKED = 1

    def check_middle_seat(self, seat_id):
        """Checks if booking this seat would leave a single seat in the middle of the row"""
        # Extract row and column
        row = seat_id[0]
        col = int(seat_id[1:])

        # Check if booking this would leave a single seat
        left_seat_id = f"{row}{col - 1}" if col > 1 else None
        right_seat_id = f"{row}{col + 1}" if col < 20 else None

        if not left_seat_id or not right_seat_id:
            return False  # Edge seats don't create middle problems

        left_status = self.get_seat_status(left_seat_id) if left_seat_id else None
        right_status = self.get_seat_status(right_seat_id) if right_seat_id else None

        # Check if this would create a single seat
        if left_status == SEAT_STATUS.AVAILABLE and right_status == SEAT_STATUS.BOOKED:
            return True

        if left_status == SEAT_STATUS.BOOKED and right_status == SEAT_STATUS.AVAILABLE:
            return True

        return False


class Customer:
    def __init__(
        self, db_manager, customer_id=None, name=None, phone=None, customer_type=None
    ):
        self.db_manager = db_manager
        self.id = customer_id
        self.name = name
        self.phone = phone
        self.customer_type = customer_type

        if self.id is not None and not self.name:
            # Load from database
            customer = self.db_manager.get_customer(self.id)
            if customer:
                self.name = customer["name"]
                self.phone = customer["phone"]
                self.customer_type = customer["customer_type"]

    @classmethod
    def create(cls, db_manager, name, phone, customer_type):
        """Create a new customer or retrieve existing one"""
        customer_id = db_manager.add_customer(name, phone, customer_type)
        return cls(db_manager, customer_id, name, phone, customer_type)


class Ticket:
    def __init__(
        self,
        db_manager,
        ticket_id=None,
        customer=None,
        performance=None,
        seat_id=None,
        price=None,
        timestamp=None,
    ):
        self.db_manager = db_manager
        self.id = ticket_id
        self.customer = customer
        self.performance = performance
        self.seat_id = seat_id
        self.price = price
        self.timestamp = timestamp or datetime.now().isoformat()

    @classmethod
    def create(cls, db_manager, customer, performance, seat_id, price):
        """Create a new ticket"""
        ticket_id = db_manager.add_ticket(customer.id, performance.id, seat_id, price)
        return cls(db_manager, ticket_id, customer, performance, seat_id, price)

    def generate_e_ticket(self):
        """Generate an electronic ticket that can be emailed or printed"""
        # Generate a unique ticket ID based on data
        unique_id = (
            hashlib.md5(f"{self.timestamp}{self.customer.name}{self.seat_id}".encode())
            .hexdigest()[:8]
            .upper()
        )

        ticket_text = f"""
        ====================================================
                    THEATER PERFORMANCE TICKET
        ====================================================
        
        Performance Date: {self.performance.date}
        Seat: {self.seat_id}
        
        Customer: {self.customer.name}
        Phone: {self.customer.phone}
        
        Price Paid: £{self.price}
        
        Ticket ID: {unique_id}
        
        Please present this ticket at the entrance.
        Thank you for your support!
        ====================================================
        """
        return ticket_text
