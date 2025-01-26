from flask import Blueprint, render_template, request, flash, jsonify 
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
import os
from groq import Groq

views = Blueprint('views', __name__)

# Initialize Groq client (for chatbot)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')  # Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  # Providing the schema for the note 
            db.session.add(new_note)  # Adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data)  # This function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


# New route for the chatbot page
@views.route('/chatbot', methods=['GET', 'POST'])
@login_required
def chatbot():
    if request.method == 'POST':
        user_message = request.form.get('message')  # Get the user's message from the form

        if not user_message:
            flash('Please enter a message', category='error')
        else:
            try:
                # Call the Groq API to get the chatbot's response
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": user_message}],
                    model="llama-3.3-70b-versatile",  # Specify your model
                )

                # Extract the chatbot's response
                chatbot_reply = chat_completion.choices[0].message.content
                return render_template('chatbot.html', user=current_user, reply=chatbot_reply, message=user_message)

            except Exception as e:
                flash(f'Error: {str(e)}', category='error')

    return render_template('chatbot.html', user=current_user)
