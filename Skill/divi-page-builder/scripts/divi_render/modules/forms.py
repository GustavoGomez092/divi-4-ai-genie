"""Form modules: Contact Form + Contact Field, Email Optin (Signup) + its custom fields (templates
from ContactForm.php, ContactFormItem.php and Signup.php render()).

Static markup only: nothing is submitted and no email provider is called. What real Divi prints per
request is reproduced in shape, not value: the captcha digits (rand(1, 15) per render) are fixed at
1 + 1 here and the nonce is a placeholder. The fidelity harness compares tag/class sequences and
builder CSS, never attribute values or text, so neither affects the comparison
(research/tools/fidelity.py).
"""
from __future__ import annotations

import hashlib
import json
import re

from divi_shortcode import parse

from ..base import Module, base_classes, bg_layout_classes, register, render_children, render_node
from ..values import decode_icon, esc, esc_url, hover_enabled, property_values

# ContactForm::predefined_child_modules(): the fields a form without children renders.
PREDEFINED_FIELDS = ('[et_pb_contact_field field_title="Name" field_type="input" field_id="Name" required_mark="on" '
                     'fullwidth_field="off" /][et_pb_contact_field field_title="Email Address" field_type="email" '
                     'field_id="Email" required_mark="on" fullwidth_field="off" /][et_pb_contact_field '
                     'field_title="Message" field_type="text" field_id="Message" required_mark="on" fullwidth_field="on" /]')
# Email providers whose API only takes a single name field (core/components/api/email/*.php
# `$name_field_only = true`).
NAME_FIELD_ONLY = ("aweber", "campaign_monitor", "convertkit", "getresponse")
SYMBOLS = {"letters": ("[A-Za-z\\s\\-]", "Only letters allowed."), "numbers": ("[0-9\\s\\-]", "Only numbers allowed."),
           "alphanumeric": ("[\\w\\s\\-]", "Only letters and numbers allowed.")}
BUTTON_RELS = ("bookmark", "external", "nofollow", "noreferrer", "noopener")
NONCE = "0000000000"   # wp_nonce_field() value: per session in WordPress, a placeholder here


def php_serialize(attrs: dict) -> str:
    """PHP serialize() of a string => string array (the Signup checksum, WithSpamProtection.php)."""
    def s(v):
        return f's:{len(v.encode("utf-8"))}:"{v}";'
    return f"a:{len(attrs)}:{{" + "".join(s(k) + s(v) for k, v in attrs.items()) + "}"


def strip_all_tags(text) -> str:
    """wp_strip_all_tags(): drops <script>/<style> elements with their content, then every tag,
    then trims."""
    text = re.sub(r"<(script|style)[^>]*?>.*?</\1>", "", str(text), flags=re.S | re.I)
    return re.sub(r"<[^>]*>", "", text).strip()


def sortable_options(value: str) -> list:
    """A sortable_list value ('[{"value":..,"checked":..,"dragID":..}]', brackets possibly as
    &#91;/&#93;) as a list of dicts; [] when it isn't valid JSON."""
    try:
        opts = json.loads(value.replace("&#91;", "[").replace("&#93;", "]")) if value else []
    except ValueError:
        return []
    return opts if isinstance(opts, list) else []


def field_pattern(p) -> tuple:
    """ContactFormItem::render(): the (pattern, title, maxlength) attributes of a text input."""
    try:
        mn, mx = int(float(p.get("min_length", "0") or 0)), int(float(p.get("max_length", "0") or 0))
    except ValueError:
        mn = mx = 0
    sym, title = SYMBOLS.get(p.get("allowed_symbols", ""), (".", ""))
    length, maxlen = "*", ""
    if mn and mx:
        mx, mn = max(mn, mx), min(mn, mx)
        if mx > 0:
            maxlen = f' maxlength="{mx}"'
    if mn or mx:
        length = "{" + (str(mn) if mn else "") + ("," if not mx else "") + ("0" if not mn else "") + (f",{mx}" if mx else "") + "}"
        title += f"Minimum length: {mn} characters. " if mn else ""
        title += f"Maximum length: {mx} characters." if mx else ""
    pattern = f' pattern="{esc(sym + length)}"' if (sym != "." or length != "*") else ""
    return pattern, (f' title="{esc(title)}"' if title else ""), maxlen


