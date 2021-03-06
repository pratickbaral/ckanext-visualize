import ckan.plugins as p
from ckan.tests import helpers, factories
from ckan.plugins import toolkit

from ckanext.visualize.plugin import VisualizePlugin

ignore_missing = p.toolkit.get_validator('ignore_missing')


class TestVisualizeView(helpers.FunctionalTestBase):

    @classmethod
    def setup_class(self):
        super(TestVisualizeView, self).setup_class()

        if not p.plugin_loaded('visualize'):
            p.load('visualize')

        if not p.plugin_loaded('datastore'):
            p.load('datastore')

        self.plugin = VisualizePlugin()

    @classmethod
    def teardown_class(self):
        super(TestVisualizeView, self).teardown_class()

        p.unload('visualize')
        p.unload('datastore')

        helpers.reset_db()

    def test_info(self):
        assert self.plugin.info() == {
            'name': 'visualize',
            'title': toolkit._('Visualize data'),
            'icon': 'bar-chart-o',
            'filterable': True,
            'iframed': False,
            'schema': {
                'visualize_x_axis': [ignore_missing],
                'visualize_y_axis': [ignore_missing],
                'visualize_color_attr': [ignore_missing],
            }
        }

    def test_can_view(self):
        data_dict = {'resource': {'datastore_active': True}}
        assert self.plugin.can_view(data_dict) is True

        data_dict = {'resource': {'datastore_active': False}}
        assert self.plugin.can_view(data_dict) is False

        data_dict = {'resource': {}}
        assert self.plugin.can_view(data_dict) is False

    def test_setup_template_variables(self):
        dataset = factories.Dataset()
        resource = factories.Resource(
            schema='',
            validation_options='',
            package_id=dataset.get('id'),
            datastore_active=True,
        )
        data = {
            'fields': [
                {'id': 'Age', 'type': 'numeric'},
                {'id': 'Name', 'type': 'text'},
            ],
            'records': [
                {'Age': 35, 'Name': 'John'},
                {'Age': 28, 'Name': 'Sara'},
            ],
            'force': True,
            'resource_id': resource.get('id'),
        }
        helpers.call_action('datastore_create', **data)
        data_dict = {
            'resource': {'id': resource.get('id')},
            'resource_view': {},
        }

        result = self.plugin.setup_template_variables({}, data_dict)

        assert result == {
            'resource': {'id': resource.get('id')},
            'resource_view': {},
            'fields': [{'value': u'Age', 'type': 'numeric'}, {'value': u'Name', 'type': 'text'}],
            'point_chart_icon': '/base/images/Point-symbol.png',
            'line_chart_icon': '/base/images/Line-symbol.png',
            'bar_chart_icon': '/base/images/Bar-symbol.png',
        }

    def test_view_template(self):
        assert self.plugin.view_template({}, {}) == 'visualize_view.html'

    def test_update_config_schema(self):
        assert 'visualize_colors' in self.plugin.update_config_schema({})
