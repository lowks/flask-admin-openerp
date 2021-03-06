from flask.ext.admin.model import BaseModelView
from .form import Form
from .filters import *


class OpenERPModelView(BaseModelView):

    def get_pk_value(self, model):
        return model.id

    def scaffold_list_columns(self):
        return self.model.fields_get().keys()

    def scaffold_sortable_columns(self):
        return None

    def scaffold_form(self):
        oo_form = Form(self)
        return oo_form.create_form()

    def scaffold_filters(self, name):
        field = self.model.fields_get([name])[name]
        field_type = field.get('type', 'float')
        label = field.get('string', name)
        flt = []
        if field_type == 'boolean':
            flt += [OpenerpBooleanFilter(name)]
        else:
            flt += [OpenerpEqualFilter(label, name)]
            if field_type in ('char', 'text'):
                flt += [OpenerpLikeFilter(label, name)]
            else:
                flt += [
                    OpenerpGreaterFilter(label, name),
                    OpenerpLesserFilter(label, name)
                ]
        return flt

    def init_search(self):
        return False

    def get_one(self, object_id):
        object_id = int(object_id)
        return self.model.browse(object_id)

    def get_list(self, page, sort_field, sort_desc, search, flts):
        limit = self.page_size
        offset = page * limit
        query = []
        if not flts:
            flts = []
        for flt, value in flts:
            query = self._filters[flt].apply(query, value)
        n_items = self.model.search_count(query)
        ids = self.model.search(query, offset=offset, limit=limit)
        if not ids:
            res = []
        else:
            res = self.model.browse(ids)
        return n_items, res

    def create_model(self, form):
        return self.model.create(form.data)

    def update_model(self, form, model):
        return model.write(form.data)

    def delete_model(self, model):
        return model.unlink()
