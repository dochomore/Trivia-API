from array import array
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
             
            for index, question in enumerate(questions):
                q = {'id': question.id, 'question': question.question, 'answer': question.answer,
                     'difficulty': question.difficulty, 'category': question.category}
                qts.append(q)
                if index == 0:
                    data['currentCategory'] = categories()['1']
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
        question = request.json['question']
        answer = request.json['answer']
        difficulty = request.json['difficulty']
        category = request.json['category']
        
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
        search_term = request.json['searchTerm']
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

                if index == 0:
                    data['currentCategory'] = categories()['1']

            data['questions'] = qts
            data['totalQuestions'] = len(questions)

        except:
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify(data)

    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def question_categories(id):
        data = {}
        qts = []
        try:
            questions = Question.query.filter(
                Question.category == id).all()
            for index, q in enumerate(questions):
                obje = {}
                obje['id'] = q.id
                obje['question'] = q.question
                obje['answer'] = q.answer
                obje['category'] = q.category
                qts.append(obje)

                if index == 0:
                    data['currentCategory'] = categories()['1']

            data['questions'] = qts
            data['totalQuestions'] = len(questions)

        except:
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify(data)

    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        prev_questions = request.json['previous_questions']
        category = request.json['quiz_category']
        data = {}

        try:

            questions = Question.query.filter(
                Question.category == category).filter(Question.id.not_in(prev_questions)).all()
            if questions is not None:
                question = {}
                response = questions[1]
                question['id'] = response.id
                question['question'] = response.question
                question['answer'] = response.answer
                question['difficulty'] = response.difficulty
                question['category'] = response.category
                
                data['question'] = question
        except:
            pass

        return jsonify(data)

    @app.errorhandler(404)
    def not_found(erorr):
        return jsonify({'Success': False, 'error': 404, "message": "not found"}), 404

    @app.errorhandler(422)
    def unprocessable(erorr):
        return jsonify({'Success': False, 'error': 422, "message": "unprocesable"}), 422

    return app
