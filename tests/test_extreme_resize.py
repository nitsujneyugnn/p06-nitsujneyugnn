# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from io import BytesIO
from os.path import abspath, dirname, join
from unittest import TestCase

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine

FIXTURES_PATH = abspath(join(dirname(__file__), "fixtures/"))
STORAGE_PATH = join(FIXTURES_PATH, "images")


class ExtremeResizeTestCase(TestCase):
    """A resize far from the source ratio must still return a real image.

    See thumbor/thumbor#1711.
    """

    def get_context(self, width, height, fit_in=False):
        cfg = Config(
            SECURITY_KEY="ACME-SEC",
            ENGINE="thumbor.engines.pil",
        )
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = STORAGE_PATH
        cfg.STORAGE = "thumbor.storages.no_storage"

        context = Context(config=cfg)
        context.request = type(
            "Request",
            (),
            {
                "width": width,
                "height": height,
                "fit_in": fit_in,
                "full": False,
                "adaptive": False,
                "stretch": False,
                "debug": False,
                "smart": False,
                "trim": None,
                "should_crop": False,
                "horizontal_flip": False,
                "vertical_flip": False,
                "focal_points": [],
                "halign": "center",
                "valign": "middle",
            },
        )()
        context.request.engine = Engine(context)

        return context

    def _load(self, context, name):
        with open(join(STORAGE_PATH, name), "rb") as image_file:
            context.request.engine.load(image_file.read(), None)
        return context.request.engine

    def _transform_and_read(self, context, name):
        from thumbor.transformer import Transformer

        engine = self._load(context, name)
        transformer = Transformer(context)
        transformer._calculate_target_dimensions()
        transformer.adjust_focal_points()
        if context.request.fit_in:
            transformer.fit_in_resize()
        else:
            transformer.auto_crop()
            transformer.resize()
        return Image.open(BytesIO(engine.read()))

    def test_very_wide_and_short_resize_is_not_blank(self):
        result = self._transform_and_read(
            self.get_context(800, 20), "rainbow.png"
        )
        assert result.size == (800, 20)

        # The source is transparent with coloured bars: a real strip must
        # have at least some non-transparent pixels, not a fully blank image.
        alpha = result.convert("RGBA").getchannel("A")
        assert max(alpha.getextrema()) > 0

    def test_fit_in_one_by_one_returns_one_pixel(self):
        result = self._transform_and_read(
            self.get_context(1, 1, fit_in=True), "940x2.png"
        )
        assert result.size == (1, 1)

    def test_fit_in_width_only_returns_a_real_image(self):
        result = self._transform_and_read(
            self.get_context(100, 0, fit_in=True), "940x2.png"
        )
        assert result.size == (100, 1)
