// ==================== GLOBAL VARIABLES ====================
let currentTurfId = null;
let currentTurfName = null;

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    // Initialize chat input
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    // Load bookings
    loadBookings();
    
    // Smooth scroll for navigation links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth' });
                
                // Update active link
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });
    
    // Scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe turf cards
    document.querySelectorAll('.turf-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'all 0.6s ease';
        observer.observe(card);
    });
});

// ==================== NAVIGATION ====================
function scrollToChat() {
    const chatSection = document.getElementById('chat');
    if (chatSection) {
        chatSection.scrollIntoView({ behavior: 'smooth' });
    }
}

// ==================== CHAT FUNCTIONALITY ====================
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Disable input while processing
    input.disabled = true;
    document.getElementById('sendBtn').disabled = true;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    
    // Clear input
    input.value = '';
    
    try {
        // Send message to backend
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            throw new Error('Failed to send message');
        }
        
        const data = await response.json();
        
        // Add bot response to chat
        setTimeout(() => {
            addMessageToChat(data.response, 'bot');
        }, 500);
        
    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('Sorry, I encountered an error. Please try again.', 'bot');
    } finally {
        // Re-enable input
        input.disabled = false;
        document.getElementById('sendBtn').disabled = false;
        input.focus();
    }
}

function sendQuickMessage(message) {
    const input = document.getElementById('chatInput');
    input.value = message;
    sendMessage();
}

function addMessageToChat(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.innerHTML = sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Format message with markdown-like syntax
    const formattedMessage = formatMessage(message);
    contentDiv.innerHTML = formattedMessage;
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    contentDiv.appendChild(timeDiv);
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatMessage(message) {
    // Convert **text** to bold
    message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert line breaks to <br>
    message = message.replace(/\n/g, '<br>');
    
    // Convert bullet points
    message = message.replace(/^- (.*?)$/gm, '• $1');
    
    return message;
}

// ==================== BOOKING FUNCTIONALITY ====================
function bookTurf(turfId, turfName) {
    currentTurfId = turfId;
    currentTurfName = turfName;
    
    scrollToChat();
    
    setTimeout(() => {
        const input = document.getElementById('chatInput');
        input.value = `I want to book ${turfName}`;
        sendMessage();
    }, 500);
}

async function loadBookings() {
    const container = document.getElementById('bookingsContainer');
    
    try {
        const response = await fetch('/api/bookings');
        
        if (!response.ok) {
            throw new Error('Failed to load bookings');
        }
        
        const bookings = await response.json();
        
        // Filter confirmed bookings
        const confirmedBookings = bookings.filter(b => b.status === 'confirmed');
        
        if (confirmedBookings.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-calendar-times"></i>
                    <h3>No Bookings Found</h3>
                    <p>You don't have any bookings yet. Book a turf to get started!</p>
                    <button class="cta-btn" onclick="scrollToChat()" style="margin-top: 1rem;">
                        <i class="fas fa-calendar-plus"></i> Book Now
                    </button>
                </div>
            `;
            return;
        }
        
        // Display bookings
        container.innerHTML = confirmedBookings.map(booking => `
            <div class="booking-card">
                <div class="booking-header">
                    <span class="booking-id">🎫 ${booking.booking_id}</span>
                    <span class="booking-status ${booking.status}">${booking.status.toUpperCase()}</span>
                </div>
                <div class="booking-details">
                    <div class="detail-row">
                        <span class="detail-label">Customer:</span>
                        <span class="detail-value">${booking.customer_name}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Phone:</span>
                        <span class="detail-value">${booking.customer_phone}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Date:</span>
                        <span class="detail-value">${booking.date}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Time:</span>
                        <span class="detail-value">${booking.time_slot}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Amount:</span>
                        <span class="detail-value">₹${booking.total_amount}</span>
                    </div>
                </div>
                <div class="booking-actions">
                    <button class="cancel-btn" onclick="cancelBooking('${booking.booking_id}')">
                        <i class="fas fa-times-circle"></i> Cancel Booking
                    </button>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading bookings:', error);
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Error Loading Bookings</h3>
                <p>Please try again later.</p>
            </div>
        `;
    }
}

async function cancelBooking(bookingId) {
    if (!confirm('Are you sure you want to cancel this booking?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/cancel/${bookingId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to cancel booking');
        }
        
        const data = await response.json();
        
        // Show success message
        alert(data.message);
        
        // Reload bookings
        loadBookings();
        
        // Add message to chat
        addMessageToChat(`Booking ${bookingId} has been cancelled successfully.`, 'bot');
        
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to cancel booking. Please try again.');
    }
}

// ==================== UTILITY FUNCTIONS ====================
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// ==================== NAVBAR SCROLL EFFECT ====================
let lastScroll = 0;
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 100) {
        navbar.style.background = 'rgba(255, 255, 255, 0.98)';
        navbar.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.15)';
    } else {
        navbar.style.background = 'rgba(255, 255, 255, 0.95)';
        navbar.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
    }
    
    lastScroll = currentScroll;
});

// ==================== SECTION OBSERVER ====================
const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const id = entry.target.getAttribute('id');
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${id}`) {
                    link.classList.add('active');
                }
            });
        }
    });
}, { threshold: 0.5 });

document.querySelectorAll('section[id]').forEach(section => {
    sectionObserver.observe(section);
});
