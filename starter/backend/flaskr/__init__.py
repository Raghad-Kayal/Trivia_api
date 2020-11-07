import os
import pprint
from flask import Flask, request, abort, jsonify, current_app, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy import func
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_question(request, allQuestions):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [i.format() for i in allQuestions]
    print(questions)
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    # CORS(APP)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):

        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def request_categories():
        allCategories = Category.query.all()
        theCategory = {}

        for i in allCategories:
            theCategory[i.id] = i.type

        if len(theCategory) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'Categories': theCategory
        })

    @app.route('/questions', methods=['GET'])
    def request_questions():
        allQuestions = Question.query.all()
        allCategories = Category.query.all()
        theQuestion = paginate_question(request, allQuestions)
        theCategory = {}

        if len(theQuestion) == 0:
            abort(404)

        for i in allCategories:
            theCategory[i.id] = i.type

        return jsonify({
            'success': True,
            'questions': theQuestion,
            'total_questions': len(allQuestions),
            'categories': theCategory
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):

        try:

            deletedQuestions = Question.query.filter(
                Question.id == question_id).one_or_none()

            if deletedQuestions is None:
                abort(404)

            deletedQuestions.delete()

            allQuestions = Question.query.all()
            theQuestion = paginate_question(request, allQuestions)

            allCategories = Category.query.all()
            theCategory = [i.format() for i in allCategories]

            return jsonify({
                'success': True,
                'Questions': theQuestion,
                'The deleted question id is': question_id,
                'Number of questions': len(allQuestions),
                'Categories': theCategory
            })

        except:
            abort(422)

    @app.route('/newquestions', methods=['POST'])
    def new_question():
        body = request.get_json()
        try:
            newQuestion = Question(question=body['question'], answer=body['answer'],
                                   category=body['category'], difficulty=body['difficulty'])
            newQuestion.insert()

            return jsonify({
                'success': True,
                'question': newQuestion.question,
                'answer': newQuestion.answer,
                'category': newQuestion.category,
                'difficulty': newQuestion.difficulty
            })

        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def search_question():
        x = request.get_json()
        searchTerm = x['searchTerm']

        try:
            searchQuestion = Question.query.filter(
                Question.question.ilike(f'%{searchTerm}%')).all()

            data = []
            for a in searchQuestion:

                data.append({
                    'id': a.id,
                    'question': a.question,
                    'answer': a.answer,
                    'category': a.category,
                    'difficulty': a.difficulty
                })

            return jsonify({
                'success': True,
                'questions': data,
                'total_questions': len(searchQuestion)
            })

        except:
            abort(422)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def question_by_category(category_id):

        allQuestions = Question.query.filter(
            Question.category == category_id).all()
        theQuestion = paginate_question(request, allQuestions)

        if len(theQuestion) == 0:
            abort(404)

        return jsonify({
            'questions': theQuestion,
            'totalQuestions': len(allQuestions)
        })

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()

        previous_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')
        id = quiz_category['id']
        category_id = int(id)

        if not body:
            abort(400)

        if category_id == 0:
            question = Question.query.all()
            if len(previous_questions) == len(question):
                question = None
                return jsonify({
                    'success': True,
                    'question': question
                })

            else:
                question = Question.query.order_by(func.random()).first()
                return jsonify({
                    'success': True,
                    'question': question.format()
                })

        else:
            question = Question.query.filter(
                Question.category == category_id).all()

            if len(previous_questions) == len(question):
                question = None
                return jsonify({
                    'success': True,
                    'question': question
                })

            else:
                question = Question.query.filter(
                    Question.category == category_id).order_by(
                        func.random()).filter(Question.id.notin_(
                            previous_questions)).first()

            return jsonify({
                'success': True,
                'question': question.format()
            })

        """ if question:
            if len(previous_questions) == len(question):
                question = None
                return jsonify({
                    'success': True,
                    'question': question
                })

            else:
                # while Question.category == 0:
                while category_id == 0:
                    question = Question.query.order_by(func.random()).first()

                question = Question.query.filter(
                    Question.category == category_id).order_by(
                        func.random()).filter(Question.id.notin_(
                            previous_questions)).first()

                return jsonify({
                    'success': True,
                    'question': question.format()
                })
        else:
            abort(404) """

        """  previous_questions = request.json['previous_questions']
        quiz_category = request.json['quiz_category']
        if quiz_category['id'] == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter(
                Question.category == quiz_category['id']).all()

        if questions:
            if len(previous_questions) == len(questions):
                question = None
                return jsonify({
                    'success': True,
                    'question': question
                })
            else:
                question = random.choice(questions)
                while question.id in previous_questions:
                  question = random.choice(questions)
                return jsonify({
                    'success': True,
                    'question': question.format()
                })
        else:
         abort(404) """

    @app.errorhandler(404)
    def not_found(error):

        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(405)
    def not_allowed(error):

        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not Allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
        }), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "Bad Request"
        }), 400

    return app
