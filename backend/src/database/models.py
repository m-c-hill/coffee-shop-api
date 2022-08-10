import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
import json

database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))

db = SQLAlchemy()


def setup_db(app):
    """
    binds a flask application and a SQLAlchemy service
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

    # Add dummy data
    drink_data = [
        {
            "title": "water",
            "recipe": '[{"name": "water", "color": "blue", "parts": 1}]',
        },
        {
            "title": "matchashake",
            "recipe": '[{"name": "milk", "color": "grey", "parts": 1 }, { "name": "matcha", "color":"green", "parts":3}]',
        },
        {
            "title": "flatwhite",
            "recipe": '[{ "name":"milk", "color":"grey", "parts":3 }, { "name":"coffee", "color":"brown", "parts":1}]',
        },
        {
            "title": "cap",
            "recipe": '[{"name": "foam", "color": "white", "parts": 1 }, { "name": "milk", "color": "grey", "parts": 2}, { "name": "coffee", "color": "brown", "parts": 1}]',
        },
    ]

    for data in drink_data:
        drink = Drink(
        title=data["title"], recipe=data["recipe"]
        )
        drink.insert()


class Drink(db.Model):
    # a persistent drink entity, extends the base SQLAlchemy Model
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    title = Column(String(80), unique=True)
    recipe = Column(
        String(180), nullable=False
    )  # Lazy json blob: [{'color': string, 'name':string, 'parts':number}]

    def short(self):
        # short form representation of the Drink model

        print(json.loads(self.recipe))
        short_recipe = [
            {"color": r["color"], "parts": r["parts"]} for r in json.loads(self.recipe)
        ]
        return {"id": self.id, "title": self.title, "recipe": short_recipe}

    def long(self):
        # long form representation of the Drink model
        return {"id": self.id, "title": self.title, "recipe": json.loads(self.recipe)}

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.short())
