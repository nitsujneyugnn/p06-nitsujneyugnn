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


class GifTransparencyTestCase(TestCase):
    """Resizing a palette GIF must not turn its transparent pixels opaque.

    See thumbor/thumbor#1886.
    """

    def get_context(self):
        cfg = Config(
            SECURITY_KEY="ACME-SEC",
            ENGINE="thumbor.engines.pil",
            PILLOW_PRESERVE_INDEXED_MODE=True,
        )
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = STORAGE_PATH
        cfg.STORAGE = "thumbor.storages.no_storage"

        return Context(config=cfg)

    def setUp(self):
        self.context = self.get_context()

    def _load_sticker(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "sticker.gif"), "rb") as image_file:
            buffer = image_file.read()
        engine.load(buffer, ".gif")
        return engine

    def test_source_gif_has_transparency(self):
        engine = self._load_sticker()
        assert "transparency" in engine.image.info

    def test_resized_gif_keeps_its_transparency(self):
        engine = self._load_sticker()
        assert "transparency" in engine.image.info

        engine.resize(240, 160)

        result = Image.open(BytesIO(engine.read()))

        assert result.format == "GIF"
        assert result.size == (240, 160)

        # The saved GIF must carry a transparency index ...
        assert "transparency" in result.info

        # ... and the pixels that were transparent in the source must still
        # be transparent: the converted RGBA image must have non-opaque
        # pixels, not a solid black box.
        alpha = result.convert("RGBA").getchannel("A")
        assert min(alpha.getextrema()) < 255
