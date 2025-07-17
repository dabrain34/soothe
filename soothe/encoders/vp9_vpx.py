# Soothe - testing framework for encoders quality
# Copyright (C) 2020, Fluendo, S.A.
#  Author: Pablo Marcos Oltra <pmarcos@fluendo.com>, Fluendo, S.A.
# Copyright (C) 2026, Igalia, S.L.
#  Author: Stéphane Cerveau <scerveau@igalia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library. If not, see <https://www.gnu.org/licenses/>.

"""Module for VP9 reference encoder"""

from ..codec import Codec
from ..encoder import register_encoder
from .webm import WebMEncoder


@register_encoder
class VP9VPXEncoder(WebMEncoder):
    """libvpx VP9 reference encoder implementation"""
    encoder_name = "libvpx-VP9"
    codec = Codec.VP9
    description = "libvpx VP9 reference encoder"
    binary = "vpxenc"
    is_reference = True
    extra_args = [
        "--codec=vp9",
        "--good",
        "--cpu-used=4",
        "--end-usage=q",
        "--cq-level=30",
        "--threads=4",
        "--webm",
    ]
