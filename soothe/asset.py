# Soothe - testing framework for encoders quality
# Copyright (C) 2020, Fluendo, S.A.
#  Author: Pablo Marcos Oltra <pmarcos@fluendo.com>, Fluendo, S.A.
# Copyright (C) 2025, Igalia, S.L.
#  Author: Victor Jaquez <vjaquez@igalia.com>
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

"""Module that holds an asset"""

from dataclasses import dataclass, field
from typing import Any, Type


@dataclass
class Asset:
    """Asset class"""

    # JSON members
    name: str
    source: str
    checksum: str
    filename: str
    width: int
    height: int
    framerate: str

    # Not in JSON
    test_time: float = field(default=0.0, init=False)

    @classmethod
    def from_json(cls: Type["Asset"], data: Any) -> Any:
        """Deserialize an instance of Asset from json file"""
        return (data["name"], cls(**data))

    def __str__(self) -> str:
        return self.filename
