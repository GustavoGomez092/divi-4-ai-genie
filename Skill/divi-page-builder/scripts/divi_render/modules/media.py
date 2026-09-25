"""Media modules: Fullwidth Image, Video, Audio and Gallery (templates from each module's render()).

Remote media is never fetched: Divi's markup is reproduced with the given URLs (the browser loads
them) and runtime behaviour (MediaElement players, lightboxes, sliders) is left to Divi's JS.
"""
from __future__ import annotations

import base64
import re

from ..base import Module, base_classes, bg_layout_classes, register
from ..values import DEVICES, decode_icon, esc, esc_url, new_window, property_values


def overlay_span(m: Module, base: str = "hover_icon") -> str:
    """ET_Builder_Module_Helper_Overlay::render(): the hover overlay, with inline-icon classes
    and data-icon attributes for the responsive icon values."""
    vals = property_values(m.props, base)
    classes, attrs = ["et_overlay"], []
    for dev, suffix in (("desktop", ""), ("tablet", "_tablet"), ("phone", "_phone")):
        if vals[dev]:
            classes.append(f"et_pb_inline_icon{suffix}")
            attrs.append(f'data-icon{suffix.replace("_", "-")}="{esc(decode_icon(vals[dev]))}"')
    return f'<span class="{" ".join(classes)}"{" " + " ".join(attrs) if attrs else ""}></span>'


def media_wrap(m: Module, inner: str) -> str:
    """The common module shell: video/parallax backgrounds, pattern and mask, then the content."""
    return (f'<div class="{m.classname()}">\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{m.mask_markup}\n'
            f'\t\t\t\t{inner}\n\t\t\t</div>')


@register("et_pb_fullwidth_image")
class FullwidthImage(Module):
    slug = "et_pb_fullwidth_image"

    def render(self):
        p = self.props
        self.process_additional()
        url, lightbox = p.get("url", ""), p.get("show_in_lightbox", "") == "on"
        # FullwidthImage.php: the overlay needs a link or the lightbox
        overlay = p.get("use_overlay", "") == "on" and (lightbox or url != "")
        if overlay:
            self.generate_styles("overlay_icon_color", "%%order_class%% .et_overlay:before", "color", important=True,
                                 hover=False)
            self.generate_styles("hover_overlay_color", "%%order_class%% .et_overlay", "background-color", hover=False)
            self.icon_style("hover_icon", "%%order_class%% .et_overlay:before")
        src = p.get("src", "")
        title = p.get("title_text", "")
        img = (f'<img decoding="async" src="{esc_url(src)}" alt="{esc(p.get("alt", ""))}" title="{esc(title)}" />'
               if src else "")
        out = f'{img}\n\t\t\t{overlay_span(self) if overlay else ""}'
        if lightbox:
            out = f'<a href="{esc(src)}" class="et_pb_lightbox_image" title="{esc(title)}">{out}</a>'
        elif url:
            out = f'<a href="{esc_url(url)}"{new_window(p)}>{out}</a>'
        base_classes(self)
        if p.get("animation_style", "") not in ("", "none"):
            self.add_class("et-waypoint")
        if overlay:
            self.add_class("et_pb_has_overlay")
        return media_wrap(self, out)


