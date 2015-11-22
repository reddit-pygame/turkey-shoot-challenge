import pygame as pg
import prepare, tools

#Used to avoid loading fonts multiple times
LOADED_FONTS = {}

LABEL_DEFAULTS = {
        "font_path": None,
        "font_size": 24,
        "text_color": "white",
        "fill_color": None,
        "alpha": 255}


def _parse_color(color):
    """
    Helper function for Label class to allow passing colors
    by RGB value or colorname.
    """
    if color is not None:
        try:
            return pg.Color(str(color))
        except ValueError:
            return pg.Color(*color)
    return color


class LabelGroup(pg.sprite.Group):
    """Container class for Label objects."""
    def __init__(self):
        super(LabelGroup, self).__init__()


class Label(pg.sprite.Sprite, tools._KwargMixin):
    """
    Parent class all labels inherit from. Color arguments can use color names
    or an RGB tuple. rect_attr should be a dict with keys of pygame.Rect
    attribute names (strings) and the relevant position(s) as values.

    Creates a surface with text blitted to it (self.image) and an associated
    rectangle (self.rect). Label will have a transparent bg if
    fill_color is not passed to __init__.
    """
    def __init__(self, text, rect_attr, *groups, **kwargs):
        super(Label, self).__init__(*groups)
        self.process_kwargs("Label", LABEL_DEFAULTS, kwargs)
        path, size = self.font_path, self.font_size
        if (path, size) not in LOADED_FONTS:
            LOADED_FONTS[(path, size)] = pg.font.Font(path, size)
        self.font = LOADED_FONTS[(path, size)]
        self.fill_color = _parse_color(self.fill_color)
        self.text_color = _parse_color(self.text_color)
        self.rect_attr = rect_attr
        self.set_text(text)

    def set_text(self, text):
        """Set the text to display."""
        self.text = text
        self.update_text()

    def update_text(self):
        """Update the surface using the current properties and text."""
        if self.fill_color:
            render_args = (self.text, True, self.text_color, self.fill_color)
        else:
            render_args = (self.text, True, self.text_color)
        self.image = self.font.render(*render_args)
        if self.alpha != 255:
            self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect(**self.rect_attr)

    def draw(self, surface):
        """Blit self.image to target surface."""
        surface.blit(self.image, self.rect)