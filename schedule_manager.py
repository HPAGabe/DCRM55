class ScheduleManager:
    def __init__(self):
        # Dictionary to store customer schedules
        # Each customer can have a list of schedules
        self.customers = {}

    def add_schedule(self, customer_id, schedule):
        # If customer does not exist, create a new entry
        if customer_id not in self.customers:
            self.customers[customer_id] = []
        self.customers[customer_id].append(schedule)
        print(f"Added schedule for customer {customer_id}: {schedule}")

    def update_schedule(self, customer_id, schedule_index, new_schedule):
        # Ensure the customer and schedule index exist
        if customer_id in self.customers and 0 <= schedule_index < len(self.customers[customer_id]):
            self.customers[customer_id][schedule_index] = new_schedule
            print(f"Updated schedule {schedule_index} for customer {customer_id}: {new_schedule}")
        else:
            print(f"Schedule {schedule_index} for customer {customer_id} does not exist.")

    def archive_schedule(self, customer_id, schedule_index):
        # Ensure the customer and schedule index exist
        if customer_id in self.customers and 0 <= schedule_index < len(self.customers[customer_id]):
            # Archive the schedule by marking it as 'archived'
            archived_schedule = self.customers[customer_id].pop(schedule_index)
            print(f"Archived schedule {schedule_index} for customer {customer_id}: {archived_schedule}")
        else:
            print(f"Schedule {schedule_index} for customer {customer_id} does not exist.")

    def get_schedules(self, customer_id):
        # Retrieve schedules for a customer
        if customer_id in self.customers:
            return self.customers[customer_id]
        else:
            return f"No schedules found for customer {customer_id}"
