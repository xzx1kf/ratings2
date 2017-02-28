from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app import app, db
from models import Team, Team_Stats


admin = Admin(app, name='Football Ratings', template_mode='bootstrap3')


class TeamView(ModelView):
    form_excluded_columns = ['team_stats',]

    
admin.add_view(TeamView(Team, db.session))
admin.add_view(ModelView(Team_Stats, db.session))