@register("et_pb_video")
class Video(Module):
    slug = "et_pb_video"
    PLAY = "%%order_class%% .et_pb_video_overlay .et_pb_video_play"
    TRANSITIONS = {"play_icon_color": {"color": PLAY},
                   "icon_font_size": {"font-size": PLAY, "line-height": PLAY, "margin-top": PLAY, "margin-left": PLAY}}

    def render(self):
        p = self.props
        self.process_additional()
        self.generate_styles("play_icon_color", self.PLAY, "color", hover_loc="suffix")
        self.icon_style("font_icon", f"{self.PLAY}:before", content=True)
        if p.get("use_icon_font_size", "") != "off":
            self.overlay_icon_size(self.PLAY, "font-size:{0}; line-height:{0}; margin-top:-{1}; margin-left:-{1};")
        self.generate_styles("thumbnail_overlay_color", "%%order_class%% .et_pb_video_overlay_hover:hover",
                             "background-color", hover=False)
        box = f'<div class="et_pb_video_box">{self.video_html()}</div>'
        cover = p.get("image_src", "")
        overlay = (f'<div style="background-image:url({esc(cover)})" class="et_pb_video_overlay">'
                   f'<div class="et_pb_video_overlay_hover"><a href="#" class="et_pb_video_play"></a></div></div>'
                   if cover else "")
        base_classes(self)
        return media_wrap(self, f"{box}\n\t\t\t\t{overlay}")

    def video_html(self) -> str:
        """Video.php get_video(): YouTube/Vimeo URLs go through WordPress oEmbed, which needs the
        network; here they become the iframe oEmbed would return (listed in the coverage report as
        video_oembed). Anything else is a native <video> with its mp4/webm sources."""
        p = self.props
        src, webm = p.get("src", ""), p.get("src_webm", "")
        embed = oembed_iframe(src)
        if embed:
            self.ctx.count_unsupported("video_oembed")
            return embed
        return ("\n\t\t\t\t<video controls>\n\t\t\t\t\t"
                + (f'<source type="video/mp4" src="{esc_url(src)}" />' if src else "") + "\n\t\t\t\t\t"
                + (f'<source type="video/webm" src="{esc_url(webm)}" />' if webm else "") + "\n\t\t\t\t</video>")


YOUTUBE = re.compile(r"(?:youtube\.com/(?:watch\?(?:.*&)?v=|embed/|shorts/)|youtu\.be/)([\w-]{6,})")
VIMEO = re.compile(r"vimeo\.com/(?:video/)?(\d+)")


def oembed_iframe(url: str) -> str:
    m = YOUTUBE.search(url or "")
    if m:
        src = f"https://www.youtube.com/embed/{m.group(1)}?feature=oembed"
    else:
        m = VIMEO.search(url or "")
        if not m:
            return ""
        src = f"https://player.vimeo.com/video/{m.group(1)}?dnt=1&amp;app_id=122963"
    return (f'<iframe title="Video" width="1080" height="608" src="{src}" frameborder="0" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; '
            'web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>')


AUDIO_TYPES = {"mp3": "audio/mpeg", "m4a": "audio/mpeg", "ogg": "audio/ogg", "flac": "audio/flac", "wav": "audio/wav"}


@register("et_pb_audio")
class Audio(Module):
    slug = "et_pb_audio"

    def render(self):
        p = self.props
        self.process_additional()
        lvl = p.get("title_level", "") or "h2"
        title = f'<{lvl} class="et_pb_module_header">{p.get("title")}</{lvl}>' if p.get("title", "") else ""
        metas = []
        if p.get("artist_name", ""):
            metas.append(f'by <strong>{p.get("artist_name")}</strong>')
        if p.get("album_name", ""):
            metas.append(f'<span>{p.get("album_name")}</span>')
        meta = f'<p class="et_audio_module_meta">{" | ".join(metas)}</p>' if metas else ""
        image = p.get("image_url", "")
        cover = f'<div style="background-image:url({esc(image)})" class="et_pb_audio_cover_art"></div>' if image else ""
        base_classes(self)
        self.add_class("et_pb_audio_module", "clearfix", *bg_layout_classes(self, text_color=True))
        if not image:
            self.add_class("et_pb_audio_no_image")
        self.classes.remove("et_pb_audio")  # Audio.php: remove_classname( $render_slug )
        return (f'<div class="{self.classname()}">\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{self.mask_markup}\n'
                f'\t\t\t\t{cover}\n\t\t\t\t<div class="et_pb_audio_module_content et_audio_container">\n'
                f'\t\t\t\t\t{title}\n\t\t\t\t\t{meta}\n\t\t\t\t\t{self.audio_html()}\n\t\t\t\t</div>\n\t\t\t</div>')

    def audio_html(self) -> str:
        """Audio::get_audio() = do_shortcode('[audio src="..."]'), i.e. wp_audio_shortcode()."""
        src = self.props.get("audio", "")
        if not src:
            return ""
        ext = src.split("?")[0].rsplit(".", 1)[-1].lower()
        if ext not in AUDIO_TYPES:
            return f'<a class="wp-embedded-audio" href="{esc_url(src)}">{esc(src)}</a>'
        n = self.ctx.next_index("wp_audio_shortcode") + 1
        return (f'<audio class="wp-audio-shortcode" id="audio-0-{n}" preload="none" style="width: 100%;" '
                f'controls="controls"><source type="{AUDIO_TYPES[ext]}" src="{esc_url(src)}?_={n}" />'
                f'<a href="{esc_url(src)}">{esc_url(src)}</a></audio>')


