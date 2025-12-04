from flask import Flask, render_template, request, redirect, url_for
from db import get_db_connection
import random
from datetime import datetime

app = Flask(__name__)

# ------------------ TOKEN GENERATOR ------------------
def generate_token():
    num = random.randint(0, 999)
    return f"{num:03d}"
	

# ------------------ DASHBOARD ------------------
@app.route("/")
def dashboard():
    return render_template("dashboard.html")


# ------------------ REQUIRED FIX ------------------
@app.route("/status")
def status():
    return render_template("status.html")
# ----------------------------------------------------


# ------------------ PARKING INFORMATION ------------------
@app.route("/parking-rates")
def parking_rates():
    return render_template("parking_rates.html")

@app.route("/opening-hours")
def opening_hours():
    return render_template("opening_hours.html")

@app.route("/rules")
def rules():
    return render_template("rules.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/places")
def places_info():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT place_id, place_name FROM places")
    places = cur.fetchall()
    conn.close()
    return render_template("places_info.html", places=places)


# ------------------ USER SERVICES ------------------
@app.route("/check-token", methods=["GET", "POST"])
def check_token():
    data = None
    if request.method == "POST":
        token = request.form["token"]

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT token, user_name, mobile, vehicle_type, vehicle_number,
                   place_id, slot_id, entry_time
            FROM vehicle_entry
            WHERE token = %s
        """, (token,))
        data = cur.fetchone()

        conn.close()

        if not data:
            flash("No vehicle found with this token!")
    
    return render_template("check_token.html", data=data)

@app.route("/lost-token")
def lost_token():
    return render_template("lost_token.html")

@app.route("/help")
def help_page():
    return render_template("help.html")


# ------------------ ANALYTICS ------------------
@app.route("/stats/today")
def stats_today():
    conn = get_db_connection()
    cur = conn.cursor()

    # Total vehicles today
    cur.execute("""
        SELECT COUNT(*) FROM vehicle_entry
        WHERE DATE(entry_time) = CURDATE()
    """)
    total_today = cur.fetchone()[0]

    # Cars today
    cur.execute("""
        SELECT COUNT(*) FROM vehicle_entry
        WHERE vehicle_type='car' AND DATE(entry_time) = CURDATE()
    """)
    cars_today = cur.fetchone()[0]

    # Bikes today
    cur.execute("""
        SELECT COUNT(*) FROM vehicle_entry
        WHERE vehicle_type='bike' AND DATE(entry_time) = CURDATE()
    """)
    bikes_today = cur.fetchone()[0]

    # Recent tokens → NOW ALSO includes vehicle number
    cur.execute("""
        SELECT vehicle_type, vehicle_number, entry_time
        FROM vehicle_entry
        WHERE DATE(entry_time)=CURDATE()
        ORDER BY entry_time DESC
        LIMIT 10
    """)
    recent_list = cur.fetchall()

    conn.close()

    return render_template(
        "stats_today.html",
        total_today=total_today,
        cars_today=cars_today,
        bikes_today=bikes_today,
        recent_list=recent_list
    )

@app.route("/stats/earnings")
def stats_earnings():
    conn = get_db_connection()
    cur = conn.cursor()

    # Calculate today's total earnings
    cur.execute("""
        SELECT COALESCE(SUM(charge), 0)
        FROM vehicle_entry
        WHERE DATE(exit_time) = CURDATE()
    """)
    earnings_today = cur.fetchone()[0]

    conn.close()

    return render_template("stats_earnings.html", earnings_today=earnings_today)

@app.route("/stats/occupancy")
def stats_occupancy():
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch all places
    cur.execute("SELECT place_id, place_name FROM places")
    places = cur.fetchall()

    place_data = []

    for pid, pname in places:

        # total slots in this place
        cur.execute("SELECT COUNT(*) FROM parking_slots WHERE place_id=%s", (pid,))
        total = cur.fetchone()[0]

        # occupied slots
        cur.execute("SELECT COUNT(*) FROM parking_slots WHERE place_id=%s AND status='occupied'", (pid,))
        occupied = cur.fetchone()[0]

        # free slots
        cur.execute("SELECT COUNT(*) FROM parking_slots WHERE place_id=%s AND status='available'", (pid,))
        free = cur.fetchone()[0]

        # total active vehicles in this place
        cur.execute("""
            SELECT COUNT(*) FROM vehicle_entry 
            WHERE place_id=%s AND exit_time IS NULL
        """, (pid,))
        vehicles = cur.fetchone()[0]

        # cars
        cur.execute("""
            SELECT COUNT(*) FROM vehicle_entry 
            WHERE place_id=%s AND vehicle_type='car' AND exit_time IS NULL
        """, (pid,))
        cars = cur.fetchone()[0]

        # bikes
        cur.execute("""
            SELECT COUNT(*) FROM vehicle_entry 
            WHERE place_id=%s AND vehicle_type='bike' AND exit_time IS NULL
        """, (pid,))
        bikes = cur.fetchone()[0]

        # percentage
        percent = (occupied / total * 100) if total > 0 else 0

        place_data.append({
            "place_name": pname,
            "total": total,
            "occupied": occupied,
            "free": free,
            "vehicles": vehicles,
            "cars": cars,
            "bikes": bikes,
            "percent": int(percent)
        })

    conn.close()

    return render_template("stats_occupancy.html", place_data=place_data)

@app.route("/stats/recent")
def stats_recent():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT vehicle_number,
               vehicle_type,
               place_id,
               slot_id,
               entry_time
        FROM vehicle_entry
        WHERE DATE(entry_time) = CURDATE()
        ORDER BY entry_time DESC
        LIMIT 10
    """)
    recent_entries = cur.fetchall()

    conn.close()
    return render_template("stats_recent.html", recent_entries=recent_entries)

