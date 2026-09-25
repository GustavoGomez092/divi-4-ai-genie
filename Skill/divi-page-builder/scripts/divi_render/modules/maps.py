"""Map modules: Map, Fullwidth Map and Map Pin (templates from Map.php, FullwidthMap.php and
MapItem.php render()).

Divi prints the map as an empty `.et_pb_map` element whose data attributes (centre, zoom,
controls, grayscale) and child `.et_pb_map_pin` elements are read by its front-end JS, which
draws the Google map with the site's API key. The preview reproduces that markup and the CSS;
without a key and network the canvas itself stays empty, as it does on a site with no key.
The map's CSS filters (`child_filter_*`, `generate_css_filters()`) are not ported.
"""
from __future__ import annotations

from ..base import Module, base_classes, register
from ..values import esc, module_content, property_values


def css_decimal(v: str) -> str:
    """et_()->to_css_decimal(): a decimal comma becomes a point."""
    return v.replace(",", ".")


@register("et_pb_map")
class Map(Module):
    slug = "et_pb_map"
    responsive_grayscale = True   # FullwidthMap.php prints only the desktop amount

    def grayscale_attrs(self) -> str:
        p = self.props
        if p.get("use_grayscale_filter", "") != "on":
            return ""
        if not self.responsive_grayscale:
            v = p.get("grayscale_filter_amount", "")
            return f' data-grayscale="{esc(v)}"' if v != "" else ""
        vals = property_values(p, "grayscale_filter_amount")
        return "".join(f' data-grayscale{"" if d == "desktop" else "-" + d}="{esc(vals[d])}"'
                       for d in ("desktop", "tablet", "phone") if vals[d] != "")

    def render(self):
        p = self.props
        p.get("address")   # the builder geocodes it into address_lat/lng; the front end never prints it
        pins = self.content_html()
        self.process_additional()
        base_classes(self)
        self.add_class("et_pb_map_container")
        self.classes = [c for c in self.classes if c != self.render_slug]
        try:
            zoom = int(float(p.get("zoom_level", "") or 0))
        except ValueError:
            zoom = 0
        mid = f' id="{esc(p.get("module_id"))}"' if p.get("module_id", "") else ""
        return (f'<div{mid} class="{self.classname()}"{self.grayscale_attrs()}>\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t'
                f'{self.mask_markup}\n\t\t\t\t<div class="et_pb_map" data-center-lat="{esc(css_decimal(p.get("address_lat", "")))}" '
                f'data-center-lng="{esc(css_decimal(p.get("address_lng", "")))}" data-zoom="{zoom}" '
                f'data-mouse-wheel="{esc(p.get("mouse_wheel", ""))}" data-mobile-dragging="{esc(p.get("mobile_dragging", ""))}">'
                f'</div>\n\t\t\t\t{pins}\n\t\t\t</div>')


@register("et_pb_fullwidth_map")
class FullwidthMap(Map):
    slug = "et_pb_fullwidth_map"
    responsive_grayscale = False


@register("et_pb_map_pin")
class MapPin(Module):
    """MapItem.php: no module wrapper or order class in the markup; the title is an h3 and the
    content an .infowindow (printed when either exists)."""
    slug = "et_pb_map_pin"

    def render(self):
        p = self.props
        p.get("pin_address")   # geocoded into pin_address_lat/lng by the builder
        title = p.get("title", "")
        content = module_content(self.node)
        strip = {"&#8221;": "", "&#8243;": ""}
        lat, lng = p.get("pin_address_lat", ""), p.get("pin_address_lng", "")
        for k, v in strip.items():
            lat, lng = lat.replace(k, v), lng.replace(k, v)
        h3 = f'<h3 style="margin-top:10px">{title}</h3>' if title else ""
        info = f'<div class="infowindow">{content}</div>' if title or content else ""
        return (f'<div class="et_pb_map_pin" data-lat="{esc(css_decimal(lat))}" data-lng="{esc(css_decimal(lng))}" '
                f'data-title="{esc(title)}">\n\t\t\t\t{h3}\n\t\t\t\t{info}\n\t\t\t</div>')
