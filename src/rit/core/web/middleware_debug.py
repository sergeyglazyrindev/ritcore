import re
import sys
from jinja2 import Template
import traceback
import pytz

import pprint
import six
from datetime import datetime

from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText

from wheezy.http.response import not_found, internal_error
from rit.app.conf import settings

utc = pytz.utc

HIDDEN_SETTINGS = re.compile('API|TOKEN|KEY|SECRET|PASS|SIGNATURE|DATABASES', re.IGNORECASE)

CLEANSED_SUBSTITUTE = '********************'


def mail_admins(subject, message):
    emails = settings.DEBUG_EMAILS
    msg = MIMEText(message, 'plain')
    msg['Subject'] = subject
    if len(emails) > 1:
        msg['Cc'] = emails[1:]
    try:
        conn = SMTP(settings.EMAIL_HOST)
        conn.set_debuglevel(True)
        conn.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        try:
            conn.sendmail(settings.DEFAULT_EMAIL_FROM, emails[0], msg.as_string())
        finally:
            conn.close()
    except Exception as exc:
        # logger.error("ERROR!!!")
        # logger.critical(exc)
        sys.exit("Mail failed: {}".format(exc))


def debug_middleware(request, following):
    assert following is not None
    try:
        response = following(request)
        if response is None:
            # generate 404 http error response
            response = technical_404_response(request)
    except (KeyboardInterrupt, SystemExit, MemoryError):
        raise
    except Exception:
        exc_info = sys.exc_info()
        if not settings.DEBUG:
            raise
        response = technical_500_response(request, *exc_info)
    return response


def rit_http_error_middleware_factory(options):
    """ Interval HTTP  Server error error middleware factory.
    """
    return debug_middleware


def technical_404_response(request):
    "Create a technical 404 error response. The exception should be the Http404."
    route_path = request.environ['REQUEST_URI']

    t = Template(TECHNICAL_404_TEMPLATE)
    c = {
        'route_path': route_path,
        'request': request,
        'settings': get_safe_settings(),
    }
    response = not_found()
    response.write(t.render(**c))
    return response


class CallableSettingWrapper(object):
    """ Object to wrap callable appearing in settings
    * Not to call in the debug page (#21345).
    * Not to break the debug page if the callable forbidding to set attributes (#23070).
    """
    def __init__(self, callable_setting):
        self._wrapped = callable_setting

    def __repr__(self):
        return repr(self._wrapped)


def cleanse_setting(key, value):
    """Cleanse an individual setting key/value of sensitive content.
    If the value is a dictionary, recursively cleanse the keys in
    that dictionary.
    """
    try:
        if HIDDEN_SETTINGS.search(key):
            cleansed = CLEANSED_SUBSTITUTE
        else:
            if isinstance(value, dict):
                cleansed = {k: cleanse_setting(k, v) for k, v in value.items()}
            else:
                cleansed = value
    except TypeError:
        # If the key isn't regex-able, just return as-is.
        cleansed = value

    if callable(cleansed):
        # For fixing #21345 and #23070
        cleansed = CallableSettingWrapper(cleansed)

    return cleansed


def get_safe_settings():
    "Returns a dictionary of the settings module, with sensitive settings blurred out."
    settings_dict = {}
    for k in settings.loaded_settings.keys():
        if k.isupper():
            settings_dict[k] = cleanse_setting(k, getattr(settings, k))
    return settings_dict


def technical_500_response(request, exc_type, exc_value, tb, status_code=500):
    """
    Create a technical server error response. The last three arguments are
    the values returned from sys.exc_info() and friends.
    """
    reporter = ExceptionReporter(request, exc_type, exc_value, tb)
    html = reporter.get_traceback_html()
    response = internal_error()
    if settings.DEBUG:
        response.write(html)
    else:
        mail_admins('INTERNAL SERVER ERROR', html)
    return response


class ExceptionReporterFilter(object):
    """
    Base for all exception reporter filter classes. All overridable hooks
    contain lenient default behaviors.
    """

    def get_post_parameters(self, request):
        if request is None:
            return {}
        else:
            return request.query if request.method == "GET" else request.form

    def get_traceback_frame_variables(self, request, tb_frame):
        return list(tb_frame.f_locals.items())


