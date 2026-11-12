# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

# Issue #2 (thumbor/thumbor#1687): with the transparent flag, the pixels on
# the curve of a rounded corner stay fully opaque and are darkened, which
# draws a dark ring. The edge pixels should be partly transparent.

from tornado.testing import gen_test

from tests.base import FilterTestCase


class RoundCornerRingTestCase(FilterTestCase):
    @gen_test
    async def test_transparent_round_corner_edge_is_partly_transparent(self):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(50,255,255,255,1)",
            mode="RGBA",
        )

        # Edge pixel on the 45 degree arc of a 50 pixel radius corner.
        _, _, _, alpha = image.getpixel((14, 14))

        assert alpha < 255, (
            f"arc pixel is fully opaque (alpha={alpha}); "
            "the edge has no transparency and shows a dark ring"
        )
