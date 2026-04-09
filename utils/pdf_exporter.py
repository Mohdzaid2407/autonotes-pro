from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

def export_note_to_pdf(file_path, title, topic, keywords, summary, transcript):
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    x = 50
    y = height - 50

    def write_line(text, font="Helvetica", size=11, gap=18):
        nonlocal y
        c.setFont(font, size)

        max_chars = 95
        lines = []

        while len(text) > max_chars:
            split_index = text.rfind(" ", 0, max_chars)
            if split_index == -1:
                split_index = max_chars
            lines.append(text[:split_index])
            text = text[split_index:].strip()

        lines.append(text)

        for line in lines:
            if y < 60:
                c.showPage()
                y = height - 50
                c.setFont(font, size)
            c.drawString(x, y, line)
            y -= gap

    c.setTitle(title)

    write_line("AutoNotes Pro - Note Export", "Helvetica-Bold", 15, 22)
    write_line(f"Title: {title}", "Helvetica-Bold", 12, 18)
    write_line(f"Topic: {topic}", "Helvetica", 11, 18)
    write_line(f"Keywords: {keywords}", "Helvetica", 11, 18)

    y -= 10
    write_line("Summary:", "Helvetica-Bold", 12, 20)
    write_line(summary, "Helvetica", 11, 18)

    y -= 10
    write_line("Transcript:", "Helvetica-Bold", 12, 20)
    write_line(transcript, "Helvetica", 11, 18)

    c.save()