class ExceptionReporter(object):
    """
    A class to organize and coordinate reporting on exceptions.
    """
    def __init__(self, request, exc_type, exc_value, tb):
        self.request = request
        self.request.path = request.environ.get('SCRIPT_NAME', '') + request.environ.get('PATH_INFO', '')
        self.filter = ExceptionReporterFilter()
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.tb = tb
        self.is_email = not settings.DEBUG

        self.template_info = None
        self.template_does_not_exist = False
        self.postmortem = None
        # Handle deprecated string exceptions
        if isinstance(self.exc_type, six.string_types):
            self.exc_value = Exception('Deprecated String Exception: %r' % self.exc_type)
            self.exc_type = type(self.exc_value)

    def get_traceback_data(self):
        """Return a dictionary containing traceback information.
        """
        frames = self.get_traceback_frames()
        for i, frame in enumerate(frames):
            if 'vars' in frame:
                frame_vars = []
                for k, v in frame['vars']:
                    v = pprint.pprint(v)
                    if not v:
                        continue
                    # The force_escape filter assume unicode, make sure that works
                    if isinstance(v, six.binary_type):
                        v = v.decode('utf-8', 'replace')  # don't choke on non-utf-8 input
                    # Trim large blobs of data
                    if len(v) > 4096:
                        v = '%s... <trimmed %d bytes string>' % (v[0:4096], len(v))
                    frame_vars.append((k, v))
                frame['vars'] = frame_vars
            frames[i] = frame

        unicode_hint = ''
        if self.exc_type and issubclass(self.exc_type, UnicodeError):
            start = getattr(self.exc_value, 'start', None)
            end = getattr(self.exc_value, 'end', None)
            if start is not None and end is not None:
                unicode_str = self.exc_value.args[1]
                unicode_hint = unicode_str[max(start - 5, 0):min(end + 5, len(unicode_str))]

        c = {
            'is_email': self.is_email,
            'unicode_hint': unicode_hint,
            'frames': frames,
            'request': self.request,
            'filtered_POST': self.filter.get_post_parameters(self.request),
            'settings': get_safe_settings(),
            'sys_executable': sys.executable,
            'sys_version_info': '%d.%d.%d' % sys.version_info[0:3],
            'server_time': now().strftime('%Y-%m-%d %M:%S'),
            'sys_path': sys.path,
        }
        # Check whether exception info is available
        if self.exc_type:
            c['exception_type'] = self.exc_type.__name__
        if self.exc_value:
            c['exception_value'] = self.exc_value
        if frames:
            c['lastframe'] = frames[-1]
        return c

    def get_traceback_html(self):
        "Return HTML version of debug 500 HTTP error page."
        t = Template(TECHNICAL_500_TEXT_TEMPLATE if self.is_email else TECHNICAL_500_HTML_TEMPLATE)
        context = self.get_traceback_data()
        return t.render(**context)

    def _get_lines_from_file(self, filename, lineno, context_lines):
        """
        Returns context_lines before and after lineno from file.
        Returns (pre_context_lineno, pre_context, context_line, post_context).
        """
        try:
            with open(filename, 'rb') as fp:
                source = fp.read().splitlines()
        except (OSError, IOError):
            return None, [], None, []

        lower_bound = max(0, lineno - context_lines)
        upper_bound = lineno + context_lines

        pre_context = source[lower_bound:lineno]
        context_line = source[lineno]
        post_context = source[lineno + 1:upper_bound]

        return lower_bound, pre_context, context_line, post_context

    def get_traceback_frames(self):
        def explicit_or_implicit_cause(exc_value):
            explicit = getattr(exc_value, '__cause__', None)
            implicit = getattr(exc_value, '__context__', None)
            return explicit or implicit

        # Get the exception and all its causes
        exceptions = []
        exc_value = self.exc_value
        while exc_value:
            exceptions.append(exc_value)
            exc_value = explicit_or_implicit_cause(exc_value)

        frames = []
        # No exceptions were supplied to ExceptionReporter
        if not exceptions:
            return frames

        # In case there's just one exception (always in Python 2,
        # sometimes in Python 3), take the traceback from self.tb (Python 2
        # doesn't have a __traceback__ attribute on Exception)
        exc_value = exceptions.pop()
        tb = self.tb if not exceptions else exc_value.__traceback__

        while tb is not None:
            # Support for __traceback_hide__ which is used by a few libraries
            # to hide internal frames.
            if tb.tb_frame.f_locals.get('__traceback_hide__'):
                tb = tb.tb_next
                continue
            filename = tb.tb_frame.f_code.co_filename
            function = tb.tb_frame.f_code.co_name
            lineno = tb.tb_lineno - 1
            pre_context_lineno, pre_context, context_line, post_context = self._get_lines_from_file(
                filename, lineno, 7
            )
            if pre_context_lineno is not None:
                frames.append({
                    'exc_cause': explicit_or_implicit_cause(exc_value),
                    'exc_cause_explicit': getattr(exc_value, '__cause__', True),
                    'tb': tb,
                    'filename': filename,
                    'function': function,
                    'lineno': lineno + 1,
                    'vars': self.filter.get_traceback_frame_variables(self.request, tb.tb_frame),
                    'id': id(tb),
                    'pre_context': pre_context,
                    'context_line': context_line,
                    'post_context': post_context,
                    'pre_context_lineno': pre_context_lineno + 1,
                })

            # If the traceback for current exception is consumed, try the
            # other exception.
            if not tb.tb_next and exceptions:
                exc_value = exceptions.pop()
                tb = exc_value.__traceback__
            else:
                tb = tb.tb_next

        return frames

    def format_exception(self):
        """Return the same data as from traceback.format_exception."""
        frames = self.get_traceback_frames()
        tb = [(f['filename'], f['lineno'], f['function'], f['context_line']) for f in frames]
        list = ['Traceback (most recent call last):\n']
        list += traceback.format_list(tb)
        list += traceback.format_exception_only(self.exc_type, self.exc_value)
        return list


