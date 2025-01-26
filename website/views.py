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
            # Providing the schema for the note
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)  # Adding the note to the database
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("Homepage.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    # This function expects a JSON from the INDEX.js file
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@views.route('/chatbot', methods=['GET', 'POST'])
@login_required
def chatbot():
    if request.method == 'POST':
        # Get the user's message from the JSON body
        user_message = request.json.get('message')

        if not user_message:
            # Return an error as JSON
            return jsonify({"error": "Please enter a message"}), 400
        else:
            try:
                sustainability_level = current_user.sustainability_level
                user_message += "You are an expert on helping people create sustainable businesses that are safe for the earth. Please ensure that you generate only 10 tasks for me. These 10 tasks should be actionable, and quantifiable. This is the current level of the user: {sustainability_level}. These are the decriptions of the levels, not the current level of the user. Use energy-efficient lighting, Recycle more waste, Reduce water usage, Switch to eco-friendly transportation. Please format the tasks like this, but with a little more detail. Please do not add anything else expcept for the numbered list of tasks. Level 1: Businesses are in the early stages of sustainability, with minimal practices in place. Policies are either non-existent or poorly implemented, and there is little to no tracking or measurable outcomes. Level 2: Businesses have moderate sustainability efforts, with policies in place but inconsistently applied. There is some tracking and progress, though full implementation and monitoring are still lacking. Level 3: Businesses have fully integrated sustainability into their operations with clear policies, measurable goals, and significant positive impact. Practices are well-implemented, monitored, and regularly reported. Please ensure that the response is more readable."
                # Call the Groq API to get the chatbot's response
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": user_message}],
                    model="llama-3.3-70b-versatile",  # Specify your model
                )

                # Extract the chatbot's response
                chatbot_reply = chat_completion.choices[0].message.content
                # Return the reply as JSON
                return jsonify({"reply": chatbot_reply})

            except Exception as e:
                # Return error details as JSON
                return jsonify({"error": str(e)}), 500

    # For GET requests, render the chatbot.html template
    return render_template('chatbot.html', user=current_user)

@views.route('/todos')
def todos():
    # Render the todos.html template (you need to serve the template from your static folder)
    return render_template('todos.html')

