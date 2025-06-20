# Soothe - testing framework for encoders quality
# Copyright (C) 2020, Fluendo, S.A.
#  Author: Pablo Marcos Oltra <pmarcos@fluendo.com>, Fluendo, S.A.
# Copyright (C) 2025, Igalia, S.L.
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

"""Module with the decoder abstract class and the list of available decoders"""


from abc import ABC, abstractmethod
from functools import lru_cache
from shutil import which
from typing import List, Optional, Type

from .codec import Codec, OutputFormat
from .utils import normalize_binary_cmd


class Decoder(ABC):
    """Base class for decoders"""

    name = ""
    codec = Codec.NONE
    description = ""
    binary = ""
    is_reference = False
    outputs_y4m = False  # True if decoder outputs Y4M, False for raw YUV

    def __init__(self) -> None:
        if self.binary:
            self.binary = normalize_binary_cmd(self.binary)

    @abstractmethod
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
        raise NotImplementedError

    @lru_cache(maxsize=128)
    def check(self, verbose: bool) -> bool:
        """Checks whether the decoder can be run"""
        if hasattr(self, "binary") and self.binary:
            try:
                path = which(self.binary)
                if verbose and not path:
                    print(f"Binary {self.binary} can't be found to be "
                          f"executed")

                return path is not None
            except OSError:
                return False
        return True

    def __str__(self) -> str:
        return f"    {self.name}: {self.description}"


DECODERS: List[Decoder] = []


def register_decoder(cls: Type[Decoder]) -> Type[Decoder]:
    """Register a new decoder implementation"""
    DECODERS.append(cls())
    DECODERS.sort(key=lambda dec: dec.name)
    return cls


def get_reference_decoder_for_codec(codec: Codec) -> Optional["Decoder"]:
    """Find the reference decoder for a specific codec"""

    reference_decoders = [d for d in DECODERS if d.codec == codec and
                          d.is_reference]

    if not reference_decoders:
        return None
    if len(reference_decoders) > 1:
        print(f"Multiple reference decoders found for codec {codec.name}")

    return reference_decoders[0]