class SafeExceptionReporterFilter(ExceptionReporterFilter):
    """
    Use annotations made by the sensitive_post_parameters and
    sensitive_variables decorators to filter out sensitive information.
    """

    def is_active(self, request):
        """
        This filter is to add safety in production environments. If DEBUG is True then your site is not safe anyway.
        This hook is provided as a convenience to easily activate or
        deactivate the filter on a per request basis.
        """
        return settings.DEBUG is False

    def get_cleansed_multivaluedict(self, request, payload):
        """
        Replaces the keys in a MultiValueDict marked as sensitive with stars.
        This mitigates leaking sensitive POST parameters if something like
        request.POST['nonexistent_key'] throws an exception (#21098).
        """
        sensitive_post_parameters = getattr(request, 'sensitive_post_parameters', [])
        if self.is_active(request) and sensitive_post_parameters:
            payload = payload.copy()
            for param in sensitive_post_parameters:
                if param in payload:
                    payload[param] = CLEANSED_SUBSTITUTE
        return payload

    def get_post_parameters(self, request):
        """
        Replaces the values of POST parameters marked as sensitive with
        stars (*********).
        """
        if request is None:
            return {}
        sensitive_post_parameters = getattr(request, 'sensitive_post_parameters', [])
        request_data = request.query if request.method == "GET" else request.form
        if self.is_active(request) and sensitive_post_parameters:
            cleansed = request_data.copy()
            if sensitive_post_parameters == '__ALL__':
                # Cleanse all parameters.
                for k, v in cleansed.items():
                    cleansed[k] = CLEANSED_SUBSTITUTE
                return cleansed
            else:
                # Cleanse only the specified parameters.
                for param in sensitive_post_parameters:
                    if param in cleansed:
                        cleansed[param] = CLEANSED_SUBSTITUTE
                    return cleansed
        else:
            return request_data

    def get_traceback_frame_variables(self, request, tb_frame):
        """
        Replaces the values of variables marked as sensitive with
        stars (*********).
        """
        # Loop through the frame's callers to see if the sensitive_variables
        # decorator was used.
        current_frame = tb_frame.f_back
        sensitive_variables = None
        while current_frame is not None:
            if (
                    current_frame.f_code.co_name == 'sensitive_variables_wrapper'
                    and 'sensitive_variables_wrapper' in current_frame.f_locals
            ):
                # The sensitive_variables decorator was used, so we take note
                # of the sensitive variables' names.
                wrapper = current_frame.f_locals['sensitive_variables_wrapper']
                sensitive_variables = getattr(wrapper, 'sensitive_variables', None)
                break
            current_frame = current_frame.f_back

        cleansed = {}
        if self.is_active(request) and sensitive_variables:
            if sensitive_variables == '__ALL__':
                # Cleanse all variables
                for name, value in tb_frame.f_locals.items():
                    cleansed[name] = CLEANSED_SUBSTITUTE
            else:
                # Cleanse specified variables
                for name, value in tb_frame.f_locals.items():
                    if name in sensitive_variables:
                        value = CLEANSED_SUBSTITUTE
                    cleansed[name] = value

        if (
                tb_frame.f_code.co_name == 'sensitive_variables_wrapper'
                and 'sensitive_variables_wrapper' in tb_frame.f_locals
        ):
            # For good measure, obfuscate the decorated function's
            # arguments in
            # the sensitive_variables decorator's frame,
            # in case the variables
            # associated with those arguments
            # were meant to be obfuscated from
            # # the decorated function's
            # frame.
            cleansed['func_args'] = CLEANSED_SUBSTITUTE
            cleansed['func_kwargs'] = CLEANSED_SUBSTITUTE
        return cleansed.items()


