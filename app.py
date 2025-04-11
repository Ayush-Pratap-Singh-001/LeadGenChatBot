from flask import Flask, render_template, request, jsonify, session
import openai
import sqlite3
import os
import re
import secrets
from flask_session import Session

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# OpenRouter API setup
API_KEY = ""
client = openai.OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

KNOWLEDGE_BASE = """
Forma Creations: Your Handmade Haven
Forma Creations is an online marketplace that brings together a diverse collection of unique, handcrafted goods made by skilled artisans. Our platform offers customers a chance to discover meaningful, sustainable, and creative pieces while supporting independent makers. Whether you're shopping for yourself or a special gift, you'll find a wide variety of handmade items that tell a story and make a difference.
Products
Forma Creations specializes in unique, handcrafted goods created by independent artisans. Our diverse product range caters to various tastes and needs, emphasizing quality, sustainability, and the personal touch of handmade craftsmanship. We offer products across several main categories:
•	Jewelry & Accessories: Discover exquisite, handcrafted jewelry and stylish accessories.
o	Necklaces: Find a variety of necklace styles, from delicate pendants ($15-$45) and minimalist chains ($20-$60) to bold statement pieces ($50-$150) and beaded necklaces ($25-$75). Materials range from precious metals like sterling silver ($40+) and gold ($100+) to natural materials such as gemstones ($30+), wood ($10-$30), and leather ($15-$50).
o	Earrings: Explore handcrafted earrings in diverse designs, including studs ($10-$30), hoops ($15-$40), dangles ($20-$60), and chandelier earrings ($30-$80). Earring materials include metals ($15+), beads ($10-$35), glass ($12-$40), and polymer clay ($8-$25).
o	Bracelets: Browse our collection of bracelets, featuring beaded bracelets ($15-$40), cuff bracelets ($30-$80), chain bracelets ($25-$70), and woven bracelets ($10-$30). Artisans use various techniques, including wire wrapping, bead weaving, and metalwork.
o	Scarves: Add a touch of handmade elegance with our unique scarves. Choose from knitted scarves ($30-$80), woven scarves ($25-$70), silk scarves ($40-$120), and hand-dyed scarves ($35-$90) in a variety of colors and patterns.
o	Hats: Find handcrafted hats for all seasons, including knit hats ($20-$50), beanies ($15-$40), sun hats ($25-$60), and fedoras ($40-$100). Materials include wool ($30+), cotton ($20+), linen ($35+), and felt ($40+).
•	Home Decor: Enhance your living space with our handcrafted home decor items.
o	Wall Art: Decorate your walls with original paintings ($50-$500+), prints ($20-$100), macrame wall hangings ($30-$150), and handcrafted tapestries ($80-$300+). Styles range from abstract art to nature-inspired pieces.
o	Pottery: Discover unique ceramic pieces, including vases ($25-$80), bowls ($15-$60), mugs ($12-$35), and planters ($20-$70). Artisans use various techniques, such as wheel throwing and hand building, and glazes in a wide array of colors and finishes.
o	Candles: Create a cozy ambiance with our handcrafted candles. Choose from soy candles ($10-$30), beeswax candles ($15-$40), and scented candles ($12-$35) in various fragrances and container styles.
o	Cushions: Add comfort and style to your furniture with our handmade cushions. Find cushions in various fabrics, including cotton ($20-$50), linen ($25-$60), and velvet ($30-$70), with unique patterns and embroidery.
•	Apparel & Textiles: Express your personal style with our handcrafted clothing and textiles.
o	Hand-knit Clothing: Find cozy and stylish hand-knit sweaters ($80-$250+), cardigans ($70-$200+), scarves ($30-$80), and hats ($20-$50). Materials include wool ($50+), alpaca ($70+), and cotton yarns ($40+).
o	Custom-made T-shirts: Design your own unique t-shirts or choose from designs created by independent artists ($25-$60). We offer a variety of sizes, colors, and fabric options.
•	Stationery & Paper Goods: Discover handcrafted stationery for all your writing and gifting needs.
o	Journals: Find handcrafted journals with unique covers and high-quality paper ($15-$50). Choose from lined journals, blank journals, and sketchbooks.
o	Invitations: Make a lasting impression with our handcrafted invitations for weddings, parties, and other special events (price varies per set, $3-$10+ per invitation).
o	Greeting Cards: Send heartfelt messages with our handcrafted greeting cards for birthdays, holidays, and other occasions ($5-$15 per card).
•	Toys & Games: Find handcrafted toys and games that are both fun and educational.
o	Wooden Toys: Discover handcrafted wooden toys, such as building blocks ($20-$60 per set), puzzles ($15-$40), and toy cars ($10-$30). These toys are made from sustainable wood and finished with non-toxic paints.
o	Plush Creations: Find adorable handcrafted plush toys, including stuffed animals ($20-$50) and dolls ($30-$80). These toys are made from soft, high-quality materials.
•	Personalized Gifts: Find unique and thoughtful gifts for any occasion.
o	Personalized jewelry (price varies greatly, $30+), engraved items ($25+), custom portraits ($50+), and monogrammed gifts ($20+). Artisans can create custom pieces based on your specific requests.
•	Art & Collectibles: Discover original artworks and unique collectibles.
o	Original Paintings: Find original paintings in various styles and mediums, including oil paintings ($100-$1000+), watercolor paintings ($60-$300+), and acrylic paintings ($80-$500+).
o	Limited-edition Sculptures: Discover handcrafted sculptures made from various materials, such as metal ($150+), wood ($100+), and clay ($80+).
Platform Features
At Forma Creations, we prioritize personalization, ethics, and quality. Customers can easily request custom orders by contacting artisans directly. We promote the use of eco-friendly materials, encouraging sellers to adopt sustainable and recycled crafting methods. Our platform supports fair trade practices, ensuring that artisans are paid fairly and work under ethical conditions. Additional features include direct messaging with sellers for queries or customization, real-time order tracking, and a secure, encrypted checkout system for financial safety. All sellers go through a verification process to ensure the authenticity and quality of their offerings.
What We Can Do For You
As your chatbot assistant, I’m here to help with everything you need. I can recommend products based on your taste, budget, or occasion. I’ll guide you through the ordering process, assist in case of any issues, and provide updates on your delivery. I also help store your details—including name, mobile number, email, budget range, and product preferences—to personalize your shopping experience and keep you informed about future updates or offers. In case of problems like delayed shipping, damaged products, or returns, I can guide you to the right pages and assist you in resolving the issue.
I can also help you explore our values around sustainability, by sharing information about eco-conscious crafting and ethical sourcing. For quick access, I can direct you to relevant pages like the Returns Page, Seller Registration, or Product Listings.
Contact Support
If you ever need to speak with a human, our dedicated support team is here to help. You can reach us via email at connectsparkcraft@gmail.com or call us at 9876543210. Our support hours are Monday to Saturday, 9 AM to 7 PM. Whether it’s a general question or help with an order, we’re just a message or call away.
Our Goal
Our main goal is to offer you a smooth, engaging shopping experience while collecting key details to serve you better. These include your name, mobile number, email address, budget range, and product preferences. Your information is stored securely and helps us tailor recommendations and communicate important updates relevant to your interests.
Exit Chat
When you're ready to wrap up, just type “end” or “exit”. I’ll save your details and close the conversation. You’re always welcome back anytime for more handmade inspiration!


"""

