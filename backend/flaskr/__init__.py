# Import all required Libaries
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

#Import models for setup, questions and category
from models import setup_db, Question, Category

#set queston per page to 10
QUESTIONS_PER_PAGE = 10

def paginate_questions(request, all_questions):
    '''
    Paginate questions
    '''
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    disp_questions = [questions.format() for questions in all_questions]
    current_questions = disp_questions[start:end]

    return current_questions


def create_app(test_config=None):
    '''
    create and configure the app
    '''
    app = Flask(__name__)
    setup_db(app)

    # set up CORS, allowing all origins
    CORS(app, resources={'/': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        '''
        Use the after_request decorator to set Access-Control-Allow
        '''
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories')
    def get_categories():
        '''
        Create an endpoint to handle GET requests
        for all available categories.
        '''
        # get all categories in a dict
        all_categories = Category.query.all()
        categories = {}

        for category in all_categories:
            categories[category.id] = category.type
        
        # abort if there is no category
        if len(categories) == 0:
            abort(404)

        # return the category data
        return jsonify({
            'success': True,
            'categories': categories
        })

    
    @app.route('/questions')
    def get_questions():
        '''
        Create an endpoint to handle GET requests for questions,
        including pagination (every 10 questions).
        This endpoint should return a list of questions,
        number of total questions, current category, categories.
        '''
        
        # get all questions
        all_questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, all_questions)

        # abort if no questions found
        if len(all_questions) == 0:
            abort(404)
        
        # get all categories in a dict
        all_categories = Category.query.all()
        categories = {}

        for category in all_categories:
            categories[category.id] = category.type

        # return all questions and category dict
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total questions': len(all_questions),
            'categories': categories
        })

    
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        '''
        Create an endpoint to DELETE question using a question ID.
        '''

        try:
            # fetch question by quuestio id
            question = Question.query.filter_by(id=id).one_or_none()
            
            # abort if no question found
            if question is None:
                abort(404)

            # delete the question, when fetched
            question.delete()
            
            # return true when deleted successfully
            return jsonify({
                'success': True,
                'deleted': id
            })
        
        # raise exception for any error during deleting the question
        except:
            abort(422)

    
    @app.route('/questions', methods=['POST'])
    def create_question():
        '''
        Create an endpoint to POST a new question,
        which will require the question and answer text,
        category, and difficulty score.
        '''

        # Get the request body
        body = request.get_json()
        
        # check if search term exists
        if body.get('searchTerm'):
            search = body.get('searchTerm')
            all_questions = Question.query.filter(
                Question.question.ilike(f'%{search}%')).all()
            
            if (len(all_questions) == 0):
                abort(404)

            current_questions = paginate_questions(request, all_questions)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(all_questions)
            })
        
        # Create new question
        else:
            # assign question variables data from bodt
            new_question = body.get('question')
            new_answer = body.get('answer')
            new_difficulty = body.get('difficulty')
            new_category = body.get('category')

            if ((new_question is None) or (new_answer is None)
                    or (new_difficulty is None) or (new_category is None)):
                abort(422)

            try:
                # create the new question
                question = Question(question=new_question, answer=new_answer,
                                    difficulty=new_difficulty, category=new_category)
                question.insert()

                # fetch all questions and paginate
                all_questions = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, all_questions)

                # return the new created question if successfully created
                return jsonify({
                    'success': True,
                    'created': question.id,
                    'question_created': question.question,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })
            except:
                abort(422)

    
    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
        '''
        Create a GET endpoint to get questions based on category.
        '''
        # fetch the category based on id
        category = Category.query.filter_by(id=id).one_or_none()
        
        # abort if no match dound
        if (category is None):
            abort(404)

        # fetch all questions for that category    
        all_questions = Question.query.filter_by(category=category.id).all()
        current_questions = paginate_questions(request, all_questions)

        # return the data if fetch successfully
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(all_questions),
            'category': category.type
        })

    
    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        '''
        Create a POST endpoint to get questions to play the quiz.
        This endpoint should take category and previous question parameters
        and return a random questions within the given category,
        if provided, and that is not one of the previous questions.
        '''
        
        # get the request body, required category and previous question
        body = request.get_json()
        category = body.get('quiz_category')
        prev_question = body.get('previous_questions')

        if ((category is None) or (prev_question is None)):
            abort(400)

        # get random question
        def get_rand_question():
            return questions[random.randrange(0, len(questions), 1)]

        # check if thq question was asked previously
        def check_from_prev_question(question):
            played = False
            for i in prev_question:
                if (i == question.id):
                    played = True

            return played

        # fetch all question if category = All
        if category['id'] == 0:
            questions = Question.query.all()

        # fetch question for specific category
        else:
            questions = Question.query.filter_by(
                category=category['id']).all()

        # get random quesion
        question = get_rand_question()

        # check if the question was asked before
        while (check_from_prev_question(question)):
            question = get_rand_question()

            if (len(prev_question) == len(questions)):
                return jsonify({
                    'success': True
                })

        # return the quiz question
        return jsonify({
            'success': True,
            'question': question.format()
        })
        
    
    '''
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app
