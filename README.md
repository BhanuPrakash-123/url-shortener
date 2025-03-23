# URL Shortener

A simple URL shortening service built with **Python**, **Flask**, and **MongoDB**. This project allows users to shorten long URLs and redirect to the original URL using a short code. It also supports tracking the number of times a short URL is accessed. The application has been deployed and is live at [https://url-shortener-913x.onrender.com/](https://url-shortener-913x.onrender.com/).

## Screenshot

![Screenshot](https://github.com/BhanuPrakash-123/url-shortener/blob/master/web.png?raw=true)

---

## Table of Contents
1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Approach](#approach)
4. [Handling Collisions](#handling-collisions)
5. [Steps to Run Locally](#steps-to-run-locally)
6. [API Documentation](#api-documentation)

---

## Features
- Shorten long URLs.
- Redirect to the original URL using a short code.
- Track the number of times a short URL is accessed.
- Scalable and easy to deploy.

---

## Tech Stack
- **Backend**: Python, Flask
- **Database**: MongoDB
- **Deployment**: Render
- **Version Control**: Git, GitHub

---

## Approach
1. **URL Shortening**:
   - When a long URL is submitted, the system generates a unique short code using an MD5 hash.
   - The short code and long URL are stored in a MongoDB collection.
   - If the same long URL is submitted again, the system returns the existing short code.

2. **Redirection**:
   - When a user visits the short URL, the system looks up the short code in the database and redirects to the original URL.
   - The system also increments the hit count for the short URL.

3. **Statistics Tracking**:
   - The system tracks the number of times a short URL is accessed and stores it in the database.

---

## Handling Collisions
Collisions occur when two different long URLs generate the same short code. To handle this:
1. **MD5 Hashing**:
   - The system uses an MD5 hash of the long URL to generate the short code.
   - The first 8 characters of the hash are used as the short code.

2. **Salt for Collision Resolution**:
   - If a collision is detected (i.e., the short code already exists in the database for a different long URL), the system appends a **salt** (a random number) to the long URL and rehashes it.
   - This process is repeated until a unique short code is generated.

3. **Database Uniqueness**:
   - The `short_code` field in the MongoDB collection is indexed as unique, ensuring no two entries can have the same short code.

This approach ensures that collisions are resolved efficiently, and each long URL gets a unique short code.

---

## Steps to Run Locally

### Prerequisites
- Python 3.11 or higher
- MongoDB (local or remote)
- Git

### Installation
1. Clone the repository:
   ```bash
     git clone https://github.com/BhanuPrakash-123/url-shortener.git
     cd url-shortener
   ```
2. Create a virtual environment
   ```bash
    python -m venv venv
   ```
3. Create a virtual environment
    - On Windows:
       ```bash
         python -m venv venv
       ```
    - On macOS/Linux:
       ```bash
         source venv/bin/activate
       ```
4. Install dependencies:
   ```bash
     pip install -r requirements.txt
   ```
5. Set up MongoDB:
    - Start a local MongoDB instance or use a remote MongoDB instance (e.g., MongoDB Atlas).
    - Set the MONGO_URI environment variable:
       ```bash
         export MONGO_URI=mongodb://localhost:27017/  # For local MongoDB
6. Run the Flask app:
   ```bash
     python app.py

### API Documentation
## Base URL
   ```
     http://127.0.0.1:5000
   ```
## Endpoints
1. Shorten a URL
- URL: /shorten
- Method: POST
- Request Body:
  ```json
      {
        "url": "https://example.com"
      }
  ```
- Response:
  ```json
      {
        "short_code": "abc12345"
      }
  ```

2. Redirect to Original URL
- URL: /<short_code>
- Method: GET
- Response:
    - Redirects to the original URL.
3. Example Requests
- Shorten a URL:
    ```bash
        curl -X POST -H "Content-Type: application/json" -d '{"url":"https://example.com"}' http://127.0.0.1:5000/shorten
    ```
- Redirect to Original URL:
    ```bash
        curl -v http://127.0.0.1:5000/abc12345
    ```
