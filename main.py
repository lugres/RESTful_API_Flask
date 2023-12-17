from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from werkzeug.exceptions import HTTPException

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# with app.create_contect():
#     db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/all")
def get_all_cafes():
    all_cafes = db.session.execute(db.select(Cafe).order_by(Cafe.name)).scalars()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


@app.route("/search")
def search_cafe_by_location():
    query_location = request.args.get("loc")
    all_cafes_found = db.session.execute(db.select(Cafe).where(Cafe.location == query_location)).scalars().all()

    if all_cafes_found:
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes_found])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


@app.route("/random")
def get_random_cafe():
    random_cafe = db.session.execute(db.select(Cafe).order_by(func.random())).scalar()
    return jsonify(cafe=random_cafe.to_dict())

    # random_cafe = db.session.execute(db.select(Cafe).order_by(func.random())).scalar()
    # return jsonify(cafe={
    #     # "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #     "amneties":{
    #     "seats": random_cafe.seats,
    #     "has_toilet": random_cafe.has_toilet,
    #     "has_wifi": random_cafe.has_wifi,
    #     "has_sockets": random_cafe.has_sockets,
    #     "can_take_calls": random_cafe.can_take_calls,
    #     "coffee_price": random_cafe.coffee_price,}})


## HTTP GET - Read Record

## HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_a_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


## HTTP PUT/PATCH - Update Record
# @app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
# def update_coffee_price(cafe_id):
#     new_coffee_price = request.args.get("new_price")
#     # is the cafe with the specified id available in the DB?
#     cafe_found = db.get_or_404(Cafe, cafe_id, description=f"Sorry, we don't have a cafe with id {cafe_id}.")
#     # if yes, update the DB record with the new price, notify user about success
#     # if not, generate error message
#     if cafe_found:
#         cafe_found.coffee_price = new_coffee_price
#         db.session.commit()
#         return jsonify(response={"success": f"Successfully updated coffee price for cafe with id {cafe_id}."}), 200
#     else:
#         # this is never triggered - use db.session.get() instead of db.get_or_404()
#         return jsonify(error={"Not Found": f"Sorry, we don't have a cafe with id {cafe_id}."}), 404

# An update PATCH route - correctly handling 404 message, delivering our own error message
# Instead of try/except and .get_or_404() method we could have used similar if/else as above with db.session.get()
# See comments to the last solution inside the lesson
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_coffee_price(cafe_id):
    new_coffee_price = request.args.get("new_price")
    # is the cafe with the specified id available in the DB?
    # if yes, update the DB record with the new price, notify user about success
    # if not, generate error message
    try:
        cafe_found = db.get_or_404(Cafe, cafe_id)
        cafe_found.coffee_price = new_coffee_price
        db.session.commit()
        return jsonify(response={"success": f"Successfully updated coffee price for the cafe with id {cafe_id}."})
    except HTTPException as error:
        error.description = f"Sorry, Cafe with id: {cafe_id} was not found in the database"
        return jsonify(error={error.name: error.description}), error.code


## HTTP DELETE - Delete Record
# Deletes a cafe with a particular id. Change the request type to "Delete" in Postman
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        cafe = db.session.get(Cafe, cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": f"Sorry a cafe with the ID {cafe_id} was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

if __name__ == '__main__':
    app.run(debug=True)
