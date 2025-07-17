"""Common base class for WebM reference encoders (aomenc, vpxenc)"""
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

from ..encoder import Encoder
from ..utils import run_command


class WebMEncoder(Encoder):
    """Base class for WebM reference encoders (aomenc, vpxenc)"""

    file_extension = ".webm"
    extra_args: List[str] = []

    def encode(
        self,
        input_file: str,
        output_file: str,
        timeout: int,
        verbose: bool,
    ):
        """Encodes input_file in output_file"""
        cmd = [
            self.binary,
            *self.extra_args,
            "-o",
            output_file,
            input_file,
        ]

        run_command(cmd, timeout=timeout, verbose=verbose)