def now():
    """
    Returns an aware or naive datetime.datetime, depending on settings.USE_TZ.
    """
    if settings.USE_TZ:
        # timeit shows that datetime.now(tz=utc) is
        # 24% slower
        return datetime.utcnow().replace(tzinfo=utc)
    else:
        return datetime.now()

TECHNICAL_500_HTML_TEMPLATE = ("""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <meta name="robots" content="NONE,NOARCHIVE">
    <title>
        {% if exception_type %}{{ exception_type }}{% else %}Report{% endif %}
        {% if request %} at {{ request.path|escape }}{% endif %}
    </title>
    <style type="text/css">
      html * { padding:0; margin:0; }
      body * { padding:10px 20px; }
      body * * { padding:0; }
      body { font:small sans-serif; }
      body>div { border-bottom:1px solid #ddd; }
      h1 { font-weight:normal; }
      h2 { margin-bottom:.8em; }
      h2 span { font-size:80%; color:#666; font-weight:normal; }
      h3 { margin:1em 0 .5em 0; }
      h4 { margin:0 0 .5em 0; font-weight: normal; }
      code, pre { font-size: 100%; white-space: pre-wrap; }
      table { border:1px solid #ccc; border-collapse: collapse; width:100%; background:white; }
      tbody td, tbody th { vertical-align:top; padding:2px 3px; }
      thead th {
        padding:1px 6px 1px 3px; background:#fefefe; text-align:left;
        font-weight:normal; font-size:11px; border:1px solid #ddd;
      }
      tbody th { width:12em; text-align:right; color:#666; padding-right:.5em; }
      table.vars { margin:5px 0 2px 40px; }
      table.vars td, table.req td { font-family:monospace; }
      table td.code { width:100%; }
      table td.code pre { overflow:hidden; }
      table.source th { color:#666; }
      table.source td { font-family:monospace; white-space:pre; border-bottom:1px solid #eee; }
      ul.traceback { list-style-type:none; color: #222; }
      ul.traceback li.frame { padding-bottom:1em; color:#666; }
      ul.traceback li.user { background-color:#e0e0e0; color:#000 }
      div.context { padding:10px 0; overflow:hidden; }
      div.context ol { padding-left:30px; margin:0 10px; list-style-position: inside; }
      div.context ol li { font-family:monospace; white-space:pre; color:#777; cursor:pointer; padding-left: 2px; }
      div.context ol li pre { display:inline; }
      div.context ol.context-line li { color:#505050; background-color:#dfdfdf; padding: 3px 2px; }
      div.context ol.context-line li span { position:absolute; right:32px; }
      .user div.context ol.context-line li { background-color:#bbb; color:#000; }
      .user div.context ol li { color:#666; }
      div.commands { margin-left: 40px; }
      div.commands a { color:#555; text-decoration:none; }
      .user div.commands a { color: black; }
      #summary { background: #ffc; }
      #summary h2 { font-weight: normal; color: #666; }
      #explanation { background:#eee; }
      #template, #template-not-exist { background:#f6f6f6; }
      #template-not-exist ul { margin: 0 0 10px 20px; }
      #template-not-exist .postmortem-section { margin-bottom: 3px; }
      #unicode-hint { background:#eee; }
      #traceback { background:#eee; }
      #requestinfo { background:#f6f6f6; padding-left:120px; }
      #summary table { border:none; background:transparent; }
      #requestinfo h2, #requestinfo h3 { position:relative; margin-left:-100px; }
      #requestinfo h3 { margin-bottom:-1em; }
      .error { background: #ffc; }
      .specific { color:#cc3300; font-weight:bold; }
      h2 span.commands { font-size:.7em;}
      span.commands a:link {color:#5E5694;}
      pre.exception_value { font-family: sans-serif; color: #666; font-size: 1.5em; margin: 10px 0 10px 0; }
      .append-bottom { margin-bottom: 10px; }
  </style>
      {% if not is_email %}
          <script type="text/javascript">
              //<!--
              function getElementsByClassName(oElm, strTagName, strClassName){
                  // Written by Jonathan Snook, http://www.snook.ca/jon; Add-ons by Robert Nyman, http://www.robertnyman.com
                  var arrElements = (strTagName == "*" && document.all)? document.all :
                  oElm.getElementsByTagName(strTagName);
                  var arrReturnElements = new Array();
                  strClassName = strClassName.replace(/\-/g, "\\-");
                  var oRegExp = new RegExp("(^|\\s)" + strClassName + "(\\s|$)");
                  var oElement;
                  for(var i=0; i<arrElements.length; i++){
                      oElement = arrElements[i];
                      if(oRegExp.test(oElement.className)){
                          arrReturnElements.push(oElement);
                      }
                  }
                  return (arrReturnElements)
              }
              function hideAll(elems) {
                  for (var e = 0; e < elems.length; e++) {
                      elems[e].style.display = 'none';
                  }
              }
              window.onload = function() {
                  hideAll(getElementsByClassName(document, 'table', 'vars'));
                  hideAll(getElementsByClassName(document, 'ol', 'pre-context'));
                  hideAll(getElementsByClassName(document, 'ol', 'post-context'));
                  hideAll(getElementsByClassName(document, 'div', 'pastebin'));
              }
              function toggle() {
                  for (var i = 0; i < arguments.length; i++) {
                      var e = document.getElementById(arguments[i]);
                      if (e) {
                          e.style.display = e.style.display == 'none' ? 'block': 'none';
                      }
                  }
                  return false;
              }
              function varToggle(link, id) {
                  toggle('v' + id);
                  var s = link.getElementsByTagName('span')[0];
                  var uarr = String.fromCharCode(0x25b6);
                  var darr = String.fromCharCode(0x25bc);
                  s.innerHTML = s.innerHTML == uarr ? darr : uarr;
                  return false;
              }
              function switchPastebinFriendly(link) {
                  s1 = "Switch to copy-and-paste view";
                  s2 = "Switch back to interactive view";
                  link.innerHTML = link.innerHTML.trim() == s1 ? s2: s1;
                  toggle('browserTraceback', 'pastebinTraceback');
                  return false;
              }
              //-->
          </script>
      {% endif %}
  </head>
<body>
<div id="summary">
  <h1>
    {% if exception_type %}{{ exception_type }}{% else %}Report{% endif %}
    {% if request %} at {{ request.path|escape }}{% endif %}
  </h1>
  <pre class="exception_value">
    {% if exception_value %}{{ exception_value|escape }}{% else %}No exception message supplied{% endif %}
  </pre>
  <table class="meta">
    {% if request %}
      <tr>
        <th>Request Method:</th>
        <td>{{ request.method }}</td>
      </tr>
      <tr>
        <th>Request URL:</th>
        <td>{{ request.path|escape }}{{ request.query }}</td>
      </tr>
    {% endif %}
    {% if exception_type %}
      <tr>
        <th>Exception Type:</th>
        <td>{{ exception_type }}</td>
      </tr>
    {% endif %}
    {% if exception_type and exception_value %}
    <tr>
      <th>Exception Value:</th>
      <td><pre>{{ exception_value|escape }}</pre></td>
    </tr>
    {% endif %}
    {% if lastframe %}
    <tr>
      <th>Exception Location:</th>
      <td>{{ lastframe.filename|escape }} in {{ lastframe.function|escape }}, line {{ lastframe.lineno }}</td>
    </tr>
    {% endif %}
    <tr>
      <th>Python Executable:</th>
      <td>{{ sys_executable|escape }}</td>
    </tr>
    <tr>
      <th>Python Version:</th>
      <td>{{ sys_version_info }}</td>
    </tr>
    <tr>
      <th>Python Path:</th>
      <td><pre>{{ sys_path }}</pre></td>
    </tr>
    <tr>
      <th>Server time:</th>
      <td>{{server_time}}</td>
    </tr>
  </table>
</div>
{% if unicode_hint %}
  <div id="unicode-hint">
      <h2>Unicode error hint</h2>
      <p>The string that could not be encoded/decoded was: <strong>{{ unicode_hint|escape }}</strong></p>
  </div>
{% endif %}
{% if frames %}
<div id="traceback">
    <h2>Traceback</h2>
    <div id="browserTraceback">
    <ul class="traceback">
        {% for frame in frames %}
            {% if frame.exc_cause %}
                <li><h3>
                    {% if frame.exc_cause_explicit %}
                        The above exception ({{ frame.exc_cause }}) was the direct cause of the following exception:
                    {% else %}
                        During handling of the above exception ({{ frame.exc_cause }}), another exception occurred:
                    {% endif %}
                </h3></li>
            {% endif %}
            <li class="frame {{ frame.type }}">
                <code>{{ frame.filename|escape }}</code> in <code>{{ frame.function|escape }}</code>
                {% if frame.context_line %}
                <div class="context" id="c{{ frame.id }}">
                {% if frame.pre_context and not is_email %}
                <ol start="{{ frame.pre_context_lineno }}" class="pre-context" id="pre{{ frame.id }}">
                    {% for line in frame.pre_context %}
                        <li onclick="toggle('pre{{ frame.id }}', 'post{{ frame.id }}')"><pre>{{ line|escape }}</pre></li>
                    {% endfor %}
                </ol>
                {% endif %}
                <ol start="{{ frame.lineno }}" class="context-line">
                    <li onclick="toggle('pre{{ frame.id }}', 'post{{ frame.id }}')"><pre>
                        {{ frame.context_line|escape }}</pre>{% if not is_email %} <span>...</span>{% endif %}</li></ol>
                        {% if frame.post_context and not is_email  %}
                            <ol start='{{ frame.lineno }}' class="post-context" id="post{{ frame.id }}">
                                {% for line in frame.post_context %}
                                    <li onclick="toggle('pre{{ frame.id }}', 'post{{ frame.id }}')"><pre>{{ line|escape }}</pre></li>
                                {% endfor %}
                </ol>
            {% endif %}
            </div>
            {% endif %}
            {% if frame.vars %}
                <div class="commands">
                    {% if is_email %}
                        <h2>Local Vars</h2>
                    {% else %}
                        <a href="#" onclick="return varToggle(this, '{{ frame.id }}')"><span>&#x25b6;</span> Local vars</a>
                    {% endif %}
                </div>
                <table class="vars" id="v{{ frame.id }}">
                    <thead>
                        <tr>
                            <th>Variable</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for var in frame.vars %}
                            <tr>
                                <td>{{ var.0|escape }}</td>
                                <td class="code"><pre>{{ var.1 }}</pre></td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% endif %}
        </li>
        {% endfor %}
    </ul>
  </div>
</div>
{% endif %}
<div id="requestinfo">
  <h2>Request information</h2>
    {% if request %}
  <h3 id="get-info">GET</h3>
    {% if request.query %}
    <table class="req">
      <thead>
        <tr>
          <th>Variable</th>
          <th>Value</th>
        </tr>
      </thead>
      <tbody>
        {% for var in request.query.items() %}
          <tr>
            <td>{{ var.0 }}</td>
            <td class="code"><pre>{{ var.1 }}</pre></td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
    {% else %}
      <p>No GET data</p>
    {% endif %}
  <h3 id="post-info">POST</h3>
    {% if filtered_POST %}
      <table class="req">
        <thead>
          <tr>
            <th>Variable</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {% for var in filtered_POST.items() %}
            <tr>
              <td>{{ var.0 }}</td>
              <td class="code"><pre>{{ var.1 }}</pre></td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    {% else %}
      <p>No POST data</p>
    {% endif %}
  <h3 id="files-info">FILES</h3>
    {% if request.method != "GET" and request.files %}
      <table class="req">
        <thead>
          <tr>
            <th>Variable</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {% for var in request.files.items() %}
            <tr>
              <td>{{ var.0 }}</td>
              <td class="code"><pre>{{ var.1 }}</pre></td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    {% else %}
      <p>No FILES data</p>
    {% endif %}
  <h3 id="cookie-info">COOKIES</h3>
    {% if request.cookies %}
      <table class="req">
        <thead>
          <tr>
            <th>Variable</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {% for var in request.cookies.items() %}
            <tr>
              <td>{{ var.0 }}</td>
              <td class="code"><pre>{{ var.1 }}</pre></td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    {% else %}
      <p>No cookie data</p>
    {% endif %}
  <h3 id="meta-info">META</h3>
  <table class="req">
    <thead>
      <tr>
        <th>Variable</th>
        <th>Value</th>
      </tr>
    </thead>
    <tbody>
      {% for var in request.environ.items() %}
        <tr>
          <td>{{ var.0 }}</td>
          <td class="code"><pre>{{ var.1 }}</pre></td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
{% else %}
  <p>Request data not supplied</p>
{% endif %}
  <h3 id="settings-info">Settings</h3>
  <h4>Using settings module <code>{{ settings.SETTINGS_MODULE }}</code></h4>
  <table class="req">
    <thead>
      <tr>
        <th>Setting</th>
        <th>Value</th>
      </tr>
    </thead>
    <tbody>
      {% for var in settings.items() %}
        <tr>
          <td>{{ var.0 }}</td>
          <td class="code"><pre>{{ var.1 }}</pre></td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
""")