# SQLite setup
DB_FILE = 'forma_creations.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS leads 
                 (id INTEGER PRIMARY KEY, name TEXT, mobile TEXT UNIQUE, email TEXT UNIQUE, 
                  budget TEXT, preference TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (id INTEGER PRIMARY KEY, lead_id INTEGER, product TEXT, price REAL, 
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
                  FOREIGN KEY (lead_id) REFERENCES leads(id))''')
    conn.commit()
    conn.close()

if not os.path.exists(DB_FILE):
    init_db()

def validate_mobile(mobile):
    return bool(re.match(r"^\d{10}$", mobile))

def validate_email(email):
    return bool(re.match(r'^[\w\.-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email))

def store_lead(name, mobile, email, budget="N/A", preference="N/A"):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO leads (name, mobile, email, budget, preference) VALUES (?, ?, ?, ?, ?)",
                  (name or "N/A", mobile or "N/A", email or "N/A", budget, preference))
        lead_id = c.lastrowid
        conn.commit()
        conn.close()
        return lead_id
    except sqlite3.IntegrityError:
        return None
    except Exception as e:
        print(f"Error storing lead: {e}")
        return None

def store_order(lead_id, product, price):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO orders (lead_id, product, price) VALUES (?, ?, ?)", 
                  (lead_id, product, price))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error storing order: {e}")
        return False

@app.route('/')
def index():
    session['data'] = {'name': None, 'mobile': None, 'email': None, 'budget': None, 'preference': None}
    session['history'] = []
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message').strip().lower()
    history = session.get('history', [])
    data = session.get('data', {})
    response_data = {'response': ''}

    history.append({"role": "user", "content": user_message})
    if not any(h["role"] == "system" for h in history):
        history.insert(0, {
    "role": "system",
    "content": KNOWLEDGE_BASE + "\nPrompt: You are a lead generation chatbot for Forma Creations, a marketplace for handmade goods. Only recommend and answer based on products and info in the knowledge base. If asked about anything outside it, politely deny. Converse naturally, keep responses under 100 words. Help the user find suitable products from the knowledge base. Collect and confirm lead details (name, mobile, email, budget, preferences) when relevant. Validate details clearly. Save leads immediately in SQLite."
})


    
    if not data['name'] and user_message != "start":  
        name_match = re.search(r"(?:my name is)?\s*(\w+)", user_message)
        if name_match and name_match.group(1) not in ["start", "end", "exit"]:
            data['name'] = name_match.group(1)
    if not data['mobile']:
        mobile_match = re.search(r"\b\d{10}\b", user_message)
        if mobile_match and validate_mobile(mobile_match.group(0)):
            data['mobile'] = mobile_match.group(0)
    if not data['email']:
        email_match = re.search(r"[\w\.-]+@[\w\.-]+", user_message)
        if email_match and validate_email(email_match.group(0)):
            data['email'] = email_match.group(0)
    if not data['budget']:
        budget_match = re.search(r"budget.*(\d+)", user_message)
        if budget_match:
            data['budget'] = budget_match.group(1)
    if not data['preference']:
        pref_match = re.search(r"(jewelry|decor|apparel|gift)", user_message)
        if pref_match:
            data['preference'] = pref_match.group(0)

    session['data'] = data

    try:
        if user_message == "start":
            response = "Hi there! Welcome to Forma Creations. I’m here to help you find unique handmade items. Can I have your name?"
        elif user_message in ["end", "exit"]:
            lead_id = store_lead(data['name'], data['mobile'], data['email'], data['budget'], data['preference'])
            response = f"Thanks, {data['name'] or 'friend'}! Your details are saved. Come back anytime!"
            session['data'] = {'name': None, 'mobile': None, 'email': None, 'budget': None, 'preference': None}
            session['history'] = []
        elif "buy" in user_message or "purchase" in user_message:
            product = re.search(r"(necklace|pottery|sweater|portrait)", user_message).group(0) if re.search(r"(necklace|pottery|sweater|portrait)", user_message) else "Custom Item"
            price = re.search(r"\d+", user_message).group(0) if re.search(r"\d+", user_message) else "50"
            if not data['name']:
                response = f"A {product} sounds wonderful! Who am I helping with this order?"
            elif not data['mobile']:
                response = f"Hi {data['name']}, I’ll need your 10-digit mobile to confirm your {product} order. What is it?"
            elif not data['email']:
                response = f"Great pick, {data['name']}! What’s your email so I can send order details for your {product}?"
            else:
                lead_id = store_lead(data['name'], data['mobile'], data['email'], data['budget'], data['preference'])
                if lead_id and store_order(lead_id, product, price):
                    response = f"Order placed: {product} for Rs. {price}, {data['name']}! Check your email soon."
                    response_data['order'] = {'product': product, 'price': price}
                    session['data'] = {'name': None, 'mobile': None, 'email': None, 'budget': None, 'preference': None}
                else:
                    response = "Oops, something went wrong with your order. Try again or contact support!"
        else:

            ai_response = client.chat.completions.create(
                model="google/gemini-2.0-flash-thinking-exp:free",
                messages=history,
                max_tokens=200,
                temperature=0.3
            ).choices[0].message.content


            if "looking for" in user_message or "interested in" in user_message:
                if not data['preference']:
                    ai_response += " What type of items catch your eye—like jewelry or decor?"
                if not data['budget']:
                    ai_response += " Oh, and what’s your budget range?"
            elif "recommend" in user_message or "suggest" in user_message:
                if not data['name']:
                    ai_response += " I’d love to help—may I have your name?"
            elif data['name'] and not data['mobile'] and "order" not in user_message:
                ai_response += f" By the way, {data['name']}, what’s your mobile number for future updates?"

            response = ai_response

    except Exception as e:
        response = "Oops, something went wrong! Email connectsparkcraft@gmail.com for help."
        print(f"Error: {e}")

    history.append({"role": "assistant", "content": response})
    session['history'] = history
    response_data['response'] = response
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