def conditional_attrs(p) -> str:
    if p.get("conditional_logic", "") != "on":
        return ""
    rows = sortable_options(p.get("conditional_logic_rules", ""))
    rules = [[r.get("field"), r.get("condition"), str(r.get("value", "")).strip()] for r in rows if isinstance(r, dict)]
    if not rules:
        return ""
    relation = "any" if p.get("conditional_logic_relation", "") == "off" else "all"
    return (f' data-conditional-logic="{esc(json.dumps(rules, separators=(",", ":")))}"'
            f' data-conditional-relation="{relation}"')


def insert_after_order_class(m: Module, *classes):
    """add_classname() in render(): after the classes _render() set (et_pb_module, slug, order)."""
    i = m.classes.index(m.order_class) + 1
    m.classes[i:i] = [c for c in classes if c]


def has_background(m: Module) -> bool:
    """ContactFormItem::_has_background(): only the explicit enable toggles count."""
    return any(m.props.get(f"background_enable_{k}", "") == "on"
               for k in ("color", "image", "video_mp4", "video_webm", "pattern_style", "mask_style"))


@register("et_pb_contact_form")
class ContactForm(Module):
    slug = "et_pb_contact_form"
    RADIO = '%%order_class%% .input[type="radio"]:checked'
    TRANSITIONS = {"form_field_background_color": {"background-color": '%%order_class%% .input, %%order_class%% '
                   '.input[type="checkbox"]+label i, %%order_class%% .input[type="radio"]+label i'}}

    def radio_colors(self, radio: str):
        """ContactForm/ContactFormItem render(): the field text colours also fill the checked radio."""
        for opt, state in (("form_field_text_color", ""), ("form_field_focus_text_color", ":active")):
            vals = property_values(self.props, opt)
            for dev, v in vals.items():
                if v:
                    self.css(f"{radio}{state} + label i:before", f"background-color: {v};", dev)
            if hover_enabled(self.props, opt):
                hv = self.props.get(f"{opt}__hover", "")
                self.css(f"{radio}{state}:hover + label i:before", f"background-color: {hv};")

    def render(self):
        p, ctx = self.props, self.ctx
        p.get("email"), p.get("custom_message"), p.get("success_message")   # used only when a message is sent
        content = self.content_html()   # the fields render first, as in PHP
        self.process_additional()
        self.radio_colors(self.RADIO)
        num = self.index
        # render(): the globals the fields read ($et_pb_half_width_counter, $et_pb_contact_form_num)
        ctx.half_width_counter, ctx.contact_form_num = 0, num
        if not content.strip():   # predefined fields render here, inside render()
            content = "".join(render_node(n, ctx, self) for n in parse(PREDEFINED_FIELDS).nodes if hasattr(n, "tag"))
        spam = p.get("use_spam_service", "") == "on"
        base_classes(self)
        insert_after_order_class(self, "et_pb_recaptcha_enabled" if spam else "")
        lvl = p.get("title_level", "") or "h1"
        title = f'<{lvl} class="et_pb_contact_main_title">{p.get("title")}</{lvl}>' if p.get("title", "") else ""
        captcha = ""
        if p.get("captcha", "") == "on" and not spam:
            captcha = ('\n\t\t\t<div class="et_pb_contact_right">\n\t\t\t\t<p class="clearfix">\n\t\t\t\t\t'
                       '<span class="et_pb_contact_captcha_question">1 + 1</span> = <input type="text" size="2" '
                       'class="input et_pb_contact_captcha" data-first_digit="1" data-second_digit="1" value="" '
                       f'name="et_pb_contact_captcha_{num}" data-required_mark="required" autocomplete="off">'
                       '\n\t\t\t\t</p>\n\t\t\t</div>')
        icon = p.get("button_icon", "")
        data_icon = f' data-icon="{esc(decode_icon(icon))}"' if icon and p.get("custom_button", "") == "on" else ""
        text = esc(p.get("submit_button_text", "").strip() or "Submit")
        form = (f'\n\t\t\t\t<div class="et_pb_contact">\n\t\t\t\t\t<form class="et_pb_contact_form clearfix" method="post" '
                f'action="#">\n\t\t\t\t\t\t{content}\n\t\t\t\t\t\t<input type="hidden" value="et_contact_proccess" '
                f'name="et_pb_contactform_submit_{num}"/>\n\t\t\t\t\t\t<div class="et_contact_bottom_container">'
                f'\n\t\t\t\t\t\t\t{captcha}\n\t\t\t\t\t\t\t<button type="submit" name="et_builder_submit_button" '
                f'class="et_pb_contact_submit et_pb_button"{data_icon}>{text}</button>\n\t\t\t\t\t\t</div>\n\t\t\t\t\t\t'
                f'<input type="hidden" id="_wpnonce-et-pb-contact-form-submitted-{num}" '
                f'name="_wpnonce-et-pb-contact-form-submitted-{num}" value="{NONCE}" /><input type="hidden" '
                f'name="_wp_http_referer" value="/" />\n\t\t\t\t\t</form>\n\t\t\t\t</div>')
        self.add_class("et_pb_contact_form_container", "clearfix", self.text_orientation_class().strip())
        self.classes = [c for c in self.classes if c != self.render_slug]
        module_id = p.get("module_id", "") or f"et_pb_contact_form_{num}"
        redirect = (f' data-redirect_url="{esc_url(p.get("redirect_url"))}"'
                    if p.get("use_redirect", "") == "on" and p.get("redirect_url", "") else "")
        return (f'\n\t\t\t<div id="{esc(module_id)}" class="{self.classname()}" data-form_unique_num="{num}" '
                f'data-form_unique_id="{esc(p.get("_unique_id", ""))}"{redirect}>\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t'
                f'{self.mask_markup}\n\t\t\t\t{title}\n\t\t\t\t<div class="et-pb-contact-message"></div>\n\t\t\t\t{form}'
                f'\n\t\t\t</div>\n\t\t\t')


