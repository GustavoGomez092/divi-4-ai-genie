"""People and social modules: Testimonial, Team Member, Social Media Follow + its networks
(templates from each module's render())."""
from __future__ import annotations

from ..base import Module, base_classes, bg_layout_classes, register
from ..css import add_hover_to_order_class, add_hover_to_selectors
from ..values import DEVICES, esc, esc_url, hover_value, module_content, multiply_unit, property_values


@register("et_pb_testimonial")
class Testimonial(Module):
    slug = "et_pb_testimonial"
    QUOTE = "%%order_class%%.et_pb_testimonial:before"
    TRANSITIONS = {"portrait_width": {"width": "%%order_class%% .et_pb_testimonial_portrait"},
                   "portrait_height": {"height": "%%order_class%% .et_pb_testimonial_portrait"},
                   "quote_icon_color": {"color": QUOTE},
                   "quote_icon_background_color": {"background-color": QUOTE}}

    def render(self):
        p = self.props
        self.process_additional()
        for attr, prop in (("portrait_width", "width"), ("portrait_height", "height")):
            self.generate_styles(attr, "%%order_class%% .et_pb_testimonial_portrait", prop, important=True, typ="range",
                                 hover=False)
        self.generate_styles("quote_icon_color", self.QUOTE, "color", hover_loc="suffix")
        self.generate_styles("quote_icon_background_color", self.QUOTE, "background-color", hover_loc="suffix")
        self.icon_style("font_icon", self.QUOTE, content=True)
        quote = p.get("quote_icon", "") != "off"
        if quote and p.get("use_icon_font_size", "") != "off":
            self.overlay_icon_size("%%order_class%%:before",
                                   "font-size:{0}; border-radius:{0}; top:-{1}; margin-left:-{1};")
        portrait = p.get("portrait_url", "")
        portrait_div = (f'<div style="background-image:url({esc(portrait)})" class="et_pb_testimonial_portrait"></div>'
                        if portrait else "")
        url, target = p.get("url", ""), ' target="_blank"' if p.get("url_new_window", "") == "on" else ""

        def link(text):
            return f'<a href="{esc_url(url)}"{target}>{text}</a>' if url else text
        author, job, company = p.get("author", ""), p.get("job_title", ""), p.get("company_name", "")
        metas = []
        if job:
            metas.append(f'<span class="et_pb_testimonial_position">{job}</span>')
        if company:
            metas.append(f'<span class="et_pb_testimonial_company">{link(company)}</span>')
        author_html = (f'<span class="et_pb_testimonial_author">{author if company else link(author)}</span>'
                       if author else "")
        base_classes(self)
        self.add_class("clearfix", self.text_orientation_class(), *bg_layout_classes(self))
        if not quote:
            self.add_class("et_pb_icon_off")
        # Testimonial.php: has_value( 'portrait_url', 'desktop' ) compares the URL with the string
        # 'desktop', so real Divi adds this class even when a portrait is set.
        if portrait != "desktop":
            self.add_class("et_pb_testimonial_no_image")
        use_bg = p.get("use_background_color", "")
        if use_bg == "off":
            self.add_class("et_pb_testimonial_no_bg")
        if use_bg == "on":  # render() repeats the background colour (and its hover) on top of the generic rule
            self.css("%%order_class%%.et_pb_testimonial", f"background-color: {p.get('background_color')};")
            hbg = hover_value(p, "background_color")
            if hbg is not None and hbg != p.get("background_color"):
                self.css(add_hover_to_order_class("%%order_class%%.et_pb_testimonial"), f"background-color: {hbg};")
        content = f'<div class="et_pb_testimonial_content">{module_content(self.node)}</div>'
        sep = '<span class="et_pb_testimonial_separator">,</span> '
        return (f'<div class="{self.classname()}">\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{self.mask_markup}\n'
                f'\t\t\t\t{portrait_div}\n\t\t\t\t<div class="et_pb_testimonial_description">\n'
                f'\t\t\t\t\t<div class="et_pb_testimonial_description_inner">{content}</div>\n'
                f'\t\t\t\t\t{author_html}\n\t\t\t\t\t<p class="et_pb_testimonial_meta">{sep.join(metas)}</p>\n'
                f'\t\t\t\t</div>\n\t\t\t</div>')


TEAM_NETWORKS = (("facebook_url", "facebook", "Facebook"), ("twitter_url", "twitter", "X"),
                 ("linkedin_url", "linkedin", "LinkedIn"))


