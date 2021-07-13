import dash_core_components as dcc
import dash_html_components as html


def make_dropdown(label, dropdown_options, clearable=False, div_id=''):
    return html.Div([
        html.Label(label),
        dcc.Dropdown(**dropdown_options, clearable=clearable),
    ], id=div_id)


def make_slider(label, slider_options):
    return html.Div([
        html.Label([label, ': ', html.Span(id={'type': 'label', 'index': slider_options['id']['index']})]),
        dcc.Slider(**slider_options)
    ])


def create_detail_table(df):
    out = {}

    last_time = df[df.time == max(df.time)]

    out['total infected'] = calc_perc_infected(last_time)
    out['susceptible remaining'] = calc_susceptible_remaining(last_time)
    out['peak time'] = calc_peak_time(df)
    out['peak infected'] = calc_peak_infected(df)
    out['effective end'] = calc_effective_end(df)

    for k, v in out.items():
        out[k] = '%.4f' % v

    columns = [{"name": i, "id": i} for i in ['key', 'value']]
    records = [{'key': k, 'value': v} for k, v in out.items()]

    return records, columns


def calc_perc_infected(df):
    r = df[df.compartment == 'removed'].iloc[0]['value']
    e = df[df.compartment == 'exposed'].iloc[0]['value']
    return r + e


def calc_susceptible_remaining(df):
    return df[df.compartment == 'susceptible'].iloc[0]['value']


def calc_peak_time(df):
    return df.loc[df[df.compartment == 'infected'].value.idxmax(), 'time']


def calc_peak_infected(df):
    return df[df.compartment == 'infected'].value.max()


def calc_effective_end(df):
    # first time, infected is sub 1% again
    # todo what threshold makes sense here?
    infected = df[df.compartment == 'infected']

    idx = find_sub_threshold_after_peak(infected.value.tolist(), 0.01)

    if idx is None:
        return None

    return infected.time.values[idx]


def find_sub_threshold_after_peak(l: list, v: float):
    """
    Find the index of the value in a list that is below a threshold  for the
    first time after a value above the peak. If the condition is not met for
    any values, return 0 if the first value of the list is below the threshold
    or None if the first value is above the threshold.
    :param l: List of values
    :param v: Threshold value
    :return: Index or None
    """
    for i in range(1, len(l)):
        if l[i - 1] > v >= l[i]:
            return i

    return 0 if l[0] <= v else None