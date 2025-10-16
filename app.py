from flask import Flask, render_template, request, jsonify
from agent import TurfBookingAgent
from datetime import datetime
import os

app = Flask(__name__)
agent = TurfBookingAgent()

@app.route('/')
def index():
    """Render the main page"""
    turfs = agent.get_turf_info()
    return render_template('index.html', turfs=turfs)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Process message through agent
        response = agent.process_message(user_message)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().strftime('%H:%M')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/turfs', methods=['GET'])
def get_turfs():
    """Get all turfs"""
    turfs = agent.get_turf_info()
    return jsonify(turfs)

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    """Get all bookings"""
    bookings = agent.db.get_all_bookings()
    return jsonify(bookings)

@app.route('/api/book', methods=['POST'])
def create_booking():
    """Create a new booking"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['turf_id', 'customer_name', 'customer_phone', 'date', 'time_slot']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check availability
        if not agent.db.check_availability(data['turf_id'], data['date'], data['time_slot']):
            return jsonify({'error': 'This time slot is already booked'}), 400
        
        # Get turf info for pricing
        turf = agent.db.get_turf_by_id(data['turf_id'])
        if not turf:
            return jsonify({'error': 'Turf not found'}), 404
        
        # Calculate total amount
        duration = data.get('duration', 1)
        data['total_amount'] = turf['price_per_hour'] * duration
        
        # Create booking
        booking = agent.create_booking_from_details(data)
        
        return jsonify({
            'success': True,
            'booking': booking,
            'message': 'Booking confirmed successfully!'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cancel/<booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    """Cancel a booking"""
    try:
        success = agent.cancel_booking_by_id(booking_id)
        if success:
            return jsonify({
                'success': True,
                'message': 'Booking cancelled successfully'
            })
        else:
            return jsonify({'error': 'Booking not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/availability/<turf_id>/<date>', methods=['GET'])
def check_availability(turf_id, date):
    """Check availability for a specific date"""
    try:
        turf = agent.db.get_turf_by_id(turf_id)
        if not turf:
            return jsonify({'error': 'Turf not found'}), 404
        
        bookings = agent.db.get_bookings_for_date(turf_id, date)
        booked_slots = [b['time_slot'] for b in bookings if b['status'] == 'confirmed']
        available_slots = [slot for slot in turf['available_hours'] if slot not in booked_slots]
        
        return jsonify({
            'available_slots': available_slots,
            'booked_slots': booked_slots,
            'price_per_hour': turf['price_per_hour']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
