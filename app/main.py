import os
import random
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', 'postgres')
DB_NAME = os.environ.get('DB_NAME', 'quotes')

def get_conn():
    import psycopg2
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME
    )

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            author TEXT NOT NULL,
            upvotes INT DEFAULT 0,
            downvotes INT DEFAULT 0
        )
    ''')
    cur.execute("SELECT COUNT(*) FROM quotes")
    if cur.fetchone()[0] == 0:
        seed = [
            ("The only way to do great work is to love what you do.", "Steve Jobs"),
            ("Innovation distinguishes between a leader and a follower.", "Steve Jobs"),
            ("Talk is cheap. Show me the code.", "Linus Torvalds"),
            ("In open source, we feel strongly that to really do something well, you have to get a lot of people involved.", "Linus Torvalds"),
            ("Simplicity is the ultimate sophistication.", "Leonardo da Vinci")
        ]
        for text, author in seed:
            cur.execute("INSERT INTO quotes (text, author) VALUES (%s, %s)", (text, author))
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def index():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, text, author, upvotes, downvotes FROM quotes ORDER BY RANDOM() LIMIT 1")
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        quote = {'id': row[0], 'text': row[1], 'author': row[2], 'upvotes': row[3], 'downvotes': row[4]}
    else:
        quote = {'id': 0, 'text': 'No quotes found.', 'author': '', 'upvotes': 0, 'downvotes': 0}
    return render_template('index.html', quote=quote)

@app.route('/upvote/<int:quote_id>')
def upvote(quote_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE quotes SET upvotes = upvotes + 1 WHERE id = %s", (quote_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/')

@app.route('/downvote/<int:quote_id>')
def downvote(quote_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE quotes SET downvotes = downvotes + 1 WHERE id = %s", (quote_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)