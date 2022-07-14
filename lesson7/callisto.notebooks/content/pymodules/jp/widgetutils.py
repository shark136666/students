def show_widget(widget, show=True):
    set_widget_visible(widget, show)


def hide_widget(widget, hide=True):
    set_widget_visible(widget, not hide)


def set_widget_visible(widget, visible=True):
    widget.layout.visibility = None if visible else 'hidden'


def toggle_widget_visibility(widget):
    widget.layout.visibility = \
        'hidden' if widget.layout.visibility is None else None


def disable_widget(widget, disable=True):
    widget.disabled = disable


def enable_widget(widget, enable=True):
    widget.disabled = not enable


def clear_dropdown(dropdown):
    dropdown.options = []


def dropdown_value_changed_event(change):
    return change['type'] == 'change' and change['name'] == 'value'


def dropdown_index_changed_event(change):
    return change['type'] == 'change' and change['name'] == 'index'


def dropdown_new_value_from_event(change):
    return change['new']
