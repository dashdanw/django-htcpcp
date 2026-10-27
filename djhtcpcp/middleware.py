from xml.etree import ElementTree as ET

from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from . import signals, state
from .additions import parse_accept_additions
from .pots import resolve
from .rfc import (
    BREW,
    COFFEEPOT_MEDIA_TYPE,
    COFFEEPOT_MEDIA_TYPES,
    HTCPCP_MEDIA_TYPES,
    POST,
    PROPFIND,
    START,
    STOP,
    TEAPOT_MEDIA_TYPE,
    WHEN,
)

TEXT = "text/plain; charset=utf-8"
DAV_NS = "DAV:"
HTCPCP_NS = "urn:ietf:rfc:2324"


def _response(body, status, content_type=TEXT, **headers):
    response = HttpResponse(body, status=status, content_type=content_type)
    for name, value in headers.items():
        response[name.replace("_", "-")] = value
    return response


def _alternates(pot):
    entries = []
    if pot.coffee:
        entries.append(f'{{"{pot.path}" {{type {COFFEEPOT_MEDIA_TYPE}}}}}')
    entries += [f'{{"{pot.variety_path(v)}" {{type {TEAPOT_MEDIA_TYPE}}}}}' for v in pot.varieties]
    return ", ".join(entries)


def _teapot(pot=None):
    response = _response("I'm a teapot.", 418)
    if pot is not None and pot.is_teapot:
        response["Alternates"] = _alternates(pot)
    return response