@register("et_pb_team_member")
class TeamMember(Module):
    slug = "et_pb_team_member"
    LINKS = "%%order_class%% .et_pb_member_social_links a"
    TRANSITIONS = {"icon_color": {"color": LINKS}, "icon_font_size": {"font-size": LINKS}}

    def render(self):
        p = self.props
        self.process_additional()
        self.generate_styles("icon_color", self.LINKS, "color", important=True, hover_loc="suffix")
        links = "".join(f'<li><a href="{esc_url(p.get(attr))}" class="et_pb_font_icon et_pb_{net}_icon">'
                        f'<span>{label}</span></a></li>' for attr, net, label in TEAM_NETWORKS if p.get(attr, ""))
        links = f'<ul class="et_pb_member_social_links">{links}</ul>' if links else ""
        if p.get("use_icon_font_size", "") != "off":
            self.generate_styles("icon_font_size", "%%order_class%% .et_pb_member_social_links .et_pb_font_icon",
                                 "font-size", typ="range", hover_loc="suffix")
        image = ""
        img = p.get("image_url", "")
        if img:
            cls = ["et_pb_team_member_image", "et-waypoint", f"et_pb_animation_{p.get('animation', '') or 'top'}"]
            if img.split("?")[0].lower().endswith(".svg"):
                cls.append("et-svg")
            image = (f'<div class="{" ".join(cls)}"><img decoding="async" src="{esc_url(img)}" '
                     f'alt="{esc(p.get("name", ""))}" /></div>')
        base_classes(self)
        self.add_class("clearfix", self.text_orientation_class(), *bg_layout_classes(self))
        if not image:
            self.add_class("et_pb_team_member_no_image")
        lvl = p.get("header_level", "") or "h4"
        name = f'<{lvl} class="et_pb_module_header">{p.get("name")}</{lvl}>' if p.get("name", "") else ""
        position = f'<p class="et_pb_member_position">{p.get("position")}</p>' if p.get("position", "") else ""
        body = module_content(self.node)
        body = f"<div>{body}</div>" if body else ""
        return (f'<div class="{self.classname()}">\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{self.mask_markup}\n'
                f'\t\t\t\t{image}\n\t\t\t\t<div class="et_pb_team_member_description">\n'
                f'\t\t\t\t\t{name}\n\t\t\t\t\t{position}\n\t\t\t\t\t{body}\n\t\t\t\t\t{links}\n'
                f'\t\t\t\t</div>\n\t\t\t</div>')


# SocialMediaFollowItem.php `social_network` option labels (get_network_name()) and
# ExtendedFontIcons.php et_pb_get_social_net_fa_icons() (networks drawn with FontAwesome).
NETWORK_NAMES = {
    "amazon": "Amazon", "bandcamp": "Bandcamp", "behance": "Behance", "bitbucket": "BitBucket", "buffer": "Buffer",
    "codepen": "CodePen", "deviantart": "DeviantArt", "dribbble": "dribbble", "facebook": "Facebook", "flikr": "Flickr",
    "flipboard": "FlipBoard", "foursquare": "Foursquare", "github": "GitHub", "goodreads": "Goodreads",
    "google": "Google", "houzz": "Houzz", "instagram": "Instagram", "itunes": "iTunes", "last_fm": "Last.fm",
    "line": "Line", "linkedin": "LinkedIn", "medium": "Medium", "meetup": "Meetup", "myspace": "MySpace",
    "odnoklassniki": "Odnoklassniki", "patreon": "Patreon", "periscope": "Periscope", "pinterest": "Pinterest",
    "quora": "Quora", "reddit": "Reddit", "researchgate": "ResearchGate", "rss": "RSS", "skype": "skype",
    "snapchat": "Snapchat", "soundcloud": "SoundCloud", "spotify": "Spotify", "steam": "Steam",
    "telegram": "Telegram", "tiktok": "TikTok", "tripadvisor": "TripAdvisor", "tumblr": "tumblr", "twitch": "Twitch",
    "twitter": "X", "vimeo": "Vimeo", "vk": "VK", "weibo": "Weibo", "whatsapp": "WhatsApp", "xing": "XING",
    "yelp": "Yelp", "youtube": "Youtube"}
FA_NETWORKS = {"amazon", "bandcamp", "telegram", "bitbucket", "behance", "buffer", "codepen", "deviantart",
               "flipboard", "foursquare", "github", "goodreads", "google", "houzz", "itunes", "last_fm", "line",
               "medium", "meetup", "odnoklassniki", "patreon", "periscope", "quora", "researchgate", "reddit",
               "snapchat", "soundcloud", "spotify", "steam", "tripadvisor", "tiktok", "twitch", "vk", "weibo",
               "whatsapp", "xing", "yelp"}


