from datetime import datetime, timedelta


class SmartPricing:
    def __init__(self, base_price=10, reduced_price=5):
        self.base_price = base_price
        self.reduced_price = reduced_price

    def calculate_price(
        self, performance, performance_date, customer_type, current_date=None
    ):
        """
        Calculate ticket price based on:
        - Customer type
        - Days until performance
        - Percentage of seats already sold
        """
        # Special guest always gets free ticket
        if customer_type == "Special Guest":
            return 0

        # Under 18 and Over 65 get reduced price as a starting point
        if customer_type in ["Under 18", "Over 65"]:
            price = self.reduced_price
        else:
            price = self.base_price

        # Calculate days until performance
        if current_date is None:
            current_date = datetime.now()

        performance_date_obj = datetime.strptime(performance_date, "%Y-%m-%d")
        days_until_performance = (performance_date_obj - current_date).days

        # Calculate seat occupancy percentage
        total_seats = 10 * 20  # 10 rows of 20 seats
        booked_seats = performance.get_booked_seats_count()
        occupancy_percentage = (booked_seats / total_seats) * 100

        # Apply dynamic pricing factors

        # Early bird discount (more than 30 days before)
        if days_until_performance > 30:
            price *= 0.9  # 10% discount

        # Last minute pricing (less than 7 days before)
        elif days_until_performance < 7:
            if occupancy_percentage < 60:
                price *= 0.85  # 15% discount to fill empty seats
            elif occupancy_percentage > 80:
                price *= 1.15  # 15% premium for high demand

        # High demand pricing (more than 70% seats sold)
        if occupancy_percentage > 70 and days_until_performance > 7:
            price *= 1.1  # 10% premium

        # Very high demand (more than 90% seats sold)
        if occupancy_percentage > 90:
            price *= 1.2  # Additional 20% premium

        # Round to nearest pound/half-pound
        price = round(price * 2) / 2

        # Never go below minimum price for category
        if customer_type in ["Under 18", "Over 65"]:
            price = max(price, self.reduced_price)
        else:
            price = max(price, self.base_price)

        return price

    def get_price_explanation(self, performance, performance_date, customer_type):
        """Generate an explanation of how the price was calculated"""
        base = self.base_price if customer_type == "Regular" else self.reduced_price

        explanation = f"Base price for {customer_type}: £{base}\n"

        # Add explanation of factors that affected price
        current_date = datetime.now()
        performance_date_obj = datetime.strptime(performance_date, "%Y-%m-%d")
        days_until_performance = (performance_date_obj - current_date).days

        total_seats = 10 * 20
        booked_seats = performance.get_booked_seats_count()
        occupancy_percentage = (booked_seats / total_seats) * 100

        if days_until_performance > 30:
            explanation += "Early bird discount: -10%\n"
        elif days_until_performance < 7:
            if occupancy_percentage < 60:
                explanation += "Last minute discount: -15%\n"
            elif occupancy_percentage > 80:
                explanation += "Last minute high demand: +15%\n"

        if occupancy_percentage > 70 and days_until_performance > 7:
            explanation += "High demand premium: +10%\n"

        if occupancy_percentage > 90:
            explanation += "Very high demand premium: +20%\n"

        # Add final price
        final_price = self.calculate_price(performance, performance_date, customer_type)
        explanation += f"\nFinal price: £{final_price}"

        return explanation
