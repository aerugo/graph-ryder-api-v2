from routes.generics.getters import *


def add_generics_routes(api):

    # GET
    api.add_resource(GetLabelsByLabel, '/getLabels/<string:label>')
    api.add_resource(GetLabelsById, '/getLabels/<int:id>')  # todo usefull ?

    api.add_resource(GetPropertiesByLabel, '/getProperties/<string:label>')
    api.add_resource(GetPropertyValueByLabel, '/getPropertyValue/<string:label>/<string:key>')

    api.add_resource(GetAttributesByLabel, '/getAttributes/<string:label>')

    # GET Element(s)
    api.add_resource(GetByLabel, '/getByLabel/<string:label>')
    api.add_resource(GetById, '/getById/<int:id>')