from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  to make it more secure '/api/' was added into the frontend paths
  '''
  CORS(app, resources={r"/api/*": {"origins": "*"}})


  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS')
    return response

  '''
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/api/categories', methods=['GET'])
  def get_categories():
    try:
      categories = Category.query.all()
      categories_list = [category.format() for category in categories]

      return jsonify({
        "success": True,
        "categories": categories_list
      })
    except:
      abort(500)  # Internal Server Error if the server could not be more specific on what the exact problem is

  '''
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/api/questions', methods=['GET'])
  def get_questions():
    selection = Question.query.all()
    current_questions = paginate_questions(request, selection)

    if len(current_questions) == 0:
      abort(404)

    categories = Category.query.all()
    categories_list = [category.format() for category in categories]

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(selection),
      'categories': categories_list,
      'current_category': None
    })

  ''' 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/api/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.get(question_id)
    if question is None:
      abort(404)
    else:
      try:
        question.delete()
        return jsonify({
          "success": True,
          "deleted": question_id
        })
      except:
        abort(422)

  ''' 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  '''
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/api/questions', methods=['POST'])
  def add_question():
    content = request.get_json()
    if 'searchTerm' in content:
      # if request contains searchTerm than get any questions
      # for whom the search term is a substring of the question
      search_term = content['searchTerm']
      questions = Question.query.filter(
        Question.question.ilike(f'%{search_term}%')).all()

      questions_list = [question.format() for question in questions]

      totalQuestions = len(Question.query.all())

      return jsonify({
        "success": True,
        "questions": questions_list,
        "totalQuestions": totalQuestions,
        "currentCategory": None
      })

    else:
      # else add a new question

      # Check for errors with the submission
      if (content['question'].strip() == "") or (content['answer'].strip() == ""):
        # if parameters of the question aren't specified, we don't create new question
        abort(400, "empty question or answer")

      try:
        new_question = Question(content['question'], content['answer'], \
                                content['category'], content['difficulty'])
        new_question.insert()
      except:
        abort(422)

      return jsonify({
        "success": True,
        "added": new_question.id
      })

  '''
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/api/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    questions = Question.query.filter_by(category=str(category_id)).all()
    current_questions = paginate_questions(request, questions)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
        "success": True,
        "questions": current_questions,
        "totalQuestions": len(current_questions),
        "currentCategory": category_id
      })

  '''
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/api/quizzes', methods=['POST'])
  def add_quiz():
    content = request.get_json()

    if 'previous_questions' in content:
      previousQuestions = content['previous_questions']
    else:
      previousQuestions = []

    try:
      quiz_category = content['quiz_category']['id']
    except:
      # Category must be supplied in this format
      abort(400)


    if quiz_category == 0:
      questions = Question.query \
        .filter(Question.id.notin_(previousQuestions)) \
        .all()
    else:
      questions = Question.query\
        .filter(Question.category==str(quiz_category), Question.id.notin_(previousQuestions))\
        .all()
    if len(questions)==0:
      return jsonify({
        "success": True
      })

    question = random.choice([question.format() for question in questions])
    return jsonify({
      "success": True,
      "question": question
    })

  '''
  Create error handlers for all expected errors 
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
  def bed_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bed request"
    }), 400

  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "method not allowed"
    }), 405

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "Internal Server Error"
    }), 500

  return app

    