# ------------------ WEBSITE EXTRAS ------------------
@app.route("/weather")
def weather():
    return render_template("weather.html")

@app.route("/about-system")
def about_system():
    return render_template("about_system.html")

@app.route("/news")
def news():
    return render_template("news.html")

# ------------------ VEHICLE ENTRY ------------------
@app.route("/vehicle/entry", methods=["GET", "POST"])
def vehicle_entry():
    conn = get_db_connection()
    cur = conn.cursor()

    # --------- WHEN FORM IS SUBMITTED ---------
    if request.method == "POST":
        name = request.form["name"]
        mobile = request.form["mobile"]
        vtype = request.form["vehicle_type"]
        vnum = request.form["vehicle_number"]
        place_id = int(request.form["place_id"])
        entry_time = datetime.now()
        token = generate_token()

        # --------- FIND AVAILABLE SLOT ---------
        cur.execute("""
            SELECT slot_id 
            FROM parking_slots
            WHERE place_id=%s
              AND vehicle_type=%s
              AND status='available'
            ORDER BY slot_id
            LIMIT 1
        """, (place_id, vtype))

        slot = cur.fetchone()

        if not slot:
            flash("No available slots for this place & vehicle type!")
            conn.close()
            return redirect(url_for("vehicle_entry"))

        slot_id = slot[0]

        # --------- MARK SLOT AS OCCUPIED ---------
        cur.execute("""
            UPDATE parking_slots
            SET status='occupied'
            WHERE slot_id=%s
        """, (slot_id,))

        # --------- INSERT VEHICLE ENTRY ---------
        cur.execute("""
            INSERT INTO vehicle_entry
            (token, user_name, mobile, vehicle_type, vehicle_number,
             slot_id, place_id, entry_time)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (token, name, mobile, vtype, vnum, slot_id, place_id, entry_time))

        conn.commit()

        ticket = {
            "token": token,
            "name": name,
            "vehicle_type": vtype,
            "vehicle_number": vnum,
            "slot_id": slot_id,
            "entry_time": entry_time
        }

        conn.close()
        return render_template("entry_success.html", ticket=ticket)

    # --------- LOAD PLACES FOR DROPDOWN ---------
    cur.execute("SELECT place_id, place_name FROM places")
    places = cur.fetchall()
    conn.close()

    return render_template("vehicle_entry.html", places=places)

# ------------------ VEHICLE EXIT ------------------

@app.route("/vehicle-exit", methods=["GET", "POST"])
def vehicle_exit():
    if request.method == "POST":
        token = request.form["token"]

        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch the active vehicle with given token
        cur.execute("""
            SELECT entry_id, token, user_name, vehicle_type, vehicle_number,
                   slot_id, place_id, entry_time
            FROM vehicle_entry
            WHERE token=%s AND exit_time IS NULL
        """, (token,))
        entry = cur.fetchone()

        if not entry:
            conn.close()
            flash("Invalid token or vehicle already exited!")
            return redirect(url_for("vehicle_exit"))

        entry_id, token, name, vtype, vnum, slot_id, place_id, entry_time = entry

        exit_time = datetime.now()

        # Calculate duration and charges
        minutes = int((exit_time - entry_time).total_seconds() / 60)
        rate = 1 if vtype == "bike" else 3
        charge = minutes * rate

        # Save exit info in database
        cur.execute("""
            UPDATE vehicle_entry
            SET exit_time=%s, charge=%s
            WHERE entry_id=%s
        """, (exit_time, charge, entry_id))

        # Free the slot
        cur.execute("""
            UPDATE parking_slots
            SET status='available'
            WHERE slot_id=%s
        """, (slot_id,))

        conn.commit()
        conn.close()

        # Prepare receipt for template
        receipt = {
            "token": token,
            "name": name,
            "vehicle_type": vtype,
            "vehicle_number": vnum,
            "slot_id": slot_id,
            "place_id": place_id,
            "entry_time": entry_time,
            "exit_time": exit_time,
            "minutes": minutes,
            "rate": rate,
            "charge": charge   # <-- VERY IMPORTANT
        }

        return render_template("exit_receipt.html", receipt=receipt)

    return render_template("vehicle_exit.html")

# ------------------ SLOT MAP ------------------
@app.route("/slot-map/<int:place_id>/<int:highlight_slot_id>")
def slot_map(place_id, highlight_slot_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT slot_id, vehicle_type, status
        FROM parking_slots
        WHERE place_id=%s
        ORDER BY slot_id
    """, (place_id,))
    slots = cur.fetchall()

    conn.close()
    return render_template("slot_map.html",
                           slots=slots,
                           highlight_slot_id=highlight_slot_id)


# ------------------ MAIN ------------------
if __name__ == "__main__":
    app.run(debug=True)
