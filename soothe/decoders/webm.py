"""Common base class for WebM reference decoders (aomdec, vpxdec)"""
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

from typing import List

from ..codec import OutputFormat
from ..decoder import Decoder
from ..utils import file_checksum, run_command


class WebMDecoder(Decoder):
    """Base class for WebM reference decoders (aomdec, vpxdec)"""

    extra_args: List[str] = []

    def decode(
        self,
        input_filepath: str,
        output_filepath: str,
        output_format: OutputFormat,
        *,
        timeout: int,
        verbose: bool,
    ) -> str:
        """Decodes input_filepath in output_filepath"""
        fmt = "--rawvideo"
        if output_format in [OutputFormat.YUV420P,
                             OutputFormat.YUV420P10LE]:
            fmt = "--i420"

        cmd = [
            self.binary,
            *self.extra_args,
            fmt,
            input_filepath,
            "-o",
            output_filepath,
        ]

        run_command(cmd, timeout=timeout, verbose=verbose)
        return file_checksum(output_filepath)