@register("et_pb_contact_field")
class ContactField(Module):
    slug = "et_pb_contact_field"
    RADIO = '%%order_class%%.et_pb_contact_field .input[type="radio"]:checked'
    TRANSITIONS = {"form_field_background_color": {"background": "%%order_class%%.et_pb_contact_field .input, "
                                                                  "%%order_class%%.et_pb_contact_field .input + label:hover i"}}
    radio_colors = ContactForm.radio_colors

    def form_num(self) -> int:
        """$current_module_num: the global $et_pb_contact_form_num + 1 (0 before any form)."""
        n = self.ctx.contact_form_num
        return 0 if n is None else n + 1

    def render(self):
        p, ctx = self.props, self.ctx
        self.process_additional()
        if self.attrs.get("form_field_text_color", ""):
            self.generate_styles("form_field_text_color", "%%order_class%% .input + label, %%order_class%% .input + label i:before",
                                 "color", important=True)
        self.radio_colors(self.RADIO)
        for k in ("min_length", "max_length", "allowed_symbols", "checkbox_checked", "checkbox_options",
                  "radio_options", "select_options", "conditional_logic_relation", "conditional_logic_rules"):
            p.get(k)   # render() reads every field option up front, whichever ones its type uses
        count = ctx.next_index("contact_form_item")   # the shared ContactFormItem render count
        num = self.form_num()
        ftype, title = p.get("field_type", ""), p.get("field_title", "")
        fid = p.get("field_id", "") or f"field_{ctx.contact_form_num or 0}_{count}"
        signup = self.render_slug == "et_pb_signup_custom_field"
        if not signup:
            fid = fid.lower()
        if p.get("fullwidth_field", "") == "off":
            ctx.half_width_counter += 1
        else:
            ctx.half_width_counter = 0
        field = self.input_html(ftype, fid, title, num, count)
        # ContactFormItem's slug, then the render slug (et_pb_signup_custom_field) and order class;
        # et_pb_module is removed
        base_classes(self, "et_pb_contact_field")
        self.classes.remove("et_pb_module")
        self.classes.insert(self.classes.index(self.order_class), self.render_slug)
        insert_after_order_class(self, "et_pb_newsletter_field" if signup else "")
        self.add_class(self.text_orientation_class().strip())
        if p.get("fullwidth_field", "") == "off":
            self.add_class("et_pb_contact_field_half")
        if ctx.half_width_counter % 2 == 0:
            self.add_class("et_pb_contact_field_last")
        if p.get("hidden", "") == "on":
            self.add_class("et_pb_contact_field--hidden")
        if has_background(self):
            self.add_class("has-background")
        return (f'<p class="{self.classname()}"{conditional_attrs(p)} data-id="{esc(fid)}" data-type="{esc(ftype)}">'
                f'\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{self.mask_markup}\n\t\t\t\t<label for="et_pb_contact_{esc(fid)}_{num}" '
                f'class="et_pb_contact_form_label">{esc(title)}</label>\n\t\t\t\t{field}\n\t\t\t</p>')

    def input_html(self, ftype: str, fid: str, title: str, num: int, count: int) -> str:
        p = self.props
        req = "not_required" if p.get("required_mark", "") == "off" else "required"
        name = f"et_pb_contact_{esc(fid)}_{num}"
        data = f'data-required_mark="{req}" data-field_type="{esc(ftype)}" data-original_id="{esc(fid)}"'
        if ftype in ("text", "textarea"):
            return (f'<textarea name="{name}" id="{name}" class="et_pb_contact_message input" {data} '
                    f'placeholder="{esc(title)}"></textarea>')
        if ftype in ("input", "email"):
            pattern, ptitle, maxlen = field_pattern(p)
            pattern = "" if ftype == "email" else pattern
            return (f'<input type="text" id="{name}" class="input" value="" name="{name}" {data} '
                    f'placeholder="{esc(title)}"{pattern}{ptitle}{maxlen}>')
        if ftype == "checkbox":
            opts = p.get("checkbox_options", "")
            if not opts:
                opts = json.dumps([{"value": title, "checked": 1 if p.get("checkbox_checked", "") == "on" else 0}])
                title = ""
            items = ""
            for i, o in enumerate(sortable_options(opts)):
                oid = o.get("id", o.get("dragID", ""))
                value = label = strip_all_tags(o.get("value", ""))   # ContactFormItem.php: both stripped
                link = (f' <a href="{esc_url(o["link_url"])}" target="_blank">{esc(o.get("link_text", ""))}</a>'
                        if o.get("link_url") else "")
                if req == "required" and not value and link:
                    value = o.get("link_text") or o["link_url"]
                cid = f"et_pb_contact_{esc(fid)}_{count}_{i}"
                checked = ' checked="checked"' if o.get("checked") == 1 else ""
                items += (f'<span class="et_pb_contact_field_checkbox">\n\t\t\t\t\t\t\t<input type="checkbox" id="{cid}" '
                          f'class="input" value="{esc(value)}"{checked} data-id="{esc(str(oid))}">\n\t\t\t\t\t\t\t'
                          f'<label for="{cid}"><i></i>{label}{link}</label>\n\t\t\t\t\t\t</span>')
            return (f'<input class="et_pb_checkbox_handle" type="hidden" name="{name}" {data}>\n\t\t\t\t\t'
                    f'<span class="et_pb_contact_field_options_wrapper">\n\t\t\t\t\t\t<span class="et_pb_contact_field_'
                    f'options_title">{esc(title)}</span>\n\t\t\t\t\t\t<span class="et_pb_contact_field_options_list">'
                    f'{items}</span>\n\t\t\t\t\t</span>')
        if ftype == "radio":
            opts = sortable_options(p.get("radio_options", ""))
            items = "" if opts or p.get("radio_options", "") else "No options added."
            for i, o in enumerate(opts):
                rid = f"et_pb_contact_{esc(fid)}_{num}_{count}_{i}"
                value = esc(strip_all_tags(o.get("value", "")))   # value and label: esc_attr(wp_strip_all_tags())
                checked = " checked='checked'" if o.get("checked") == 1 else ""
                link = (f' <a href="{esc_url(o["link_url"])}" target="_blank">{esc(o.get("link_text", ""))}</a>'
                        if o.get("link_url") else "")
                items += (f'<span class="et_pb_contact_field_radio">\n\t\t\t\t\t\t\t\t<input type="radio" id="{rid}" '
                          f'class="input" value="{value}" name="{name}" {data} {checked} '
                          f'data-id="{esc(str(o.get("id", o.get("dragID", ""))))}">\n\t\t\t\t\t\t\t\t<label for="{rid}">'
                          f'<i></i>{value}{link}</label>\n\t\t\t\t\t\t\t</span>')
            return (f'<span class="et_pb_contact_field_options_wrapper">\n\t\t\t\t\t\t<span class="et_pb_contact_field_'
                    f'options_title">{esc(title)}</span>\n\t\t\t\t\t\t<span class="et_pb_contact_field_options_list">'
                    f'{items}</span>\n\t\t\t\t\t</span>')
        if ftype == "select":
            options = f'<option value="">{esc(title)}</option>' + "".join(
                f'<option value="{esc(strip_all_tags(o.get("value", "")))}"'
                + (f' data-id="{esc(str(o["id"]))}"' if "id" in o else "") + f'>{strip_all_tags(o.get("value", ""))}</option>'
                for o in sortable_options(p.get("select_options", "")))
            return (f'<select id="{name}" class="et_pb_contact_select input" name="{name}" {data}>\n\t\t\t\t\t\t'
                    f'{options}\n\t\t\t\t\t</select>')
        return ""   # 'none' (a custom field without a type) prints only the label


