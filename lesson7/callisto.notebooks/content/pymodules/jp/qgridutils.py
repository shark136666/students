import pandas as pd


def clear(grid):
    grid.df = pd.DataFrame()


_disable_multiselection_events = ['selection_changed']


def _disable_multiselection_impl(event, qgrid):
    if event['name'] == 'selection_changed':
        selected = event['new']
        if len(selected) > 1:
            old = event['old']
            selected = [[x for x in selected if x not in old][-1]]
            qgrid.change_selection(
                rows=[qgrid.get_changed_df().index[selected[0]]])


def disable_multiselection(qgrid):
    qgrid.on(_disable_multiselection_events, _disable_multiselection_impl)


# def enable_multiselection(qgrid):
#     not work
#     qgrid.off(_disable_multiselection_events, _disable_multiselection_impl)


_keep_selection_when_sorting_events = ['selection_changed', 'sort_changed']


def _keep_selection_when_sorting_impl(event, qgrid):
    if event['name'] == 'selection_changed':
        selected = event['new']
        df = qgrid.get_changed_df()
        qgrid._cached_selection = [df.index[s] for s in selected]
    elif event['name'] == 'sort_changed':
        if hasattr(qgrid, '_cached_selection'):
            qgrid.change_selection(rows=qgrid._cached_selection)


def keep_selection_when_sorting(qgrid):
    qgrid.on(_keep_selection_when_sorting_events,
             _keep_selection_when_sorting_impl)
