from flask import Blueprint, render_template, session, redirect, request, send_file
from flask import flash
import os
import MySQLdb

from utils.speech_to_text import transcribe_audio
from utils.summarizer import get_summary
from utils.keyword_extractor import extract_keywords
from utils.topic_extractor import detect_topic
from utils.pdf_exporter import export_note_to_pdf

main = Blueprint('main', __name__)

UPLOAD_FOLDER = "static/uploads"
EXPORT_FOLDER = "static/exports"

def get_db():
    return MySQLdb.connect(
        host="localhost",
        user="root",
        passwd="zaid@12345",
        db="autonotes_pro"
    )

@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT id, title, topic, summary_text, created_at
        FROM notes
        WHERE user_id=%s
        ORDER BY id DESC
        """,
        (session['user_id'],)
    )
    notes = cursor.fetchall()

    cursor.execute(
        "SELECT COUNT(*) FROM notes WHERE user_id=%s",
        (session['user_id'],)
    )
    total_notes = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT topic, COUNT(*) as topic_count
        FROM notes
        WHERE user_id=%s
        GROUP BY topic
        ORDER BY topic_count DESC
        LIMIT 1
        """,
        (session['user_id'],)
    )
    top_topic_row = cursor.fetchone()
    top_topic = top_topic_row[0] if top_topic_row else "N/A"

    cursor.execute(
        """
        SELECT COUNT(DISTINCT topic)
        FROM notes
        WHERE user_id=%s
        """,
        (session['user_id'],)
    )
    total_topics = cursor.fetchone()[0]

    cursor.close()
    db.close()

    return render_template(
        'dashboard.html',
        notes=notes,
        total_notes=total_notes,
        top_topic=top_topic,
        total_topics=total_topics
    )


@main.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        if 'audio' not in request.files:
            return "No file selected"

        file = request.files['audio']

        if file.filename == "":
            return "No file selected"

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        transcript = transcribe_audio(file_path)
        summary = get_summary(transcript)
        keywords = extract_keywords(transcript)
        topic = detect_topic(transcript)

        keywords_text = ", ".join(keywords)

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO notes
            (user_id, title, original_text, summary_text, keywords, topic, audio_file)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                session['user_id'],
                file.filename,
                transcript,
                summary,
                keywords_text,
                topic,
                file.filename
            )
        )

        db.commit()
        note_id = cursor.lastrowid

        cursor.close()
        db.close()

        return render_template(
            "result.html",
            note_id=note_id,
            filename=file.filename,
            transcript=transcript,
            summary=summary,
            keywords=keywords,
            topic=topic
        )

    return render_template("upload.html")


@main.route('/history')
def history():
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT id, title, topic, keywords, summary_text, created_at
        FROM notes
        WHERE user_id=%s
        ORDER BY id DESC
        """,
        (session['user_id'],)
    )
    notes = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('history.html', notes=notes)


@main.route('/search')
def search_notes():
    if 'user_id' not in session:
        return redirect('/login')

    query = request.args.get('q', '').strip()

    db = get_db()
    cursor = db.cursor()

    if query:
        search_term = f"%{query}%"
        cursor.execute(
            """
            SELECT id, title, topic, keywords, summary_text, created_at
            FROM notes
            WHERE user_id=%s
            AND (
                title LIKE %s OR
                topic LIKE %s OR
                keywords LIKE %s OR
                summary_text LIKE %s OR
                original_text LIKE %s
            )
            ORDER BY id DESC
            """,
            (
                session['user_id'],
                search_term,
                search_term,
                search_term,
                search_term,
                search_term
            )
        )
    else:
        cursor.execute(
            """
            SELECT id, title, topic, keywords, summary_text, created_at
            FROM notes
            WHERE user_id=%s
            ORDER BY id DESC
            """,
            (session['user_id'],)
        )

    notes = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('search.html', notes=notes, query=query)


@main.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT id, full_name, email, created_at
        FROM users
        WHERE id=%s
        """,
        (session['user_id'],)
    )
    user = cursor.fetchone()

    cursor.execute(
        "SELECT COUNT(*) FROM notes WHERE user_id=%s",
        (session['user_id'],)
    )
    total_notes = cursor.fetchone()[0]

    cursor.close()
    db.close()

    return render_template('profile.html', user=user, total_notes=total_notes)


@main.route('/note/<int:note_id>')
def view_note(note_id):
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT id, title, topic, keywords, original_text, summary_text, created_at
        FROM notes
        WHERE id=%s AND user_id=%s
        """,
        (note_id, session['user_id'])
    )

    note = cursor.fetchone()

    cursor.close()
    db.close()

    if not note:
        return "Note not found"

    return render_template('note_detail.html', note=note)


@main.route('/delete-note/<int:note_id>')
def delete_note(note_id):
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM notes WHERE id=%s AND user_id=%s",
        (note_id, session['user_id'])
    )
    db.commit()

    cursor.close()
    db.close()

    return redirect('/history')


@main.route('/export-pdf/<int:note_id>')
def export_pdf(note_id):
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT title, topic, keywords, summary_text, original_text
        FROM notes
        WHERE id=%s AND user_id=%s
        """,
        (note_id, session['user_id'])
    )

    note = cursor.fetchone()

    cursor.close()
    db.close()

    if not note:
        return "Note not found"

    title, topic, keywords, summary, transcript = note

    os.makedirs(EXPORT_FOLDER, exist_ok=True)

    safe_title = title.replace(" ", "_").replace("/", "_").replace("\\", "_")
    pdf_path = os.path.join(EXPORT_FOLDER, f"{safe_title}.pdf")

    export_note_to_pdf(pdf_path, title, topic, keywords, summary, transcript)

    return send_file(pdf_path, as_attachment=True)

@main.route('/edit-note/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):

    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':

        summary = request.form['summary']
        topic = request.form['topic']
        keywords = request.form['keywords']

        cursor.execute(
            """
            UPDATE notes
            SET summary_text=%s,
                topic=%s,
                keywords=%s
            WHERE id=%s AND user_id=%s
            """,
            (
                summary,
                topic,
                keywords,
                note_id,
                session['user_id']
            )
        )

        db.commit()

        flash("Note updated successfully", "success")

        return redirect('/history')

    cursor.execute(
        """
        SELECT id, title, topic, keywords, summary_text
        FROM notes
        WHERE id=%s AND user_id=%s
        """,
        (note_id, session['user_id'])
    )

    note = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template(
        'edit_note.html',
        note=note
    )