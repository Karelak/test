from db_manager import DBManager

if __name__ == "__main__":
    print("Initializing theater database...")
    db = DBManager("theater.db")

    # Get all performances to verify
    performances = db.get_performances()
    print(f"Created database with {len(performances)} performances:")
    for perf in performances:
        print(f"- Performance on {perf['date']}")
        # Count seats
        counts = db.get_seat_counts(perf["id"])
        print(f"  Available seats: {counts.get(0, 0)}")

    print("\nDatabase initialization complete.")
    print("You can now run main_sql.py to use the SQL-based application.")
