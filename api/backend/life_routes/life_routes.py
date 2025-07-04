from flask import (
    Blueprint,
    request,
    jsonify,
    make_response,
    current_app,
    redirect,
    url_for,
)
from backend.db_connection import db 
from mysql.connector import Error
from backend.ml_models import model01


users = Blueprint("users", __name__)
@users.route("/users/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    try:
        cursor = db.get_db().cursor()

        query = """
            SELECT u.user_ID, u.user_name, u.user_country, r.role_name
            FROM User u
            JOIN User_Role r ON u.role_ID = r.role_ID
            WHERE u.user_ID = %s
        """
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()

        if not user:
            cursor.close()
            return jsonify({"error": "User not found"}), 404
        cursor.close()
        return jsonify(user), 200

    except Error as e:
        current_app.logger.error(f'Database error in get_user_by_id: {str(e)}')
        return jsonify({"error": str(e)}), 500
    
@users.route("/users/role/<role_name>", methods=["GET"])
def get_role_id_by_name(role_name):
    try:
        cursor = db.get_db().cursor()

        query = """
            SELECT role_ID
            FROM User_Role
            WHERE role_name = %s
        """
        cursor.execute(query, role_name)
        role = cursor.fetchone()
        cursor.close()
        if role:
            return jsonify(role["role_ID"]), 200
        else:
            return jsonify({"error": "Role not found"}), 404
    except Error as e:
        current_app.logger.error(f'Database error in get_role_id_by_name: {str(e)}')
        return jsonify({"error": str(e)}), 500

@users.route("/users/role/<int:role_id>", methods=["GET"])
def get_usernames_by_role_id(role_id):
    try:
        cursor = db.get_db().cursor()

        query = """
            SELECT user_name
            FROM User
            WHERE role_ID = %s
        """
        cursor.execute(query, (role_id))
        users = cursor.fetchall()
        cursor.close()
    
        usernames = [user["user_name"] for user in users]
        return jsonify(usernames), 200

    except Error as e:
        current_app.logger.error(f'Database error in get_user_by_role_id: {str(e)}')
        return jsonify({"error": str(e)}), 500
    
@users.route("/users/getID/<user_name>", methods=["GET"])
def get_user_id(user_name):
    try:
        cursor = db.get_db().cursor()

        query = """
            SELECT user_id
            FROM User
            WHERE user_name = %s
        """
        cursor.execute(query, (user_name))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return jsonify({"user_id": user["user_id"]}), 200
        else:
            return jsonify({"error": "User not found"}), 404

    except Error as e:
        current_app.logger.error(f'Database error in get_user_by_role_id: {str(e)}')
        return jsonify({"error": str(e)}), 500
    
@users.route('/users/remove/<int:user_id>', methods=["DELETE"])
def remove_user(user_id):
    try:
        cursor = db.get_db().cursor()
        query = 'DELETE FROM User WHERE user_ID = %s'
        cursor.execute(query, (user_id,))
        
        if cursor.rowcount == 0:
            cursor.close()
            return jsonify({'error': 'User not found'}), 404

        db.get_db().commit()
        cursor.close()
        return jsonify({'message': f'User {user_id} deleted successfully'}), 200

    except Error as e:
        return jsonify({'error': str(e)}), 500

  
@users.route('/users/name', methods=['PUT'])
def update_name():
    current_app.logger.info('PUT /users/name route')
    user_info = request.json
    user_id = user_info['user_id']
    user_name = user_info['user_name']

    query = 'UPDATE User SET user_name = %s WHERE user_id = %s'
    data = (user_name, user_id)
    cursor = db.get_db().cursor()
    cursor.execute(query, data)
    db.get_db().commit()
    cursor.close()

    return jsonify({'message': 'User name updated successfully'}), 200

grace = Blueprint("grace", __name__)
@grace.route("/pred_scores", methods=["GET"])
def get_all_pred_scores():
    try:
        current_app.logger.info('Starting get_all_pred_scores request')
        cursor = db.get_db().cursor()

        # Get query parameters for filtering
        scores = request.args.get("pred_score")
        factor = request.args.get("factor_id")
        country = request.args.get("country_id")

        current_app.logger.debug(f'Query parameters - country_id: {country}, factor_id: {factor}, pred_score: {scores}')

        # Prepare the Base query
        query = "SELECT * FROM Predicted Scores WHERE 1=1"
        params = []

        # Add filters if provided
        if country:
            query += " AND country_ID = %s"
            params.append(country)
        if factor:
            query += " AND factor_ID = %s"
            params.append(factor)
        if scores:
            query += " AND pred_score = %s"
            params.append(scores)

        current_app.logger.debug(f'Executing query: {query} with params: {params}')
        cursor.execute(query, params)
        grace_scores = cursor.fetchall()
        cursor.close()

        current_app.logger.info(f'Successfully retrieved {len(grace_scores)} countries')
        return jsonify(grace_scores), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_all_pred_scores: {str(e)}')
        return jsonify({"error": str(e)}), 500

# @grace.route("/preferences/by_user/<int:user_id>", methods=["GET"])
# def get_preferences_by_user(user_id):
#     try:
#         cursor = db.get_db().cursor(dictionary=True)
#         cursor.execute("""
#             SELECT pref_ID, pref_date, top_country 
#             FROM Preference 
#             WHERE user_ID = %s
#             ORDER BY pref_date DESC
#         """, (user_id,))
#         preferences = cursor.fetchall()
#         cursor.close()

#         return jsonify(preferences), 200
#     except Error as e:
#         return jsonify({"error": str(e)}), 500
    
@grace.route("/pred_scores/<int:country_id>", methods=["GET"])
def get_pred_scores_by_country(country_id):
    try:
        cursor = db.get_db().cursor(dictionary=True)
        cursor.execute("""
            SELECT factor_ID, pred_score 
            FROM Predicted_Score 
            WHERE country_ID = %s
        """, (country_id,))
        scores = cursor.fetchall()
        cursor.close()

        if scores:
            return jsonify(scores), 200
        else:
            return jsonify({"error": "No scores found for country"}), 404
    except Error as e:
        return jsonify({"error": str(e)}), 500

@grace.route("/university/<int:country_id>", methods=["GET"])
def get_unis_by_country(country_id):
    try:
        cursor = db.get_db().cursor()
        cursor.execute("SELECT * FROM University WHERE Country_ID = %s", (country_id,))
        universities = cursor.fetchall()
        cursor.close()

        return jsonify(universities), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500


@grace.route("/preference", methods=["POST"])
def create_preference():
    try:
        current_app.logger.info('Starting create_preference request')
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        cursor = db.get_db().cursor()
        query = """
            INSERT INTO Preference (user_ID, pref_date, top_country, factorID_1, weight1, factorID_2, weight2, factorID_3, weight3,
            factorID_4, weight4)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data.get('user_ID'),
            data.get('pref_date'),
            data.get('top_country'),
            data.get('factorID_1'),
            data.get('weight1'),
            data.get('factorID_2'),
            data.get('weight2'),
            data.get('factorID_3'),
            data.get('weight3'),
            data.get('factorID_4'),
            data.get('weight4')
        ))
        db.get_db().commit()
        cursor.close()

        current_app.logger.info('Preference created successfully')
        return jsonify({"message": "Preference created successfully"}), 201
    except Error as e:
        current_app.logger.error(f'Database error in create_preference: {str(e)}')
        return jsonify({"error": str(e)}), 500
    
@grace.route("/preference/<int:user_ID>", methods=["GET"])
def get_pref_topcountry(user_ID):
    try:
        cursor = db.get_db().cursor()
        cursor.execute("""
            SELECT pref_ID, top_country
            FROM Preference
            WHERE user_ID = %s
            ORDER BY pref_date DESC
            LIMIT 5
        """, (user_ID,))
        prefs = cursor.fetchall()
        cursor.close()

        pref_list = [
            {"pref_ID": row["pref_ID"], "top_country": row["top_country"]}
            for row in prefs
        ]

        return jsonify(pref_list), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500


model = Blueprint("model", __name__)
@model.route("/predict/<education>/<health>/<safety>/<environment>", methods=["GET"])
def get_predict(education, health, safety, environment):
    try:
        current_app.logger.info("GET /predict handler")
        
        education = float(education)
        health = float(health)
        safety = float(safety)
        environment = float(environment)

        similarity = model01.predict(health, education, safety, environment)
        current_app.logger.info(f"Cosine similarity value returned is {similarity}")

        response_data = similarity.to_dict()

        return jsonify(response_data), 200

    except Exception as e:
        response = make_response(
            jsonify({"error": "Error processing prediction request"}, {'e':e})
        )
        response.status_code = 500
        return response


@model.route("/pred_scores/<var_01>/<var_02>", methods=["GET"])
def get_pred_scores(var_01, var_02):
    current_app.logger.info("GET /prediction handler")

    try:
        prediction = model03.predict(var_01, var_02)
        current_app.logger.info(f"prediction value returned is {prediction}")
        
        response_data = {
            "prediction": prediction,
            "input_variables": {"var01": var_01, "var02": var_02},
        }

        response = make_response(jsonify(response_data))
        response.status_code = 200
        return response

    except Exception as e:
        response = make_response(
            jsonify({"error": "Error processing prediction request"})
        )
        response.status_code = 500
        return response
    
country = Blueprint("country", __name__)
@country.route("/countries", methods=["GET"])
def get_countries():
    try:
        cursor = db.get_db().cursor()
        cursor.execute('SELECT country_name FROM Country')
        rows = cursor.fetchall()
        cursor.close()

        countries = [row["country_name"] for row in rows]

        return jsonify(countries)
    except Error as e:
        return jsonify({"error": str(e)}), 500    
    
@country.route("/country", methods=["GET"])
def get_country_ID():
    try:
        cursor = db.get_db().cursor()
        cursor.execute('SELECT country_ID, country_name FROM Country')
        rows = cursor.fetchall()
        cursor.close()

        countries = [{"country_name": row["country_name"], "country_ID": row["country_ID"]} for row in rows]

        return jsonify(countries), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    

@country.route("/factor", methods=["GET"])
def get_factor_ID():
    try:
        cursor = db.get_db().cursor()
        cursor.execute('SELECT factor_ID, factor_name FROM Factor')
        rows = cursor.fetchall()
        cursor.close()

        factors = [{"factor_name": row["factor_name"], "factor_ID": row["factor_ID"]} for row in rows]

        return jsonify(factors), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

    

faye = Blueprint("faye", __name__)
@faye.route("/orgs/<int:country_ID>/<int:factor_ID>", methods=["GET"])
def get_orgs_by_country_and_factor(country_ID, factor_ID):
    try:   
        cursor = db.get_db().cursor()
        query = """
            SELECT * FROM Organization
            WHERE org_country = %s AND org_factor = %s
        """
        cursor.execute(query, (country_ID, factor_ID))
        orgs = cursor.fetchall() 
        cursor.close()
    
        if not orgs:
            return jsonify({"error": "No organizations found for that factor and country"}), 404

        return jsonify(orgs), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    
@faye.route("/scores", methods=["GET"])
def get_scores():
    try:
        cursor = db.get_db().cursor()
        cursor.execute("""
            SELECT C.country_name, S.health_score, S.education_score, S.safety_score, S.environment_score
            FROM ML_Score S
            JOIN Country C ON S.country_ID = C.country_ID
            WHERE S.score_year = 2022
        """)
        scores = cursor.fetchall()
        cursor.close()

        return jsonify(scores)
    except Error as e:
        return jsonify({"error": str(e)}), 500



