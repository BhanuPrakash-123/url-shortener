from flask import Flask, request, jsonify, redirect, render_template
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError
import hashlib
import validators
import re
from datetime import datetime

app = Flask(__name__)

# MongoDB configuration
mongo_uri = 'mongodb+srv://user:user@cluster0.dtsnf.mongodb.net/'
client = MongoClient(mongo_uri)
db = client['url_shortener']
urls_collection = db['urls']

# Ensure's unique index on short_code
urls_collection.create_index('short_code', unique=True)

def generate_short_code(url, salt=0):
    # Generate a short code using MD5 hash and salt for collision resolution
    salted_url = f"{url}{salt}" if salt else url
    hash_digest = hashlib.md5(salted_url.encode()).hexdigest()
    return hash_digest[:8]  # Use first 8 characters of the MD5 hash

def create_url_entry(short_code, long_url):
    #Create a new URL entry in the database
    return urls_collection.insert_one({
        'short_code': short_code,
        'long_url': long_url,
        'hits': 0,
        'created_at': datetime.utcnow(),
        'expires_at': None  # Expiration can be added here
    })

@app.route('/')
def index():
    # Serve the frontend
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten_url():
    # Endpoint to shorten a URL with optional custom alias
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing URL'}), 400

    long_url = data['url']
    alias = request.args.get('alias')

    # Validate URL format
    if not validators.url(long_url):
        return jsonify({'error': 'Invalid URL'}), 400

    # Handle custom alias
    if alias:
        if not re.match(r'^[\w-]+$', alias):
            return jsonify({'error': 'Alias can only contain letters, numbers, underscores, and hyphens.'}), 400
        # Check for existing alias
        existing = urls_collection.find_one({'short_code': alias})
        if existing:
            return jsonify({'error': 'Alias already exists'}), 409
        try:
            create_url_entry(alias, long_url)
            return jsonify({'short_code': alias}), 201
        except DuplicateKeyError:
            return jsonify({'error': 'Alias already exists'}), 409

    # Check if URL already exists
    existing = urls_collection.find_one({'long_url': long_url})
    if existing:
        return jsonify({'short_code': existing['short_code']}), 200

    # Generate and handle short code collisions
    attempts = 0
    while attempts < 10:
        short_code = generate_short_code(long_url, attempts)
        try:
            create_url_entry(short_code, long_url)
            return jsonify({'short_code': short_code}), 201
        except DuplicateKeyError:
            # Check if the existing entry is for the same URL
            existing = urls_collection.find_one({'short_code': short_code})
            if existing and existing['long_url'] == long_url:
                return jsonify({'short_code': short_code}), 200
            attempts += 1

    return jsonify({'error': 'Failed to generate a unique short code'}), 500

@app.route('/<short_code>')
def redirect_to_original(short_code):
    # Redirect to original URL and increment hit counter
    # Find and atomically increment the hit count
    document = urls_collection.find_one_and_update(
        {'short_code': short_code},
        {'$inc': {'hits': 1}},
        return_document=ReturnDocument.AFTER
    )
    if not document:
        return jsonify({'error': 'Short code not found'}), 404

    return redirect(document['long_url'], code=302)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))  # Use PORT environment variable or default to 5000
    app.run(host='0.0.0.0', port=port)
