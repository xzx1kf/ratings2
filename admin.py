from flask_admin import Admin, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from app import app, db
from models import Fixture, League, Team, Team_Stats

from flask_admin.model.ajax import DEFAULT_PAGE_SIZE
from flask import request
from sqlalchemy import or_
from flask import Response
from flask import json

admin = Admin(app, name='Football Ratings', template_mode='bootstrap3')

class FilteredAjaxModelLoader(QueryAjaxModelLoader):
    def get_list(self, term, offset=0,
                 limit=DEFAULT_PAGE_SIZE, filter_by=None):
        query = self.session.query(self.model)
        filter_by_options = self.options.get('filter_by')
        if filter_by_options and filter_by:
            filter_by = self.session.query(
                filter_by_options[0]).filter_by(
                    id=filter_by).first()
            if filter_by:
                query = query.filter(
                    getattr(
                        self.model,
                        filter_by_options[1]
                    )
                    ==filter_by.id)
        filters = (
            field.ilike(
                u'%%%s%%' % term) for field in self._cached_fields)
        query = query.filter(or_(*filters))

        if self.order_by:
            query = query.order_by(self.order_by)

        return query.offset(offset).limit(limit).all()

class TeamView(ModelView):
    form_excluded_columns = ['team_stats',]

class FixtureView(ModelView):
    column_filter_by = ('home_team')

    form_widget_args = {
        'home_team': {
            'data-filter-by': 'league',
            },
        }

    form_ajax_refs = {
        'home_team': FilteredAjaxModelLoader(
            'home_team', db.session, Team,
            fields=('name',),
            page_size=10,
            placeholder='Select home team...',
            filter_by=(League, 'league_id'),
            ),
        }


    @expose('/ajax/lookup/')
    def ajax_lookup(self):
        name = request.args.get('name')
        query = request.args.get('query')
        offset = request.args.get('offset', type=int)
        limit = request.args.get('limit', 10, type=int)
        filter_by = request.args.get('filter_by')

        loader = self._form_ajax_refs.get(name)

        if not loader:
            abort(404)

        if name in self.column_filter_by:
            data = [loader.format(m) for m in loader.get_list(
                query, offset, limit, filter_by)]
        else:
            data = [loader.format(m) for m in loader.get_list(
                query, offset, limit)]
        return Response(json.dumps(data), mimetype='application/json')

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
