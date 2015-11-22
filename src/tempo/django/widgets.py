"""Provied Django-Admin widget."""
# pylint: disable=old-style-class,invalid-name,missing-docstring
# coding=utf-8
import json
import uuid

from django.forms.utils import flatatt
from django.forms.widgets import Input


class RecurrentEventSetWidget(Input):
    """Django-Admin widget, that represents RecurrentEventSet."""
    # pylint: disable=no-init,no-member
    def render(self, name, value, attrs=None):
        """Renders HTML representation and needed JavaScript."""
        # pylint: disable=no-self-use
        if value is None:
            value = ''
        elif hasattr(value, 'to_json'):
            value = json.dumps(value.to_json())

        final_attrs = self.build_attrs(attrs, name=name)
        return """
        <div id='tempo-{uuid}-controls' class='tempo-controls'>
            <input id='tempo-{uuid}-create' type='button' value='Create' />
            <input id='tempo-{uuid}-clear' type='button' value='Clear' />
        </div>
        <div id='tempo-{uuid}-container' class='tempo-container'>
            <input type='hidden' value='{value}' {attrs} />
        </div>
        <script id='tempo-{uuid}'>(function($){{
            var input = $('#tempo-{uuid}-container').children('input'),
                value = input.val(),
                createButton = $('#tempo-{uuid}-create'),
                clearButton = $('#tempo-{uuid}-clear');

            function create() {{
                input.tempo(['or', []]);
                switchControls();
            }}

            function clear() {{
                input.tempo('destroy');
                switchControls();
            }}

            function switchControls() {{
                if (input.val()) {{
                    createButton.hide();
                    clearButton.show();
                }} else {{
                    createButton.show();
                    clearButton.hide();
                }}
            }}
            createButton.click(create);
            clearButton.click(clear);
            input.change(switchControls);
            if (value) {{
                input.tempo(value);
            }}
            switchControls();
        }})(django.jQuery)</script>
        """.format(uuid=str(uuid.uuid4()), attrs=flatatt(final_attrs),
                   value=value)

    def value_from_datadict(self, data, files, name):
        """Retrieves data, from HTML representation."""
        # pylint: disable=no-self-use,unused-argument
        value = data.get(name)
        if value is None or value == '':
            return None

        return value

    class Media:
        css = {
            'all': ('tempo/tempo.css',)
        }
        js = ('tempo/tempo.js',)