def placeholder_image(width: int, height: int) -> str:
    """A neutral grey SVG standing in for a media-library image the renderer can't resolve."""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
           f'<rect width="100%" height="100%" fill="#d1d5db"/></svg>')
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


@register("et_pb_gallery")
class Gallery(Module):
    """Gallery.php. Images come from the media library (gallery_ids are attachment IDs), which
    the Python renderer can't read. With no IDs Divi finds no attachments and prints nothing but
    the module CSS, exactly as here. With IDs, each becomes a grey placeholder item (400x284, or
    400x516 portrait) in Divi's grid or slider markup, and the coverage report counts them under
    `gallery_attachments`. The real images only show on the client's site (a WordPress draft
    preview): --exact runs a fresh Playground site with no media, where Divi prints nothing."""
    slug = "et_pb_gallery"

    def render(self):
        p = self.props
        self.process_additional()
        fullwidth = p.get("fullwidth", "") == "on"
        self.generate_styles("zoom_icon_color", "%%order_class%% .et_overlay:before", "color", important=True,
                             hover=False)
        vals = property_values(p, "hover_overlay_color")
        for dev in DEVICES:
            if vals[dev]:
                self.css("%%order_class%% .et_overlay",
                         f"background-color: {vals[dev]}; border-color: {vals[dev]};", dev)
        ids = [i.strip() for i in p.get("gallery_ids", "").split(",") if i.strip()]
        if not ids:  # get_gallery() found no attachments: render() returns ''
            return ""
        self.ctx.count_unsupported("gallery_attachments", len(ids))
        orientation = "portrait" if p.get("orientation", "") == "portrait" else "landscape"
        num = re.match(r"\s*(\d+)", p.get("posts_number", ""))
        per_page = (int(num.group(1)) if num else 0) or 4  # 0 === intval( $posts_number ) ? 4 : ...
        base_classes(self)
        layout = bg_layout_classes(self)
        self.add_class(self.text_orientation_class(), *layout)
        if fullwidth:
            self.add_class("et_pb_slider", "et_pb_gallery_fullwidth")
            if p.get("auto", "") == "on":
                self.add_class("et_slider_auto", f"et_slider_speed_{p.get('auto_speed', '')}", "clearfix")
        else:
            self.add_class("et_pb_gallery_grid")
            self.icon_style("hover_icon", "%%order_class%% .et_overlay:before")
        w, h = (1080, 608) if fullwidth else (400, 284 if orientation == "landscape" else 516)
        src = placeholder_image(w, h)
        overlay = "" if fullwidth else overlay_span(self)
        order = self.index
        items = ""
        for n, _ in enumerate(ids):
            srcset = "" if fullwidth else f' srcset="{src} 479w, {src} 480w" sizes="(max-width:479px) 479px, 100vw"'
            img = f'<img decoding="async" src="{src}" alt=""{srcset} />'
            items += (f'<div class="et_pb_gallery_item{"" if fullwidth else " et_pb_grid_item"} {" ".join(layout)} '
                      f'et_pb_gallery_item_{order}_{n}">'
                      f'<div class="et_pb_gallery_image {orientation}">\n\t\t\t\t\t<a href="{src}" title="">\n'
                      f'\t\t\t\t\t{img}\n\t\t\t\t\t{overlay}\n\t\t\t\t</a>\n\t\t\t\t</div></div>')
        pagination = ('<div class="et_pb_gallery_pagination"></div>'
                      if not fullwidth and p.get("show_pagination", "") == "on" else "")
        return (f'<div class="{self.classname()}">{self.mask_markup}\n'
                f'\t\t\t\t<div class="et_pb_gallery_items et_post_gallery clearfix" data-per_page="{per_page}">'
                f'{items}</div>{pagination}</div>')