TECHNICAL_500_TEXT_TEMPLATE = ("""
{% if request %} at {{ request.path }}{% endif %}
{% if request %}
    Request Method: {{ request.method }}
    Request URL: {{ request.environ['REQUEST_URI'] }}
{% endif %}
    Python Executable: {{ sys_executable }}
    Python Version: {{ sys_version_info }}
    Python Path: {{ sys_path }}
    Server time: {{ server_time }}
Traceback:
{% for frame in frames %}
    {% if frame.exc_cause %}
    {% if frame.exc_cause_explicit %}
        The above exception ({{ frame.exc_cause }}) was the direct cause of the following exception:
    {% else %}
        During handling of the above exception ({{ frame.exc_cause }}), another exception occurred:
    {% endif %}
    {% endif %}
    File "{{ frame.filename }}" in {{ frame.function }}
    {% if frame.context_line %}  {{ frame.lineno }}. {{ frame.context_line }}{% endif %}
{% endfor %}
{% if exception_type %}Exception Type: {{ exception_type }}{% if request %} at {{ request.path }}{% endif %}
{% if exception_value %}Exception Value: {{ exception_value }}{% endif %}{% endif %}
{% if request %}Request information:
    GET:{% for k, v in request.query.items() %}
        {{ k }} = {{ v }}
    {% endfor %}
    POST:{% for k, v in filtered_POST.items() %}
        {{ k }} = {{ v }}
    {% endfor %}
    {% if request.method != "GET" %}
        FILES:{% for k, v in request.files.items() %}
            {{ k }} = {{ v }}
        {% endfor %}
    {% endif %}
    COOKIES:{% for k, v in request.cookies.items() %}
        {{ k }} = {{ v }}
    {% endfor %}
    META:{% for k, v in request.environ.items() %}
        {{ k }} = {{ v }}
    {% endfor %}
{% else %}
    Request data not supplied
{% endif %}
Settings:
    Using settings module {{ settings.SETTINGS_MODULE }}{% for k, v in settings.items()%}
        {{ k }} = {{ v }}
    {% endfor %}
""")


TECHNICAL_404_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8">
  <title>Page not found at {{ route_path }}</title>
  <meta name="robots" content="NONE,NOARCHIVE">
  <style type="text/css">
    html * { padding:0; margin:0; }
    body * { padding:10px 20px; }
    body * * { padding:0; }
    body { font:small sans-serif; background:#eee; }
    body>div { border-bottom:1px solid #ddd; }
    h1 { font-weight:normal; margin-bottom:.4em; }
    h1 span { font-size:60%; color:#666; font-weight:normal; }
    table { border:none; border-collapse: collapse; width:100%; }
    td, th { vertical-align:top; padding:2px 3px; }
    th { width:12em; text-align:right; color:#666; padding-right:.5em; }
    #info { background:#f6f6f6; }
    #info ol { margin: 0.5em 4em; }
    #info ol li { font-family: monospace; }
    #summary { background: #ffc; }
    #explanation { background:#eee; border-bottom: 0px none; }
  </style>
</head>
<body>
  <div id="summary">
    <h1>Page not found <span>(404)</span></h1>
    <table class="meta">
      <tr>
        <th>Request Method:</th>
        <td>{{ request.method }}</td>
      </tr>
    </table>
  </div>
</body>
</html>
"""
