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

"""Test module"""

import os

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from subprocess import TimeoutExpired
from time import perf_counter
from typing import Optional, Tuple

from .asset import Asset
from .encoder import Encoder
from .decoder import get_reference_decoder_for_codec
from .codec import OutputFormat
from .utils import normalize_path, run_command_with_output


@dataclass
class Params:  # pylint: disable=too-many-instance-attributes
    """Params for a test"""

    encoder: Encoder
    asset: Tuple[str, Asset]
    vmaf_binary: Path
    resources_dir: str
    output_dir: str
    timeout: int
    keep_files: bool = False
    verbose: bool = False


class CodecTestResult(Enum):
    """Encode test result"""

    NOT_RUN = "Not Run"
    SUCCESS = "Success"
    FAIL = "Fail"
    TIMEOUT = "Timeout"
    ERROR = "Error"


@dataclass
class Result:
    """Test result class"""

    asset_fname: Optional[str] = None
    encoder_name: Optional[str] = None
    encode_time: float = 0.0
    encode_result: CodecTestResult = CodecTestResult.NOT_RUN
    decode_result: CodecTestResult = CodecTestResult.NOT_RUN
    decode_time: float = 0.0
    vmaf_result: CodecTestResult = CodecTestResult.NOT_RUN
    vmaf_score: float = 0.0
    vmaf_time: float = 0.0

    def __str__(self):
        s = f'{self.encoder_name} — {self.asset_fname} '
        if self.encode_result is not CodecTestResult.SUCCESS:
            return f'{s} → Encode {self.encode_result.value}'
        if self.decode_result is not CodecTestResult.SUCCESS:
            return f'{s} → Decode {self.decode_result.value}'
        if self.vmaf_result is not CodecTestResult.SUCCESS:
            return f'{s} → VMAF {self.vmaf_result.value}'
        time = self.encode_time + self.decode_time + self.vmaf_time
        return f'{s} [{time:.3f}s] → {self.vmaf_score:.5f}'