@register("et_pb_signup_custom_field")
class SignupCustomField(ContactField):
    """Rendered by ContactFormItem (its additional_shortcode_slugs) with the Signup Item's fields
    and design options (SignupItem.php, no_render)."""
    slug = "et_pb_signup_custom_field"


@register("et_pb_signup")
class Signup(Module):
    slug = "et_pb_signup"
    TRANSITIONS = {k: {"background-color": ", ".join(f"%%order_class%% .et_pb_newsletter_form p {s}" for s in (
        'input[type="text"]', "textarea", "select", '.input[type="checkbox"] + label i', '.input[type="radio"] + label i'))}
        for k in ("form_field_background_color", "form_field_focus_background_color")}

    def render(self):
        p, ctx = self.props, self.ctx
        self.process_additional()
        custom = render_children(self.node, ctx, self)   # children render first, as in PHP
        ctx.half_width_counter = 0
        spam = p.get("use_spam_service", "") == "on"
        provider = p.get("provider", "") or "mailchimp"
        if p.get("form_field_text_color", ""):
            self.css('%%order_class%% .et_pb_newsletter_form p .input[type="radio"] + label i:before',
                     f"background-color: {p.get('form_field_text_color')};")
        base_classes(self)
        insert_after_order_class(self, "et_pb_recaptcha_enabled" if spam else "",
                                 f"et_pb_newsletter_layout_{p.get('layout')}" if p.get("layout", "") else "")
        self.add_class("et_pb_newsletter", "et_pb_subscribe", "clearfix", self.text_orientation_class().strip(),
                       *bg_layout_classes(self))
        if p.get("use_background_color", "") != "on":
            self.add_class("et_pb_no_bg")
        if p.get("use_focus_border_color", "") == "on":
            self.add_class("et_pb_with_focus_border")
        if not p.get("title", ""):
            self.add_class("et_pb_newsletter_description_no_title")
        if not p.get("description", ""):
            self.add_class("et_pb_newsletter_description_no_content")
        self.classes = [c for c in self.classes if c != self.render_slug]
        attrs = ""
        if p.get("success_action", "") == "redirect" and p.get("success_redirect_url", ""):
            attrs = f' data-redirect_url="{esc_url(p.get("success_redirect_url"))}"'
        return (f'<div class="{self.classname()}"{attrs}>\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{self.mask_markup}\n\t\t\t\t'
                f'{self.description()}\n\t\t\t\t{self.form(provider, custom)}\n\t\t\t</div>')

    def description(self) -> str:
        p = self.props
        lvl = p.get("header_level", "") or "h2"
        title = f'<{lvl} class="et_pb_module_header">{p.get("title")}</{lvl}>' if p.get("title", "") else ""
        # multi_view_filter_value(): a stray leading '</p>' and trailing '<p>' are dropped
        desc = re.sub(r"<p>$", "", re.sub(r"^\w?</p>", "", p.get("description", ""), flags=re.I | re.M), flags=re.I | re.M)
        desc = f"<div>{desc}</div>" if desc else ""
        return f'<div class="et_pb_newsletter_description">{title}{desc}</div>' if title or desc else ""

    def name_field(self, key: str, label: str, prop: str, ident: str) -> str:
        """Signup::get_form_field_html() for the name and email fields."""
        full = self.props.get(prop, "on") != "off"
        vals = property_values(self.props, prop, "on", True)
        cls = (" et_pb_contact_field_last" if full else " et_pb_contact_field_half") + "".join(
            f" et_pb_contact_field_{'last' if vals[d] == 'on' else 'half'}_{d}" for d in ("tablet", "phone"))
        return (f'\n\t\t\t\t\t<p class="et_pb_newsletter_field{cls}">\n\t\t\t\t\t\t<label class="et_pb_contact_form_label" '
                f'for="et_pb_signup_{ident}" style="display: none;">{label}</label>\n\t\t\t\t\t\t<input id="et_pb_signup_'
                f'{ident}" class="input" type="text" placeholder="{label}" name="et_pb_signup_{ident}">\n\t\t\t\t\t</p>')

    def button(self) -> str:
        p = self.props
        icon = p.get("button_icon", "") if p.get("custom_button", "") == "on" else ""
        rels = [r for r, on in zip(BUTTON_RELS, p.get("button_rel", "").split("|")) if on == "on"]
        rel = f' rel="{" ".join(rels)}"' if rels else ""
        text = p.get("button_text", "")
        label = f'<span class="et_pb_newsletter_button_text">{text}</span>' if text else ""
        return (f'\n\t\t\t\t\t<p class="et_pb_newsletter_button_wrap">\n\t\t\t\t\t\t<a class="et_pb_newsletter_button '
                f'et_pb_button" href="#"{rel} data-icon="{esc(decode_icon(icon)) if icon else ""}">\n\t\t\t\t\t\t\t'
                f'<span class="et_subscribe_loader"></span>\n\t\t\t\t\t\t\t{label}\n\t\t\t\t\t\t</a>\n\t\t\t\t\t</p>')

    def form(self, provider: str, custom: str) -> str:
        """The form prints only once a list is chosen: '<account>|<list id>' from the live site's
        connected account (no provider API is called here)."""
        p = self.props
        lst = p.get(f"{provider}_list", "") if provider != "feedburner" else ""
        if provider == "feedburner":
            return ""   # FeedBurner (retired by Google) is not ported
        if lst in ("", "none"):
            return ""
        single = p.get("name_field_only" if provider in NAME_FIELD_ONLY else "name_field", "") == "on"
        first = p.get("first_name_field", "") == "on" and provider not in NAME_FIELD_ONLY
        last = p.get("last_name_field", "") == "on" and provider not in NAME_FIELD_ONLY
        name = self.name_field("name", "Name" if single else "First Name",
                               "name_fullwidth" if single else "first_name_fullwidth", "firstname") if first or single else ""
        last_html = self.name_field("last_name", "Last Name", "last_name_fullwidth", "lastname") if last and not single else ""
        email = self.name_field("email", "Email", "email_fullwidth", "email")
        use_custom = p.get("use_custom_fields", "") == "on"
        footer = p.get("footer_content", "")
        footer = f'<div class="et_pb_newsletter_footer">{footer}</div>' if footer else ""
        account, _, list_id = lst.rpartition("|")
        checksum = hashlib.md5(php_serialize(self.node.attrs).encode("utf-8")).hexdigest()
        hidden = (f'\n\t\t\t\t\t\t<input type="hidden" value="{esc(provider)}" name="et_pb_signup_provider" />\n\t\t\t\t\t\t'
                  f'<input type="hidden" value="{esc(list_id)}" name="et_pb_signup_list_id" />\n\t\t\t\t\t\t'
                  f'<input type="hidden" value="{esc(account)}" name="et_pb_signup_account_name" />\n\t\t\t\t\t\t'
                  f'<input type="hidden" value="{"true" if p.get("ip_address", "") == "on" else "false"}" '
                  f'name="et_pb_signup_ip_address" /><input type="hidden" value="{checksum}" name="et_pb_signup_checksum" />')
        return (f'\n\t\t\t\t<div class="et_pb_newsletter_form">\n\t\t\t\t\t<form method="post"'
                f'{" class=" + chr(34) + "et_pb_newsletter_custom_fields" + chr(34) if use_custom else ""}>\n\t\t\t\t\t\t'
                f'<div class="et_pb_newsletter_result et_pb_newsletter_error"></div>\n\t\t\t\t\t\t<div class="et_pb_newsletter_'
                f'result et_pb_newsletter_success">\n\t\t\t\t\t\t\t<h2>{esc(p.get("success_message", ""))}</h2>\n\t\t\t\t\t\t'
                f'</div>\n\t\t\t\t\t\t<div class="et_pb_newsletter_fields">\n\t\t\t\t\t\t\t{name}\n\t\t\t\t\t\t\t{last_html}'
                f'\n\t\t\t\t\t\t\t{email}\n\t\t\t\t\t\t\t{custom if use_custom else ""}\n\t\t\t\t\t\t\t{self.button()}'
                f'\n\t\t\t\t\t\t\t{footer}\n\t\t\t\t\t\t</div>\n\t\t\t\t\t\t{hidden}\n\t\t\t\t\t</form>\n\t\t\t\t</div>')

