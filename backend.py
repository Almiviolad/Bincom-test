from flask import Flask, request, jsonify, render_template
from flask_mysqldb import MySQL

app = Flask(__name__)

# Database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'almiviolad'
app.config['MYSQL_DB'] = 'bincomtest'

mysql = MySQL(app)

@app.route("/")
def home():
    return render_template("index.html")  # Renders index.html


@app.route("/<int:state_id>/lga")
def get_all_lga(state_id):
    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT lga_id, lga_name FROM lga WHERE state_id = %s", (state_id,))
            lgas = cursor.fetchall()
        if not lgas:
            return jsonify({"error": "No LGA found for this state"}), 404
        return jsonify([{"lga_id": lga[0], "lga_name": lga[1]} for lga in lgas])
    except Exception as err:
        return jsonify({"error": "Internal server error", "message": str(err)}), 500


@app.route("/<int:state_id>/<int:lga_id>/wards")
def get_all_wards(state_id, lga_id):
    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT ward_id, ward_name FROM ward WHERE lga_id = %s", (lga_id,))
            wards = cursor.fetchall()
        if not wards:
            return jsonify({"error": "No ward found for this LGA"}), 404
        return jsonify([{"ward_id": ward[0], "ward_name": ward[1]} for ward in wards])
    except Exception as err:
        return jsonify({"error": "Internal server error", "message": str(err)}), 500

@app.route("/<int:state_id>/<int:lga_id>/<int:ward_id>/pu")
def get_all_pu(state_id, lga_id, ward_id):
    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT uniqueid, polling_unit_id, polling_unit_name FROM polling_unit WHERE lga_id = %s AND ward_id = %s", (lga_id, ward_id))
            pus = cursor.fetchall()
        if not pus:
            return jsonify({"error": "No polling unit found for this ward"}), 404
        return jsonify([{"polling_unit_uniqueid": pu[0], "polling_unit_id": pu[1], "polling_unit_name": pu[2]} for pu in pus])
    except Exception as err:
        return jsonify({"error": "Internal server error", "message": str(err)}), 500

@app.route("/parties")
def get_all_parties():
    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT partyid, partyname FROM party")
            parties = cursor.fetchall()
        if not parties:
            return jsonify({"error": "No party found"}), 404
        return jsonify([{"party_id": party[0], "party_name": party[1]} for party in parties])
    except Exception as err:
        return jsonify({"error": "Internal server error", "message": str(err)}), 500

@app.route("/<int:polling_unit_uniqueid>")
def get_pu_results(polling_unit_uniqueid):
    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT result_id, polling_unit_uniqueid, party_abbreviation, party_score FROM announced_pu_results WHERE polling_unit_uniqueid = %s", (polling_unit_uniqueid,))
            pu_results = cursor.fetchall()
        if not pu_results:
            return jsonify({"error": "No result found for this polling unit"}), 404
        return jsonify([{"result_id": pu_res[0], "polling_unit_uniqueid": pu_res[1], "party": pu_res[2], "score": pu_res[3]} for pu_res in pu_results])
    except Exception as err:
        return jsonify({"error": "Internal server error", "message": str(err)}), 500

@app.route("/<int:lga_id>/results")    
def get_pu_results_in_lga(lga_id):
    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute("""
                SELECT apr.party_abbreviation, SUM(apr.party_score) as total_score
                FROM announced_pu_results apr 
                JOIN polling_unit pu ON apr.polling_unit_uniqueid = pu.polling_unit_id
                WHERE pu.lga_id = %s
                GROUP BY apr.party_abbreviation
                ORDER BY total_score DESC
            """, (lga_id,))
            lga_pu_results = cursor.fetchall()
        if not lga_pu_results:
            return jsonify({"error": "No polling unit results found for this LGA"}), 404
        return jsonify([{"party": result[0], "total_score": result[1]} for result in lga_pu_results])
    except Exception as err:
        return jsonify({"error": "Internal server error", "message": str(err)}), 500

@app.route("/add_pu_result", methods=["POST"])
def post_pu_results():
    data = request.get_json()
    
    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO announced_pu_results (polling_unit_uniqueid, party_abbreviation, party_score, entered_by_user, date_entered, user_ip_address) 
                VALUES (%s, %s, %s, %s, NOW(), %s)
            """, (data["pu_uid"], data["party_abbr"], data["party_score"], data["user"], request.remote_addr))
        
        mysql.connection.commit()
        return jsonify({"message": "Polling unit and votes added successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/results")
def results():
    with mysql.connection.cursor() as cursor:
        cursor.execute("SELECT lga_id, lga_name FROM lga WHERE state_id = 25")
        lgas = cursor.fetchall()
        print(lgas)
    return render_template("results.html", lgas=lgas)

if __name__ == "__main__":
    app.run(debug=True)
