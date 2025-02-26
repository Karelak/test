from db_manager import DBManager
from models_sql import Customer, Performance, Ticket, SEAT_STATUS
import random
import datetime
import names  # If not installed, use: pip install names


def generate_phone_number():
    """Generate a random UK phone number"""
    formats = [
        "07{0}{1}{2} {3}{4}{5}{6}{7}{8}",
        "01{0}{1} {2}{3}{4} {5}{6}{7}{8}",
        "+44 7{0}{1}{2} {3}{4}{5}{6}{7}{8}",
    ]
    digits = [random.randint(0, 9) for _ in range(9)]
    return random.choice(formats).format(*digits)


def generate_random_seats(performance, count, exclude_seats=None):
    """Generate random seats for booking"""
    if exclude_seats is None:
        exclude_seats = []

    all_seats = []
    for row in range(10):
        for col in range(20):
            seat_id = f"{chr(65 + row)}{col + 1}"
            if seat_id not in exclude_seats:
                all_seats.append(seat_id)

    # Shuffle and return required number
    random.shuffle(all_seats)
    return all_seats[: min(count, len(all_seats))]


def populate_database(db_file="theater.db", reset=False):
    """Populate the database with sample data"""
    print(f"Initializing database: {db_file}")

    if reset:
        import os

        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"Removed existing database: {db_file}")

    # Initialize the database
    db = DBManager(db_file)

    # Get performances
    performances = db.get_performances()
    print(f"Found {len(performances)} performances in database")

    # Customer types with weights for random selection
    customer_types = {
        "Regular": 0.6,  # 60% regular customers
        "Under 18": 0.15,  # 15% under 18
        "Over 65": 0.15,  # 15% over 65
        "Special Guest": 0.1,  # 10% special guests
    }

    # Total tickets to generate per performance
    tickets_to_generate = 80  # Approximately 40% occupancy

    # Generate bookings for each performance
    for perf in performances:
        performance_id = perf["id"]
        perf_date = perf["date"]

        print(f"\nPopulating performance on {perf_date}...")
        performance = Performance(db, performance_id, perf_date)

        # Block some seats (e.g., for technical reasons)
        blocked_seats = generate_random_seats(performance, 5)
        for seat in blocked_seats:
            performance.block_seat(seat)
        print(f"- Blocked {len(blocked_seats)} seats: {', '.join(blocked_seats)}")

        # Book tickets
        booked_seats = []
        customers_generated = []

        # Create some families/groups that book adjacent seats
        num_groups = random.randint(5, 10)
        for _ in range(num_groups):
            # Group size between 2 and 5
            group_size = random.randint(2, 5)

            # Find a row with enough consecutive available seats
            found_seats = False
            for row in range(10):
                if found_seats:
                    break

                for start_col in range(21 - group_size):
                    consecutive_seats = []
                    for i in range(group_size):
                        seat = f"{chr(65 + row)}{start_col + i + 1}"
                        if seat in blocked_seats or seat in booked_seats:
                            consecutive_seats = []
                            break
                        consecutive_seats.append(seat)

                    if len(consecutive_seats) == group_size:
                        # Found enough consecutive seats
                        found_seats = True

                        # Create a family/group with same surname
                        surname = names.get_last_name()
                        for seat in consecutive_seats:
                            # Create customer
                            customer_type = random.choices(
                                list(customer_types.keys()),
                                weights=list(customer_types.values()),
                                k=1,
                            )[0]
                            first_name = names.get_first_name()
                            full_name = f"{first_name} {surname}"
                            phone = generate_phone_number()

                            # Add customer to database and create ticket
                            customer = Customer.create(
                                db, full_name, phone, customer_type
                            )

                            # Calculate price based on customer type
                            price = 0
                            if customer_type == "Regular":
                                price = 10
                            elif customer_type in ["Under 18", "Over 65"]:
                                price = 5

                            # Book seat and create ticket
                            if performance.book_seat(seat):
                                ticket = Ticket.create(
                                    db, customer, performance, seat, price
                                )
                                booked_seats.append(seat)
                                customers_generated.append(customer)

                        print(
                            f"- Booked {group_size} seats for {surname} family: {', '.join(consecutive_seats)}"
                        )
                        break

        # Book remaining individual seats
        remaining_to_book = tickets_to_generate - len(booked_seats)

        if remaining_to_book > 0:
            individual_seats = generate_random_seats(
                performance,
                remaining_to_book,
                exclude_seats=booked_seats + blocked_seats,
            )

            for seat in individual_seats:
                # Create customer
                customer_type = random.choices(
                    list(customer_types.keys()),
                    weights=list(customer_types.values()),
                    k=1,
                )[0]
                full_name = f"{names.get_first_name()} {names.get_last_name()}"
                phone = generate_phone_number()

                # Add customer to database and create ticket
                customer = Customer.create(db, full_name, phone, customer_type)

                # Calculate price based on customer type
                price = 0
                if customer_type == "Regular":
                    price = 10
                elif customer_type in ["Under 18", "Over 65"]:
                    price = 5

                # Book seat and create ticket
                if performance.book_seat(seat):
                    ticket = Ticket.create(db, customer, performance, seat, price)
                    booked_seats.append(seat)
                    customers_generated.append(customer)

            print(f"- Booked {len(individual_seats)} individual seats")

        # Counts for this performance
        seat_counts = db.get_seat_counts(performance_id)
        print(f"- Total seats booked: {seat_counts.get(1, 0)}")
        print(f"- Total seats blocked: {seat_counts.get(2, 0)}")
        print(f"- Available seats: {seat_counts.get(0, 0)}")

        # Calculate revenue
        revenue = db.get_total_revenue_by_performance(performance_id)
        print(f"- Total revenue: £{revenue:.2f}")

    # Overall database stats
    print("\nDatabase population complete!")
    print(f"Total performances: {len(db.get_performances())}")

    # Count all tickets
    db.cursor.execute("SELECT COUNT(*) as count FROM tickets")
    ticket_count = db.cursor.fetchone()["count"]
    print(f"Total tickets: {ticket_count}")

    # Count all customers
    db.cursor.execute("SELECT COUNT(*) as count FROM customers")
    customer_count = db.cursor.fetchone()["count"]
    print(f"Total customers: {customer_count}")

    # Total revenue
    db.cursor.execute("SELECT SUM(price) as total FROM tickets")
    total_revenue = db.cursor.fetchone()["total"] or 0
    print(f"Total revenue: £{total_revenue:.2f}")

    db.close()
    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Populate theater database with sample data"
    )
    parser.add_argument(
        "--reset", action="store_true", help="Reset the database before populating"
    )
    parser.add_argument("--db", default="theater.db", help="Path to the database file")

    args = parser.parse_args()

    try:
        import names
    except ImportError:
        print("The 'names' package is required. Installing...")
        import subprocess

        subprocess.check_call(["pip", "install", "names"])
        import names

    populate_database(args.db, args.reset)
