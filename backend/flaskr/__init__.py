import os
from sre_constants import ANY
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.sql import func
from sqlalchemy import and_
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app)



    """
        DONE
    """
    @app.after_request
    def after_request(res):
        res.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        res.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return res

    """
        DONE
    """
    @app.route('/categories')
    def getallcategories():
        getall = Category.query.all()
        
        loopedcategory = {category.id: category.type for category in getall}
        return jsonify({
            'categories':loopedcategory
        })



    """
        DONE
    """
    @app.route('/questions', methods=['GET'])
    def getpaginatedquestions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        getquestions = Question.query.order_by(Question.id).all()
        loopedquestions = [singlequestion.format() for singlequestion in getquestions]
        
        activeQuestionPage = loopedquestions[start:end]

        if len(activeQuestionPage) == 0:
            abort(404)
        
        getallcategories = Category.query.all()
        
        loopedcategory = {category.id: category.type for category in getallcategories}
        return jsonify({
            'success': True,
            'questions':activeQuestionPage,
            'totalQuestions':len(loopedquestions),
            'categories':loopedcategory,
        })
    




    """
        DONE
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def deleteQuestion(question_id):
        try:
            thequestion = Question.query.filter(Question.id == question_id).one_or_none()

            if thequestion is None:
                abort(404)

            thequestion.delete()
            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                }
            )

        except:
            abort(422)

    
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    """
    @app.route("/questions", methods=["POST"])
    def addNewQuestion():
        body = request.get_json()

        NewQuestion = body.get("question", None)
        New_QuestionAns = body.get("answer", None)
        Question_difficulty = body.get("difficulty", None)
        Question_Cat = body.get("category", None)
        try:
            addthenewquestion = Question(question=NewQuestion, answer=New_QuestionAns, category=Question_Cat, difficulty=Question_difficulty)
            addthenewquestion.insert()
            return jsonify(
                {
                    "success": True,
                }
            )

        except:
            abort(422)
    """
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    """
    @app.route('/questions/search', methods=['POST'])
    def searchspecificquestion():
        body = request.get_json()

        searchreq = body.get("searchTerm", None)

        search = "%{}%".format(searchreq)
        try:
            SearchResult = Question.query.filter(Question.question.like(search)).all()
            loopedsearchquestions = [singleresult.format() for singleresult in SearchResult]

            return jsonify(
                {
                    "success": True,
                    'questions': loopedsearchquestions,
                    'totalQuestions':len(Question.query.all()),
                }
            )
        except:
            abort(422)
    """
    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
        DONE
    """
    @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
    def getcategoryquestions(cat_id):
        try:
            findthecategory = Category.query.filter(Category.id == cat_id).one_or_none()

            if findthecategory is None:
                abort(404)

            fetchcatquestions = Question.query.filter(Question.category == cat_id).all()

            categoryloopedquestions = [eachquestion.format() for eachquestion in fetchcatquestions]
            

            return jsonify({
                'success': True,
                'questions':categoryloopedquestions,
                'totalQuestions':len(Question.query.all()),
                'currentCategory': findthecategory.type
            })

        except:
            abort(422)
        

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    """
    @app.route('/quizzes', methods=['POST'])
    def playQuizgame():
        body = request.get_json()

        prevQuestion = body.get("previous_questions", None)
        category_of_quiz = body.get("quiz_category", None)
        try:
            # print(prevQuestion)
            
            # if category_of_quiz['id'] == 0:
            #     get_questions = random.choice(Question.query.filter(Question.id not in prevQuestion).all())
            # else:
            #     get_questions = random.choice(Question.query.filter(and_(Question.category == category_of_quiz['id'], Question.id not in prevQuestion)).all())
            if category_of_quiz['id'] == 0:
                get_questions = Question.query.all()
            else:
                get_questions = Question.query.filter(Question.category == category_of_quiz['id']).all()
            
            notInPrevQuestion = [item for item in get_questions if item not in prevQuestion]
            # quiz = list(get_questions.items())
            randomItem = random.choice(notInPrevQuestion)
            # print(category_of_quiz)

            return jsonify(
                {
                    "success": True,
                    "question": randomItem.format()
                }
            )

        except:
            abort(422)

    """
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
        DONE
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )
    @app.errorhandler(500)
    def Server_error_occurred(error):
        return (
            jsonify({"success": False, "error": 500, "message": "Internal Server Error"}),
            405,
        )

    return app

