from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app import app, db
from models import Fixture, League, Team, Team_Stats


admin = Admin(app, name='Football Ratings', template_mode='bootstrap3')


class TeamView(ModelView):
    form_excluded_columns = ['team_stats',]

class FixtureView(ModelView):
    """
    The on_model_change allows me to insert some logic. So in the case
    of the fixture save I can calculate fixture stats etc
    """
    def on_model_change(self, form, model, is_created):
        print("{}".format(model.home_team.name))

admin.add_view(FixtureView(Fixture, db.session))
admin.add_view(ModelView(League, db.session))    
admin.add_view(TeamView(Team, db.session))
admin.add_view(ModelView(Team_Stats, db.session))
