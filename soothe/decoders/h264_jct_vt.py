"""JCT-VT H.264/AVC reference decoder"""
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

from ..codec import Codec
from ..decoder import register_decoder
from .jct_vt import JCTVTDecoder


@register_decoder
class H264JCTVTDecoder(JCTVTDecoder):
    """JCT-VT H.264/AVC reference decoder implementation"""

    name = "JCT-VT-H.264"
    description = "JCT-VT H.264/AVC reference decoder"
    codec = Codec.H264
    binary = "ldecod"
    is_reference = True
    input_flag = "-i"
    extra_flags = ("-s",)
