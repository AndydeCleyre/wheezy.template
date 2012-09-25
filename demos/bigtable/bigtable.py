
"""
"""

import sys

try:
    from wheezy.html.utils import escape_html as escape
except ImportError:
    import cgi
    escape = cgi.escape

PY3 = sys.version_info[0] >= 3
s = PY3 and str or unicode

ctx = {
    'table': [dict(a=1,b=2,c=3,d=4,e=5,f=6,g=7,h=8,i=9,j=10)
          for x in range(1000)]
}


# region: python list append

if PY3:
    def test_list_append():
        b = []; w = b.append
        table = ctx['table']
        w('<table>\n')
        for row in table:
            w('<tr>\n')
            for key, value in row.items():
                w('<td>')
                w(escape(key))
                w('</td><td>')
                w(str(value))
                w('</td>\n')
            w('</tr>\n')
        w('</table>')
        return ''.join(b)
else:
    def test_list_append():
        b = []; w = b.append
        table = ctx['table']
        w(u'<table>\n')
        for row in table:
            w(u'<tr>\n')
            for key, value in row.items():
                w(u'<td>')
                w(escape(key))
                w(u'</td><td>')
                w(unicode(value))
                w(u'</td>\n')
            w(u'</tr>\n')
        w(u'</table>')
        return ''.join(b)


# region: python list extend

if PY3:
    def test_list_extend():
        b = []; e = b.extend
        table = ctx['table']
        e(('<table>\n',))
        for row in table:
            e(('<tr>\n',))
            for key, value in row.items():
                e(('<td>',
                   escape(key),
                   '</td><td>',
                   str(value),
                   '</td>\n'))
            e(('</tr>\n',))
        e(('</table>',))
        return ''.join(b)
else:
    def test_list_extend():
        b = []; e = b.extend
        table = ctx['table']
        e((u'<table>\n',))
        for row in table:
            e((u'<tr>\n',))
            for key, value in row.items():
                e((u'<td>',
                   escape(key),
                   u'</td><td>',
                   unicode(value),
                   u'</td>\n'))
            e((u'</tr>\n',))
        e((u'</table>',))
        return ''.join(b)


# region: wheezy.template

try:
    from wheezy.template.engine import Engine
    from wheezy.template.loader import DictLoader
    from wheezy.template.ext.core import CoreExtension
except ImportError:
    test_wheezy_template = None
else:
    engine = Engine(loader=DictLoader({'x': s("""\
@require(table)
<table>
    @for row in table:
    <tr>
        @for key, value in row.items():
        <td>@key!h</td><td>@value!s</td>
        @end
    </tr>
    @end
</table>
""")}), extensions=[CoreExtension()])
    engine.global_vars.update({'h': escape})
    wheezy_template = engine.get_template('x')

    def test_wheezy_template():
        return wheezy_template.render(ctx)


# region: Jinja2

try:
    from jinja2 import Environment
except ImportError:
    test_jinja2 = None
else:
    jinja2_template = Environment().from_string(s("""\
<table>
    {% for row in table: %}
    <tr>
        {% for key, value in row.items(): %}
        <td>{{ key | e }}</td><td>{{ value }}</td>
        {% endfor %}
    </tr>
    {% endfor %}
</table>
"""))
    def test_jinja2():
        return jinja2_template.render(ctx)


# region: tornado

try:
    from tornado.template import Template
except ImportError:
    test_tornado = None
else:
    tornado_template = Template(s("""\
<table>
    {% for row in table %}
    <tr>
        {% for key, value in row.items() %}
        <td>{{ key }}</td><td>{{ value }}</td>
        {% end %}
    </tr>
    {% end %}
</table>
"""))
    def test_tornado():
        return tornado_template.generate(**ctx).decode('utf8')


# region: mako

try:
    from mako.template import Template
except ImportError:
    test_mako = None
else:
    mako_template = Template(s("""\
<table>
    % for row in table:
    <tr>
        % for key, value in row.items():
        <td>${ key | h }</td><td>${ value }</td>
        % endfor
    </tr>
    % endfor
</table>
"""))
    def test_mako():
        return mako_template.render(**ctx)


# region: tenjin

try:
    import tenjin
except ImportError:
    test_tenjin = None
else:
    try:
        import webext
        helpers = {
            'to_str': s,
            'escape': webext.escape_html
        }
    except ImportError:
        helpers = {
            'to_str': tenjin.helpers.to_str,
            'escape': tenjin.helpers.escape
        }
    tenjin_template = tenjin.Template()
    tenjin_template.convert(s("""\
<table>
    <?py for row in table: ?>
    <tr>
        <?py for key, value in row.items(): ?>
        <td>${ key }</td><td>#{ value }</td>
        <?py #end ?>
    </tr>
    <?py #end ?>
</table>
"""))
    def test_tenjin():
        return tenjin_template.render(ctx, helpers)


def run(number=100):
    from timeit import Timer
    names = globals().keys()
    names = sorted([(name, globals()[name])
             for name in names if name.startswith('test_')])
    for name, test in names:
        if test:
            assert isinstance(test(), s)
            t = Timer(setup='from __main__ import %s as t' % name,
                      stmt='t()')
            t = t.timeit(number=number)
            print('%-30s %.2fms  %.2frps' % (name[5:],
                                            1000 * t / number,
                                            number / t))
        else:
            print('%-30s not installed' % name[5:])


if __name__ == '__main__':
    run()