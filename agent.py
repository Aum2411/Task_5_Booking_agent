import os
from groq import Groq
from dotenv import load_dotenv
from typing import Dict, List
from database import TurfBookingDatabase
from datetime import datetime, timedelta
import json

# Load environment variables
load_dotenv()

class TurfBookingAgent:
    """AI-powered booking agent using Groq API"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.db = TurfBookingDatabase()
        self.db.initialize_dummy_turf()
        self.conversation_history = []
        self.model = "llama-3.3-70b-versatile"
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the AI agent"""
        turfs = self.db.get_all_turfs()
        turf_info = json.dumps(turfs, indent=2)
        
        return f"""You are a professional and friendly turf booking assistant for sports facility reservations. 
Your name is "BookMyTurf Assistant" and you help customers book turfs for sports activities.

Available Turfs:
{turf_info}

Your capabilities:
1. Provide information about available turfs, their amenities, and pricing
2. Help customers book time slots for their preferred dates
3. Check availability for specific dates and times
4. Handle booking cancellations
5. Answer questions about facilities, pricing, and policies

Guidelines:
- Be friendly, professional, and helpful
- Ask for required information politely: customer name, phone number, preferred date, and time slot
- Confirm all details before making a booking
- Provide clear information about pricing and availability
- Format dates as YYYY-MM-DD and times in 24-hour format (HH:00)
- If a slot is unavailable, suggest alternative times
- Always confirm booking details with booking ID

When a customer wants to book:
1. Ask for their name
2. Ask for their phone number
3. Ask for preferred date (today or future dates)
4. Ask for preferred time slot
5. Confirm availability
6. Confirm booking details
7. Create the booking

For cancellations:
- Ask for the booking ID
- Confirm cancellation

Always be conversational and natural in your responses."""

    def process_message(self, user_message: str) -> str:
        """Process user message and generate response"""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Check if user wants to perform specific actions
        response = self._handle_special_commands(user_message)
        if response:
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            return response
        
        # Get AI response
        try:
            messages = [
                {"role": "system", "content": self.get_system_prompt()}
            ] + self.conversation_history[-10:]  # Keep last 10 messages for context
            
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.7,
                max_tokens=1024,
            )
            
            ai_response = chat_completion.choices[0].message.content
            
            # Add AI response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response
            })
            
            return ai_response
            
        except Exception as e:
            error_message = f"I apologize, but I encountered an error: {str(e)}. Please try again."
            self.conversation_history.append({
                "role": "assistant",
                "content": error_message
            })
            return error_message
    
    def _handle_special_commands(self, message: str) -> str:
        """Handle special commands for booking operations"""
        message_lower = message.lower()
        
        # Check availability command
        if "check availability" in message_lower or "available slots" in message_lower:
            return self._get_availability_info()
        
        # View all bookings command
        if "show bookings" in message_lower or "view bookings" in message_lower or "my bookings" in message_lower:
            return self._get_all_bookings_info()
        
        return None
    
    def _get_availability_info(self) -> str:
        """Get availability information for today and tomorrow"""
        turfs = self.db.get_all_turfs()
        if not turfs:
            return "No turfs available at the moment."
        
        turf = turfs[0]
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        info = f"**{turf['name']}** - Availability Status\n\n"
        info += f"Price: ₹{turf['price_per_hour']}/hour\n\n"
        
        for date, date_label in [(today, "Today"), (tomorrow, "Tomorrow")]:
            info += f"**{date_label} ({date}):**\n"
            bookings = self.db.get_bookings_for_date(turf['id'], date)
            booked_slots = [b['time_slot'] for b in bookings if b['status'] == 'confirmed']
            
            available_slots = [slot for slot in turf['available_hours'] if slot not in booked_slots]
            
            if available_slots:
                info += f"Available slots: {', '.join(available_slots[:10])}"
                if len(available_slots) > 10:
                    info += f" and {len(available_slots) - 10} more"
                info += "\n\n"
            else:
                info += "No slots available\n\n"
        
        return info
    
    def _get_all_bookings_info(self) -> str:
        """Get all current bookings"""
        bookings = self.db.get_all_bookings()
        if not bookings:
            return "No bookings found."
        
        confirmed_bookings = [b for b in bookings if b['status'] == 'confirmed']
        if not confirmed_bookings:
            return "No confirmed bookings at the moment."
        
        info = "**Current Bookings:**\n\n"
        for booking in confirmed_bookings[-10:]:  # Show last 10 bookings
            info += f"🎫 **Booking ID:** {booking['booking_id']}\n"
            info += f"   Customer: {booking['customer_name']}\n"
            info += f"   Date: {booking['date']} at {booking['time_slot']}\n"
            info += f"   Amount: ₹{booking['total_amount']}\n\n"
        
        return info
    
    def create_booking_from_details(self, details: Dict) -> Dict:
        """Create a booking with provided details"""
        return self.db.create_booking(details)
    
    def cancel_booking_by_id(self, booking_id: str) -> bool:
        """Cancel a booking"""
        return self.db.cancel_booking(booking_id)
    
    def get_turf_info(self) -> List[Dict]:
        """Get information about available turfs"""
        return self.db.get_all_turfs()
