# Turf Booking Agent - AI-Powered Appointment Scheduler

A sophisticated turf booking system powered by Groq AI for intelligent conversational booking, built with Python Flask, HTML, and advanced CSS.

## 🌟 Features

- **AI-Powered Booking Assistant**: Natural language processing using Groq API (LLaMA 3.1)
- **Beautiful Modern UI**: Advanced CSS with gradients, animations, and responsive design
- **Real-time Chat Interface**: Interactive chat for seamless booking experience
- **Smart Availability Checker**: Check available time slots instantly
- **Booking Management**: Create, view, and cancel bookings
- **Dummy Turf Data**: Pre-configured "Green Valley Sports Arena" with complete details

## 📋 Requirements

- Python 3.8+
- Groq API Key
- Flask
- Modern web browser

## 🚀 Installation

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Environment Setup**:
The `.env` file is already configured with your Groq API key.

3. **Run the Application**:
```bash
python app.py
```

4. **Access the Application**:
Open your browser and navigate to:
```
http://localhost:5000
```

## 📁 Project Structure

```
Task_5/
├── app.py                  # Flask application (main server)
├── agent.py                # Groq AI booking agent
├── database.py             # JSON-based database handler
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (API key)
├── .gitignore             # Git ignore file
├── bookings.json          # Database file (auto-created)
├── templates/
│   └── index.html         # Main HTML template
└── static/
    ├── css/
    │   └── style.css      # Advanced CSS styling
    └── js/
        └── script.js      # Frontend JavaScript
```

## 🎯 Dummy Turf Details

**Green Valley Sports Arena**
- **Location**: Downtown, Sector 21, Main Street
- **Size**: 100x60 feet
- **Surface**: Artificial Grass
- **Price**: ₹1500/hour
- **Amenities**: Floodlights, Changing Rooms, Parking, Water Facility, First Aid
- **Hours**: 06:00 AM - 11:00 PM
- **Rating**: 4.5/5 (128 reviews)

## 💬 How to Use the Booking Agent

1. **Start a Conversation**: Type your query in the chat interface
2. **Book a Turf**: Say "I want to book a turf" or click "Book Now"
3. **Provide Details**: The AI will ask for:
   - Your name
   - Phone number
   - Preferred date (YYYY-MM-DD format)
   - Time slot (HH:00 format)
4. **Confirm Booking**: Review details and confirm
5. **Get Booking ID**: Receive confirmation with booking ID

## 🔧 API Endpoints

- `GET /` - Main page
- `POST /chat` - Chat with AI agent
- `GET /api/turfs` - Get all turfs
- `GET /api/bookings` - Get all bookings
- `POST /api/book` - Create new booking
- `POST /api/cancel/<booking_id>` - Cancel booking
- `GET /api/availability/<turf_id>/<date>` - Check availability

## 🎨 Features Showcase

### Advanced CSS Features:
- Custom CSS variables for theming
- Gradient backgrounds and text effects
- Smooth animations and transitions
- Glassmorphism effects
- Responsive grid layouts
- Custom scrollbar styling
- Intersection Observer animations
- Hover effects and transformations

### AI Capabilities:
- Natural language understanding
- Context-aware responses
- Booking validation
- Availability checking
- Conversational booking flow
- Error handling and suggestions

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop computers (1920px+)
- Laptops (1024px+)
- Tablets (768px+)
- Mobile phones (320px+)

## 🔐 Security Notes

- API key is stored in `.env` file (included in `.gitignore`)
- Input validation on both frontend and backend
- Sanitized user inputs
- CORS protection

## 🛠️ Customization

### Adding More Turfs:
Edit the `initialize_dummy_turf()` method in `database.py`

### Changing AI Model:
Modify the `model` variable in `agent.py`

### Styling:
Update CSS variables in `style.css` root section

## 📊 Database Schema

### Turfs:
```json
{
  "id": "string",
  "name": "string",
  "location": "string",
  "description": "string",
  "amenities": ["array"],
  "size": "string",
  "surface_type": "string",
  "price_per_hour": number,
  "available_hours": ["array"],
  "rating": number,
  "total_reviews": number
}
```

### Bookings:
```json
{
  "booking_id": "string",
  "turf_id": "string",
  "customer_name": "string",
  "customer_phone": "string",
  "customer_email": "string",
  "date": "string",
  "time_slot": "string",
  "duration": number,
  "status": "string",
  "created_at": "string",
  "total_amount": number
}
```

## 🎉 Future Enhancements

- Payment integration
- Email notifications
- SMS confirmations
- User authentication
- Multiple turf support
- Review and rating system
- Calendar view
- PDF booking receipts
- Recurring bookings

## 📞 Support

For issues or questions, contact: info@bookmyturf.com

## 📄 License

This project is open source and available for educational purposes.

---

**Built with ❤️ using Groq AI, Flask, HTML, and Advanced CSS**
