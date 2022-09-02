from asyncio import constants
import json
from operator import index
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

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        search_term = request.args.get('searchTerm', '', type=str)
        term = "%{}%".format(search_term)
        data = {}
        qts = []
        try:
            questions = Question.query.filter(
                Question.question.ilike(term)).all()
            for index, q in enumerate(questions):
                obje = {}
                obje['id'] = q.id
                obje['question'] = q.question
                obje['answer'] = q.answer
                obje['category'] = q.category
                qts.append(obje)

            data['questions'] = qts
            data['totalQuestions'] = len(questions)

        except:
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify(data)

    @app.route('/questions/<categories>', methods=['GET'])
    def question_categories(categories):
        term = "%{}%".format(categories)
        data = {}
        qts = []
        try:
            questions = Question.query.filter(
                Question.category == categories).all()
            for index, q in enumerate(questions):
                obje = {}
                obje['id'] = q.id
                obje['question'] = q.question
                obje['answer'] = q.answer
                obje['category'] = q.category
                qts.append(obje)

            data['questions'] = qts
            data['totalQuestions'] = len(questions)

        except:
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify(data)

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
    # @app.route('/quizzes', methods=['POST'])
    # def quizzes():
    #     questions = request.args.get('questions', [], type=list)
    #     category = request.args.get('category', '', type=str)
    #     try:
    #         quesitons

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(erorr):
        return jsonify({'Success': False, 'error': 404, "message": "not found"}), 404

    return app
