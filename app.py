from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

flavours = []

@app.route('/')
def home():
    # Retrieve data from database
    conn = sqlite3.connect("ice_cream_rating.db")
    c = conn.cursor()
    c.execute("SELECT * FROM ice_cream_rating;")
    rows = c.fetchall()
    column_names = [description[0] for description in c.description]
    conn.close()

    # Convert into a list and sort by rating
    flavours = [dict(zip(column_names, row)) for row in rows]
    top_5 = sorted(flavours, key=lambda k: k['rating'], reverse=True)[:5]

    return render_template("index.html", flavours=flavours, top_5=top_5)

@app.route('/search', methods=["GET"])
def search():
    if not None:
        # Retrieves search term and format it
        flavour_name = request.args.get("flavour_name")
        flavour_name = flavour_name.split()
        flavour_name = [word.capitalize() for word in flavour_name]
        flavour_name = " ".join(flavour_name)

        # Search through the database for a record that includes the name
        conn = sqlite3.connect("ice_cream_rating.db")
        c = conn.cursor()
        c.execute("SELECT * FROM ice_cream_rating WHERE flavour_name = ?;", (flavour_name,))
        row = c.fetchone()

        # Redirects user to the page requested if exists
        if row:
            row = list(row)
            index = row[0]
            return redirect(url_for("profile", flavour_id=index))

    return redirect(url_for("home"))

@app.route("/<flavour_id>")
def profile(flavour_id):
    
    # Retrieves information from the record with the specified ID
    conn = sqlite3.connect("ice_cream_rating.db")
    c = conn.cursor()
    c.execute("SELECT  * FROM ice_cream_rating WHERE flavour_id = ?;", (flavour_id,))
    info = c.fetchone()

    if info:
        # Redirects thte user to the page desired if exists
        column_names = [description[0] for description in c.description]
        info = dict(zip(column_names, info))
        conn.close()
        return render_template("flavour_profile.html", info=info)
    else:
        # Redirects user to the home page if not
        conn.close()
        return redirect(url_for("home"))

@app.route("/submit_rating", methods=["POST"])
def submit_rating():
    # Obtain the id of the flavour
    flavour_id = request.form.get("flavour_id")

    # Retrieves the record of that flavour in the database
    conn = sqlite3.connect("ice_cream_rating.db")
    c = conn.cursor()
    c.execute("SELECT  * FROM ice_cream_rating WHERE flavour_id = ?;", (flavour_id,))
    info = c.fetchone()
    column_names = [description[0] for description in c.description]
    info = dict(zip(column_names, info))

    # Obtain the rating submitted and check if the rating is not None
    rating = request.form.get("rating")
    if rating is not None:
        rating = float(rating)
    else:
        return redirect(url_for("profile", flavour_id=flavour_id))

    # Recalculate the average rating and the number of ratings
    current_rating = float(info["rating"])
    no_of_ratings = int(info["no_of_ratings"])
    if no_of_ratings != 0:
        total = current_rating*no_of_ratings + rating
    else:
        total = rating
        
    average  = round(float(total / (no_of_ratings + 1)), 2)
    no_of_ratings += 1

    # Update the database
    c.execute("UPDATE ice_cream_rating SET rating = ?, no_of_ratings = ? WHERE flavour_id = ?;", (average, no_of_ratings, info["flavour_id"]))
    conn.commit()
    conn.close()
    
    return redirect(url_for("profile", flavour_id=flavour_id))

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
