const testimonials = [
    {
    name: "David Tyler",
    location: "London, UK",
    rating: 4.8,
    text: "StocksCo helped me start investing without stress. I now buy U.S. stocks weekly with small amounts, and the app's insights make everything easy to understand.",
    image: "../static/images/david.png"
  },
  {
    name: "Kathleen Perry",
    location: "Austin, TX",
    rating: 4.8,
    text: "What I love most is the speed and transparency. Funding my account takes seconds, and withdrawals hit my bank quickly.",
    image: "../static/images/kathleen.png"
  },
  {
    name: "Kelvin M.",
    location: "Chicago, Illinois",
    rating: 4.8,
    text: "Security was my biggest concern, but StocksCo gives me peace of mind. The 2FA and real-time notifications assure me that my money is protected.",
    image: "../static/images/kelvin.png"
  }, 
  {
    name: "John M.",
    location: "Miami, Florida",
    rating: 4.8,
    text: "I've tried multiple platforms, but StocksCo stands out for its simple interface and clear pricing. No hidden fees, just honest investing.",
    image: "../static/images/john.png"
  },
  {
    name: "John D.",
    location: "Las Vegas, NV",
    rating: 4.8,
    text: "StocksCo helped me start investing without stress. I now buy U.S. stocks weekly with small amounts, and the app's insights make everything easy to understand.",
    image: "../static/images/johnD.png"
  },
  {
    name: "Martin Westwood",
    location: "Las Vegas, NV",
    rating: 4.8,
    text: "StocksCo helped me start investing without stress. I now buy U.S. stocks weekly with small amounts, and the app's insights make everything easy to understand.",
    image: "../static/images/johnD.png"
  },
]
const duplicatedTestimonials = [...testimonials, ...testimonials];


function createTestimonialCard(testimonials) {
    return `<div class="testimonial-scroll-item">
                <div class="testimonial-card">
                    <div class="d-flex align-items-center mb-3">
                        <span class="star-rating">★ ★ ★ ★ ★</span>
                        <span class="rating-number">${testimonials.rating}</span>
                    </div>
                    <p class="mb-4 flex-grow-1">${testimonials.text}</p>
                    <div class="d-flex align-items-center gap-3">
                        <img src=${testimonials.image} alt="John D" class="testimonial-avatar">
                        <div>
                            <h6 class="mb-0 fw-bold">${testimonials.name}</h6>
                            <p class="text-muted small mb-0">${testimonials.location}</p>
                        </div>
                    </div>
                </div>
            </div>`;
}


function renderTestimonials() {
  const container = document.getElementById('testimonials-container');
  const html = duplicatedTestimonials.map(t => createTestimonialCard(t)).join('');
  container.innerHTML = html;
}

renderTestimonials();