class HTCPCPMiddleware(MiddlewareMixin):
    """Answer HTCPCP requests (RFC 2324) and HTCPCP-TEA requests (RFC 7168).

    Pots are configured with the ``HTCPCP_POTS`` setting. ``BREW`` and ``WHEN``
    requests to anything that is not a pot are answered with 418 I'm a teapot.
    ``PROPFIND`` is only answered for pots, and ``POST`` only when it carries an
    HTCPCP media type, so WebDAV and form handling elsewhere are unaffected.
    """

    def process_request(self, request):
        method = request.method
        if method not in (BREW, WHEN, PROPFIND, POST):
            return None
        if method == POST and request.content_type not in HTCPCP_MEDIA_TYPES:
            return None

        match = resolve(request.path)
        if method == PROPFIND:
            return self.propfind(request, *match) if match else None
        if match is None:
            return _teapot()
        if method == WHEN:
            return self.when(request, *match)
        return self.brew(request, *match)

    # BREW / POST

    def brew(self, request, pot, variety):
        wants_tea = request.content_type == TEAPOT_MEDIA_TYPE
        command = request.body.strip().decode("ascii", "replace").casefold() or START
        if command not in (START, STOP):
            return _response('The coffee-message-body must be "start" or "stop".', 400)

        if not pot.is_teapot:
            if wants_tea:
                return _response(
                    "This is a coffee pot.", 415, Accept=", ".join(COFFEEPOT_MEDIA_TYPES)
                )
            return self.brew_beverage(request, pot, None, command)

        if variety is None:
            if wants_tea:
                body = "Choose a tea:\n" + "\n".join(pot.variety_path(v) for v in pot.varieties)
                return _response(body, 300, Alternates=_alternates(pot))
            if not pot.coffee:
                return _teapot(pot)
            response = self.brew_beverage(request, pot, None, command)
            response["Alternates"] = _alternates(pot)
            return response

        if variety not in pot.varieties:
            return _response("No such tea.", 404, Alternates=_alternates(pot))
        if not wants_tea:
            return _teapot(pot)
        return self.brew_beverage(request, pot, variety, command)

    def brew_beverage(self, request, pot, variety, command):
        content_type = TEAPOT_MEDIA_TYPE if variety else COFFEEPOT_MEDIA_TYPE
        beverage = variety or "coffee"

        if command == STOP:
            brew = state.stop(pot, variety)
            if brew is None:
                return _response(f"The pot is not brewing {beverage}.", 409)
            strength = state.strength(brew.elapsed, pot.varieties[variety]) if variety else None
            signals.brew_stopped.send(
                type(self),
                request=request,
                pot=pot,
                variety=variety,
                elapsed=brew.elapsed,
                strength=strength,
            )
            body = f"Stopped brewing {beverage}."
            if strength is not None:
                body += f" Served at {strength}% strength."
            return _response(body, 200, content_type)

        additions = parse_accept_additions(request.headers.get("Accept-Additions"))
        requested = [a for a in additions if not a.is_wildcard]
        available = {name.casefold() for name in pot.additions}
        unavailable = [a.name for a in requested if a.name.casefold() not in available]
        if unavailable:
            if pot.additions:
                body = f"Cannot provide {', '.join(unavailable)}. Available additions: "
                body += ", ".join(pot.additions) + "."
            else:
                body = "This pot cannot provide additions."
            return _response(body, 406)
        forbidden = {name.casefold() for name in pot.forbidden_additions.get(variety, ())}
        blasphemy = [a.name for a in requested if a.name.casefold() in forbidden]
        if blasphemy:
            return _response(f"{', '.join(blasphemy)} in {variety}? Absolutely not.", 403)

        state.start(pot, variety, requested)
        signals.brew_started.send(
            type(self), request=request, pot=pot, variety=variety, additions=requested
        )
        body = f"Brewing {beverage}."
        if any(a.is_milk for a in requested):
            body = "Say WHEN . . . "
        return _response(body, 202, content_type, Safe="if-user-awake")

    # WHEN

    def when(self, request, pot, variety):
        if pot.is_teapot:
            if variety is None and not pot.coffee:
                return _teapot(pot)
            if variety is not None and variety not in pot.varieties:
                return _response("No such tea.", 404, Alternates=_alternates(pot))
        signals.when_said.send(type(self), request=request, pot=pot, variety=variety)
        if variety:
            return _response("Mmmmmmm tea!", 201, TEAPOT_MEDIA_TYPE)
        return _response("Mmmmmmm coffee!", 201, COFFEEPOT_MEDIA_TYPE)

    # PROPFIND

    def propfind(self, request, pot, variety):
        if variety is not None and variety not in pot.varieties:
            return None

        ET.register_namespace("D", DAV_NS)
        ET.register_namespace("C", HTCPCP_NS)
        dav = f"{{{DAV_NS}}}"
        cp = f"{{{HTCPCP_NS}}}"

        multistatus = ET.Element(f"{dav}multistatus")
        response = ET.SubElement(multistatus, f"{dav}response")
        ET.SubElement(response, f"{dav}href").text = request.path
        propstat = ET.SubElement(response, f"{dav}propstat")
        prop = ET.SubElement(propstat, f"{dav}prop")

        ET.SubElement(prop, f"{cp}pot-type").text = "teapot" if pot.is_teapot else "coffeepot"
        ET.SubElement(prop, f"{cp}coffee").text = str(pot.coffee).lower()
        if variety:
            ET.SubElement(prop, f"{cp}variety").text = variety
            ET.SubElement(prop, f"{cp}steep-seconds").text = str(pot.varieties[variety])
        elif pot.is_teapot:
            varieties = ET.SubElement(prop, f"{cp}varieties")
            for name, seconds in pot.varieties.items():
                ET.SubElement(
                    varieties,
                    f"{cp}variety",
                    href=pot.variety_path(name),
                    **{"steep-seconds": str(seconds)},
                ).text = name

        additions = ET.SubElement(prop, f"{cp}additions")
        for name in pot.additions:
            ET.SubElement(additions, f"{cp}addition").text = name

        brew = state.get(pot, variety)
        ET.SubElement(prop, f"{cp}brewing").text = str(brew is not None).lower()
        if brew is not None:
            ET.SubElement(prop, f"{cp}elapsed-seconds").text = str(round(brew.elapsed))
            for name in brew.additions:
                ET.SubElement(prop, f"{cp}brewing-addition").text = name
            if variety:
                strength = state.strength(brew.elapsed, pot.varieties[variety])
                ET.SubElement(prop, f"{cp}strength").text = str(strength)

        ET.SubElement(propstat, f"{dav}status").text = "HTTP/1.1 200 OK"
        body = ET.tostring(multistatus, encoding="utf-8", xml_declaration=True)
        return _response(body, 207, "application/xml; charset=utf-8", Safe="yes")
