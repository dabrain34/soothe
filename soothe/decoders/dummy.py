"""Dummy decoder for testing pipeline"""
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

import shutil

from ..codec import Codec, OutputFormat
from ..decoder import Decoder, register_decoder
from ..utils import file_checksum


@register_decoder
class DummyDecoder(Decoder):
    """Dummy decoder implementation for testing pipeline"""

    name = "Dummy"
    description = "Dummy decoder that copies input to output"
    codec = Codec.DUMMY
    is_reference = True
    outputs_y4m = True

    def decode(
        self,
        input_filepath: str,
        output_filepath: str,
        output_format: OutputFormat,
        *,
        timeout: int,
        verbose: bool,
    ) -> str:
        """Copies input_filepath to output_filepath (dummy decode)"""
        shutil.copyfile(input_filepath, output_filepath)
        return file_checksum(output_filepath)
