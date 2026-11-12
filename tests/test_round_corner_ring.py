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

        # Scan the 45 degree arc of a 50 pixel radius corner. The edge must
        # contain at least one partly transparent pixel. On base the diagonal
        # jumps from alpha 0 straight to 255 with no partial value.
        alphas = [
            image.getpixel((i, i))[3] for i in range(12, 19)
        ]

        assert any(0 < a < 255 for a in alphas), (
            f"no partly transparent edge pixel on the arc: alphas={alphas}; "
            "the edge is hard and shows a dark ring"
        )
