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
API_KEY = "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"  # Replace with your actual API key
client = openai.OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# Knowledge base (unchanged)
KNOWLEDGE_BASE = """
🌟 Forma Creations: Your Handmade Haven
Forma Creations is an online marketplace that brings together a diverse collection of unique, handcrafted goods made by skilled artisans. Our platform offers customers a chance to discover meaningful, sustainable, and creative pieces while supporting independent makers. Whether you're shopping for yourself or a special gift, you'll find a wide variety of handmade items that tell a story and make a difference.

🛍️ Products
We offer a wide selection of handcrafted products across several categories. In Jewelry & Accessories, you'll find necklaces, earrings, bracelets, scarves, and hats. Our Home Decor range includes wall art, pottery, candles, and cushions to bring warmth and personality to any space. For fashion lovers, our Apparel & Textiles include hand-knit clothing and custom-made t-shirts. We also offer Stationery & Paper Goods, such as journals, invitations, and greeting cards, as well as Toys & Games, including wooden toys and plush creations. Shoppers looking for thoughtful gestures can explore Personalized Gifts for special occasions, and art enthusiasts will enjoy our Art & Collectibles, from original paintings to limited-edition sculptures.

You can explore our collections directly via these category links: Jewelry, Home Decor, Apparel, Stationery, Toys, Gifts, and Art.

🛠️ Platform Features
At Forma Creations, we prioritize personalization, ethics, and quality. Customers can easily request custom orders by contacting artisans directly. We promote the use of eco-friendly materials, encouraging sellers to adopt sustainable and recycled crafting methods. Our platform supports fair trade practices, ensuring that artisans are paid fairly and work under ethical conditions. Additional features include direct messaging with sellers for queries or customization, real-time order tracking, and a secure, encrypted checkout system for financial safety. All sellers go through a verification process to ensure the authenticity and quality of their offerings.

✅ What I Can Do
As your chatbot assistant, I’m here to help with everything you need. I can recommend products based on your taste, budget, or occasion. I’ll guide you through the ordering process, assist in case of any issues, and provide updates on your delivery. I also help store your details—including name, mobile number, email, budget range, and product preferences—to personalize your shopping experience and keep you informed about future updates or offers. In case of problems like delayed shipping, damaged products, or returns, I can guide you to the right pages and assist you in resolving the issue.

I can also help you explore our values around sustainability, by sharing information about eco-conscious crafting and ethical sourcing. For quick access, I can direct you to relevant pages like the Returns Page, Seller Registration, or Product Listings.

📞 Contact Support
If you ever need to speak with a human, our dedicated support team is here to help. You can reach us via email at connectsparkcraft@gmail.com or call us at 9876543210. Our support hours are Monday to Saturday, 9 AM to 7 PM. Whether it’s a general question or help with an order, we’re just a message or call away.

🎯 Goal
My main goal is to offer you a smooth, engaging shopping experience while collecting key details to serve you better. These include your name, mobile number, email address, budget range, and product preferences. Your information is stored securely and helps us tailor recommendations and communicate important updates relevant to your interests.

🧾 Exit Chat
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
        history.insert(0, {"role": "system", "content": KNOWLEDGE_BASE + "\nPrompt: You are a lead generation chatbot that sells only handmade goods, Converse naturally in few words, recommend products that are only in the knowledge base, collect lead info (name, mobile, email, budget, preference) at relevant moments and do check them whether the details are correct or not, store in SQLite, respond in <100 words, save immediately."})

    # Extract data naturally, ensuring "start" isn't stored as a name
    if not data['name'] and user_message != "start":  # Prevent "start" from being stored as name
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
            response = "Hi there! Welcome to Forma Creations. I’m here to help you find unique handmade items. What are you looking for today?"
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
            # Natural conversation with contextual info requests
            ai_response = client.chat.completions.create(
                model="google/gemma-3-1b-it:free",
                messages=history,
                max_tokens=150,
                temperature=0.7
            ).choices[0].message.content

            # Add info requests at natural points
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

            response = ai_response + " (Type 'end' to save and exit anytime.)"

    except Exception as e:
        response = "Oops, something went wrong! Email connectsparkcraft@gmail.com for help."
        print(f"Error: {e}")

    history.append({"role": "assistant", "content": response})
    session['history'] = history
    response_data['response'] = response
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)