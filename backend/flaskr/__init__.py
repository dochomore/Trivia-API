import json
import os
from pickle import GET
from tkinter import N
from wsgiref.util import request_uri
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from .models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
database = None


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    db = setup_db(app)

    cors = CORS(app=app, resources={r"/*": {'origins': '*'}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    def categories():
        categories = Category.query.all()
        data = {}
        for category in categories:
            data[f'{category.id}'] = category.type
        return data

    @app.route('/categories', methods=['GET'])
    def get_catagories():
        data = categories()
        return jsonify({'categories': data})

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        try:
            data = {}
            questions = Question.query.all()[start:end]
            if (questions is None):
                raise Exception()
            qts = []
            for question in questions:
                q = {'id': question.id, 'question': question.question, 'answer': question.answer,
                     'difficulty': question.difficulty, 'category': question.category}
                qts.append(q)
            data['questions'] = qts
            data['categories'] = categories()
            data['totalQuestions'] = len(questions)

        except:
            pass
        finally:
            return jsonify(data)

    @app.route('/questions/<int:question_id>', methods=['POST', 'DELETE'])
    def delete_question(question_id):
        data = None
        try:
            question = Question.query.get(question_id)
            db.session.delete(question)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify({'success': data})

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        question = request.args.get('question', '', type=str)
        answer = request.args.get('answer', '', type=str)
        difficulty = request.args.get('difficulty', 0, type=int)
        category = request.args.get('category', 0, type=int)

        try:
            q = Question(question=question, answer=answer,
                         difficulty=difficulty, category=category)
            db.session.add(q)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify({'success': True})

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app
