# MIT License
#
# Copyright (c) [2024] [I-Hao Chen]
# Copyright (c) [2017] [Stefan Huber]

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import numpy as np
import pandas as pd


class Peak:
    def __init__(self, startidx, value):
        self.born = startidx
        self.left = startidx
        self.right = startidx
        self.value = value
        self.died = None

    def get_persistence(self, seq):
        return -1 if self.died is None else seq[self.born] - seq[self.died]


def get_persistent_homology(seq):
    # Some changes to the code :D

    peaks = []
    # Maps indices to peaks
    idxtopeak = [None for s in seq]
    # Sequence indices sorted by values
    indices = range(len(seq))
    indices_sorted = sorted(indices, key=lambda i: seq[i], reverse=True)

    # Process each sample in descending order
    for idx in indices_sorted:
        lftdone = (idx > 0 and idxtopeak[idx - 1] is not None)
        rgtdone = (idx < len(seq) - 1 and idxtopeak[idx + 1] is not None)
        il = idxtopeak[idx - 1] if lftdone else None
        ir = idxtopeak[idx + 1] if rgtdone else None

        # New peak born
        if not lftdone and not rgtdone:
            peaks.append(Peak(idx, seq[idx]))
            idxtopeak[idx] = len(peaks) - 1

        # Directly merge to next peak left
        if lftdone and not rgtdone:
            peaks[il].right += 1
            idxtopeak[idx] = il

        # Directly merge to next peak right
        if not lftdone and rgtdone:
            peaks[ir].left -= 1
            idxtopeak[idx] = ir

        # Merge left and right peaks
        if lftdone and rgtdone:
            # Left was born earlier: merge right to left
            if seq[peaks[il].born] > seq[peaks[ir].born]:
                peaks[ir].died = idx
                peaks[il].right = peaks[ir].right
                idxtopeak[peaks[il].right] = idxtopeak[idx] = il
            else:
                peaks[il].died = idx
                peaks[ir].left = peaks[il].left
                idxtopeak[peaks[ir].left] = idxtopeak[idx] = ir
    # This is optional convenience
    peak_data = {
        'born': [peak.born for peak in peaks],
        'left': [peak.left for peak in peaks],
        'right': [peak.right for peak in peaks],
        'value': [peak.value for peak in peaks],
        'died': [peak.died if isinstance(peak.died, int) else -1 for peak in peaks]
    }
    peak_data["died"] = [int(el) for el in peak_data["died"]]

    peaks_df = pd.DataFrame(peak_data)
    peaks_df["persistence"] = [
        peak.get_persistence(seq) if peak.get_persistence(seq) != -1 else peak.value - np.min(seq) for
        peak in peaks]
    return peaks_df.sort_values(by="persistence", ascending=False)
