import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class TurfBookingDatabase:
    """Simple JSON-based database for turf bookings"""
    
    def __init__(self, db_file: str = "bookings.json"):
        self.db_file = db_file
        self.data = self.load_data()
    
    def load_data(self) -> Dict:
        """Load data from JSON file"""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                return json.load(f)
        return {
            "turfs": [],
            "bookings": []
        }
    
    def save_data(self):
        """Save data to JSON file"""
        with open(self.db_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def initialize_dummy_turf(self):
        """Initialize dummy turf data"""
        if not self.data["turfs"]:
            self.data["turfs"] = [
                {
                    "id": "turf_001",
                    "name": "Green Valley Sports Arena",
                    "location": "Downtown, Sector 21, Main Street",
                    "description": "Premium artificial turf with floodlights, perfect for football, cricket, and other sports",
                    "amenities": ["Floodlights", "Changing Rooms", "Parking", "Water Facility", "First Aid"],
                    "size": "100x60 feet",
                    "surface_type": "Artificial Grass",
                    "price_per_hour": 1500,
                    "available_hours": ["06:00", "07:00", "08:00", "09:00", "10:00", "11:00", 
                                       "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", 
                                       "18:00", "19:00", "20:00", "21:00", "22:00"],
                    "images": ["turf1.jpg", "turf2.jpg"],
                    "rating": 4.5,
                    "total_reviews": 128
                }
            ]
            self.save_data()
    
    def get_all_turfs(self) -> List[Dict]:
        """Get all available turfs"""
        return self.data["turfs"]
    
    def get_turf_by_id(self, turf_id: str) -> Optional[Dict]:
        """Get specific turf by ID"""
        for turf in self.data["turfs"]:
            if turf["id"] == turf_id:
                return turf
        return None
    
    def get_bookings_for_date(self, turf_id: str, date: str) -> List[Dict]:
        """Get all bookings for a specific turf and date"""
        bookings = []
        for booking in self.data["bookings"]:
            if booking["turf_id"] == turf_id and booking["date"] == date:
                bookings.append(booking)
        return bookings
    
    def check_availability(self, turf_id: str, date: str, time_slot: str) -> bool:
        """Check if a time slot is available"""
        bookings = self.get_bookings_for_date(turf_id, date)
        for booking in bookings:
            if booking["time_slot"] == time_slot and booking["status"] == "confirmed":
                return False
        return True
    
    def create_booking(self, booking_data: Dict) -> Dict:
        """Create a new booking"""
        booking_id = f"BK{len(self.data['bookings']) + 1:04d}"
        booking = {
            "booking_id": booking_id,
            "turf_id": booking_data["turf_id"],
            "customer_name": booking_data["customer_name"],
            "customer_phone": booking_data["customer_phone"],
            "customer_email": booking_data.get("customer_email", ""),
            "date": booking_data["date"],
            "time_slot": booking_data["time_slot"],
            "duration": booking_data.get("duration", 1),
            "status": "confirmed",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_amount": booking_data.get("total_amount", 0)
        }
        self.data["bookings"].append(booking)
        self.save_data()
        return booking
    
    def cancel_booking(self, booking_id: str) -> bool:
        """Cancel a booking"""
        for booking in self.data["bookings"]:
            if booking["booking_id"] == booking_id:
                booking["status"] = "cancelled"
                self.save_data()
                return True
        return False
    
    def get_booking_by_id(self, booking_id: str) -> Optional[Dict]:
        """Get booking by ID"""
        for booking in self.data["bookings"]:
            if booking["booking_id"] == booking_id:
                return booking
        return None
    
    def get_all_bookings(self) -> List[Dict]:
        """Get all bookings"""
        return self.data["bookings"]