class Test:  # pylint: disable=too-few-public-methods
    """Test class"""

    def __init__(self, params: Params):
        self.params = params

    def convert_yuv_to_y4m(self, yuv_filepath: str, y4m_filepath: str,
                           width: int, height: int,
                           framerate: str = "24:1") -> None:
        """Convert YUV420P file to Y4M format"""
        # Input validation
        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid dimensions: width={width}, "
                             f"height={height}")

        frame_size = width * height * 3 // 2  # YUV420P: Y + U/2 + V/2

        try:
            with open(yuv_filepath, 'rb') as yuv_file:
                with open(y4m_filepath, 'w+b') as y4m_file:
                    # Write Y4M header
                    header = (f"YUV4MPEG2 W{width} H{height} F{framerate} "
                              f"Ip A1:1 C420\n")
                    y4m_file.write(header.encode('ascii'))

                    frame_count = 0
                    while True:
                        # Read one frame of YUV data
                        frame_data = yuv_file.read(frame_size)
                        if len(frame_data) != frame_size:
                            break

                        # Write frame header
                        y4m_file.write(b"FRAME\n")
                        # Write frame data
                        y4m_file.write(frame_data)
                        frame_count += 1

                    if self.params.verbose:
                        print(f"Converted {frame_count} frames from YUV to "
                              f"Y4M format")
        except IOError as e:
            raise IOError(f"Failed to convert YUV to Y4M: {e}") from e

    def run(self, result: Result) -> None:
        """Run the test"""

        encoded_filepath = os.path.join(
            self.params.output_dir,
            self.params.asset[1].name + "_encoded" +
            self.params.encoder.get_file_extension()
        )
        # Determine output file extension based on decoder
        decoder = get_reference_decoder_for_codec(self.params.encoder.codec)
        decoded_ext = ".y4m" if decoder and decoder.outputs_y4m else ".yuv"
        decoded_filepath = os.path.join(
            self.params.output_dir,
            self.params.asset[1].name + "_decoded" + decoded_ext
        )
        input_filepath = os.path.join(
            self.params.resources_dir,
            self.params.asset[0],
            self.params.asset[1].filename,
        )
        encoded_filepath = normalize_path(encoded_filepath)
        decoded_filepath = normalize_path(decoded_filepath)
        input_filepath = normalize_path(input_filepath)

        result.asset_fname = self.params.asset[1].filename
        result.encoder_name = self.params.encoder.name()

        # Step 1: Encode
        try:
            start = perf_counter()
            self.params.encoder.encode(
                input_filepath,
                encoded_filepath,
                self.params.timeout,
                self.params.verbose,
            )
            result.encode_time = perf_counter() - start
            result.encode_result = CodecTestResult.SUCCESS
        except TimeoutExpired:
            result.encode_result = CodecTestResult.TIMEOUT
            raise
        except Exception:
            result.encode_result = CodecTestResult.ERROR
            raise

        # Step 2: Decode (only if encode was successful)
        if result.encode_result is CodecTestResult.SUCCESS:
            if decoder and decoder.check(self.params.verbose):
                try:
                    start = perf_counter()
                    decoder.decode(
                        encoded_filepath,
                        decoded_filepath,
                        OutputFormat.YUV420P,
                        timeout=self.params.timeout,
                        verbose=self.params.verbose,
                    )
                    result.decode_time = perf_counter() - start
                    result.decode_result = CodecTestResult.SUCCESS

                    # Convert YUV to Y4M if decoder outputs raw YUV
                    if decoder and not decoder.outputs_y4m:
                        y4m_filepath = decoded_filepath.replace('.yuv', '.y4m')
                        try:
                            asset = self.params.asset[1]
                            self.convert_yuv_to_y4m(
                                decoded_filepath,
                                y4m_filepath,
                                asset.width,
                                asset.height,
                                framerate=asset.framerate
                            )
                            # Delete the YUV file after successful conversion
                            os.remove(decoded_filepath)
                            # Update decoded_filepath to point to Y4M file
                            # for VMAF
                            decoded_filepath = y4m_filepath
                        except Exception as e:
                            if self.params.verbose:
                                print(f"YUV to Y4M conversion failed: {e}. "
                                      f"Continue with original YUV file.")
                except TimeoutExpired:
                    result.decode_result = CodecTestResult.TIMEOUT
                    raise
                except Exception:
                    result.decode_result = CodecTestResult.ERROR
                    raise
            else:
                if self.params.verbose:
                    print(f"No reference decoder available or usable "
                          f"for codec {self.params.encoder.codec}")
                result.decode_result = CodecTestResult.ERROR

        # Step 3: VMAF (only if decode was successful)
        if result.decode_result is CodecTestResult.SUCCESS:
            cmd = [
                str(self.params.vmaf_binary),
                '--quiet',
                '--reference',
                input_filepath,
                '--distorted',
                decoded_filepath
            ]

            # Add resolution parameters only for raw YUV files
            # Note: Y4M files contain metadata, so no additional parameters
            # needed
            if (decoder and not decoder.outputs_y4m and
                    not decoded_filepath.endswith('.y4m')):
                asset = self.params.asset[1]
                cmd.extend([
                    '--width',
                    str(asset.width),
                    '--height',
                    str(asset.height),
                    '--pixel_format',
                    '420',
                    '--bitdepth',
                    '8'
                ])
            try:
                start = perf_counter()
                output = run_command_with_output(
                    command=cmd,
                    verbose=self.params.verbose,
                )
                result.vmaf_time = perf_counter() - start
                try:
                    result.vmaf_score = float(output.split(':')[1])
                    result.vmaf_result = CodecTestResult.SUCCESS
                except (IndexError, ValueError):
                    result.vmaf_result = CodecTestResult.FAIL
            except Exception:
                result.vmaf_result = CodecTestResult.ERROR
                raise

        # Clean up temporary files
        if not self.params.keep_files:
            for filepath in [encoded_filepath, decoded_filepath]:
                if os.path.exists(filepath) and os.path.isfile(filepath):
                    os.remove(filepath)