def social_icon_size(m: Module, selector: str, wrapper: str):
    """StyleProcessor::process_social_media_icon_font_size(): the icon at the given size inside a
    square twice as large, responsive and hover."""
    vals = property_values(m.props, "icon_font_size")
    for dev in DEVICES:
        v = vals[dev]
        if v:
            d = multiply_unit(v, 2, 0)
            m.css(selector, f"font-size:{v}; line-height:{d}; height:{d}; width:{d};", dev)
            m.css(wrapper, f"height:{d}; width:{d};", dev)
    hv = hover_value(m.props, "icon_font_size")
    if hv:
        d = multiply_unit(hv, 2, 0)
        m.css(add_hover_to_selectors(selector), f"font-size:{hv}; line-height:{d}; height:{d}; width:{d};")
        m.css(add_hover_to_selectors(wrapper), f"height:{d}; width:{d};")


@register("et_pb_social_media_follow")
class SocialMediaFollow(Module):
    slug = "et_pb_social_media_follow"
    TRANSITIONS = {"icon_color": {"color": "%%order_class%% li a.icon:before"},
                   "icon_font_size": {"font-size": "%%order_class%% li a.icon:before",
                                      "line-height": "%%order_class%% li a.icon:before",
                                      "height": "%%order_class%% li a.icon", "width": "%%order_class%% li a.icon"}}

    def render(self):
        p = self.props
        self.process_additional()
        self.generate_styles("icon_color", "%%order_class%% li.et_pb_social_icon a.icon:before", "color",
                             hover_loc="suffix")
        if p.get("use_icon_font_size", "") != "off":
            social_icon_size(self, "%%order_class%% li a.icon:before", "%%order_class%% li a.icon")
        # before_render(): the children read the link target and follow-button setting
        prev = self.ctx.social_follow
        self.ctx.social_follow = self
        inner = self.content_html()
        self.ctx.social_follow = prev
        base_classes(self)
        self.add_class("clearfix", self.text_orientation_class(), *bg_layout_classes(self))
        if p.get("follow_button", "") == "on":
            self.add_class("has_follow_button")
        return (f'<ul class="{self.classname()}">\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{self.mask_markup}\n'
                f'\t\t\t\t{inner}\n\t\t\t</ul>')


@register("et_pb_social_media_follow_network")
class SocialMediaFollowNetwork(Module):
    slug = "et_pb_social_media_follow_network"
    _ICON = ".et_pb_social_media_follow %%order_class%% .icon:before"
    TRANSITIONS = {"icon_color": {"color": _ICON},
                   "icon_font_size": {"font-size": _ICON, "line-height": _ICON,
                                      "height": ".et_pb_social_media_follow %%order_class%% .icon",
                                      "width": ".et_pb_social_media_follow %%order_class%% .icon"}}

    def render(self):
        p = self.props
        parent = self.ctx.social_follow
        new_window = parent.props.get("url_new_window", "") == "on" if parent else True
        follow = parent is not None and parent.props.get("follow_button", "") == "on"
        self.process_additional()
        network = p.get("social_network", "")
        url = p.get("url", "")
        if network == "skype":
            url = f"skype:{p.get('skype_url', '')}?{p.get('skype_action', '')}"
        label = self.raw_content().strip()
        name = esc(NETWORK_NAMES.get(label, label))
        if any(p.get(k, "") for k in ("custom_padding", "custom_padding_tablet", "custom_padding_phone")):
            self.css(".et_pb_social_media_follow li%%order_class%% a", "width: auto; height: auto;")
        self.generate_styles("icon_color", ".et_pb_social_media_follow %%order_class%%.et_pb_social_icon .icon:before",
                             "color", hover=False)
        hc = hover_value(p, "icon_color")
        if hc:
            self.css(".et_pb_social_media_follow %%order_class%%.et_pb_social_icon:hover .icon:before", f"color: {hc};")
        if p.get("use_icon_font_size", "") != "off":
            social_icon_size(self, self._ICON, ".et_pb_social_media_follow %%order_class%% .icon")
        base_classes(self)
        self.classes = [c for c in self.classes if c not in ("et_pb_module", self.render_slug)]
        self.add_class("et_pb_social_icon", "et_pb_social_network_link")
        if network:
            self.add_class(f"et-social-{network}")
            if network in FA_NETWORKS:
                self.add_class("et-pb-social-fa-icon")
        target = ' target="_blank"' if new_window else ""
        button = (f'<a href="{esc_url(url)}" class="follow_button" title="{name}"{target}>Follow</a>' if follow else "")
        return (f"<li\n            class='{self.classname()}'><a\n              href='{esc_url(url)}'\n"
                f"              class='icon et_pb_with_border'\n              title='Follow on {name}'\n"
                f"              {target}><span\n                class='et_pb_social_media_follow_network_name'\n"
                f"                aria-hidden='true'\n                >Follow</span></a>{button}</li>")
