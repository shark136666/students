import visa


rm = visa.ResourceManager('@py')


def identify_instrument(resource_name, open_timeout=200, throw_on_error=True):
    try:
        with rm.open_resource(resource_name, open_timeout=open_timeout) as con:
            con.write_termination = '\n'
            con.read_termination = '\n'
            con.timeout = 4000
            return con.query('*IDN?')
    except Exception:
        if throw_on_error:
            raise
        return ''


def construct_identify_dict(identify_string):
    idn = [x.strip() for x in identify_string.split(',')]

    inf = {}
    inf['producer'] = idn[0]
    inf['model'] = idn[1]
    inf['serial'] = idn[2]
    inf['version'] = idn[3]
    return inf
