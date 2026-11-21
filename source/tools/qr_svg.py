#!/usr/bin/env python3
"""Standard-library QR code encoder for deck links (byte mode, error correction M, versions 1 to 10).

The deck compiler runs without network access or third-party packages, so it encodes its own
QR codes. Follows ISO/IEC 18004 and the structure of Project Nayuki's reference encoder.
"""

from __future__ import annotations

# Error correction level M only. Index = version.
ECC_PER_BLOCK = [None, 10, 16, 26, 18, 24, 16, 18, 22, 22, 26]
NUM_BLOCKS = [None, 1, 1, 1, 2, 2, 4, 4, 4, 5, 5]
FORMAT_ECL_BITS = 0  # M
MAX_VERSION = 10


def _raw_modules(ver: int) -> int:
    result = (16 * ver + 128) * ver + 64
    if ver >= 2:
        n = ver // 7 + 2
        result -= (25 * n - 10) * n - 55
        if ver >= 7:
            result -= 36
    return result


def _data_codewords(ver: int) -> int:
    return _raw_modules(ver) // 8 - ECC_PER_BLOCK[ver] * NUM_BLOCKS[ver]


def _rs_divisor(degree: int) -> list[int]:
    result = [0] * (degree - 1) + [1]
    root = 1
    for _ in range(degree):
        for j in range(degree):
            result[j] = _rs_mul(result[j], root)
            if j + 1 < degree:
                result[j] ^= result[j + 1]
        root = _rs_mul(root, 0x02)
    return result


def _rs_remainder(data: list[int], divisor: list[int]) -> list[int]:
    result = [0] * len(divisor)
    for b in data:
        factor = b ^ result.pop(0)
        result.append(0)
        for i, coef in enumerate(divisor):
            result[i] ^= _rs_mul(coef, factor)
    return result


def _rs_mul(x: int, y: int) -> int:
    z = 0
    for i in reversed(range(8)):
        z = (z << 1) ^ ((z >> 7) * 0x11D)
        z ^= ((y >> i) & 1) * x
    return z


def _codewords(data: bytes) -> tuple[int, list[int]]:
    for ver in range(1, MAX_VERSION + 1):
        count_bits = 8 if ver <= 9 else 16
        needed = 4 + count_bits + 8 * len(data)
        if needed <= _data_codewords(ver) * 8:
            break
    else:
        raise ValueError("text is too long for a version 10 QR code")
    bits: list[int] = []
    def put(value: int, length: int) -> None:
        bits.extend((value >> i) & 1 for i in reversed(range(length)))
    put(0b0100, 4)
    put(len(data), count_bits)
    for b in data:
        put(b, 8)
    capacity = _data_codewords(ver) * 8
    put(0, min(4, capacity - len(bits)))
    put(0, -len(bits) % 8)
    pad = 0xEC
    while len(bits) < capacity:
        put(pad, 8)
        pad ^= 0xEC ^ 0x11
    words = [int("".join(map(str, bits[i:i + 8])), 2) for i in range(0, len(bits), 8)]
    # Split into blocks, add error correction, interleave.
    nblocks, ecc = NUM_BLOCKS[ver], ECC_PER_BLOCK[ver]
    raw = _raw_modules(ver) // 8
    short_count = nblocks - raw % nblocks
    short_len = raw // nblocks
    divisor = _rs_divisor(ecc)
    blocks, k = [], 0
    for i in range(nblocks):
        dlen = short_len - ecc + (0 if i < short_count else 1)
        dat = words[k:k + dlen]
        k += dlen
        block = dat + _rs_remainder(dat, divisor)
        if i < short_count:
            block.insert(dlen, None)
        blocks.append(block)
    out = []
    for i in range(len(blocks[0])):
        for j, block in enumerate(blocks):
            if block[i] is not None:
                out.append(block[i])
    return ver, out


class _Grid:
    def __init__(self, ver: int):
        self.size = ver * 4 + 17
        self.ver = ver
        self.mod = [[False] * self.size for _ in range(self.size)]
        self.fn = [[False] * self.size for _ in range(self.size)]
        self._function_patterns()

    def set_fn(self, x: int, y: int, dark: bool) -> None:
        self.mod[y][x] = dark
        self.fn[y][x] = True

    def _function_patterns(self) -> None:
        s = self.size
        for i in range(s):
            self.set_fn(6, i, i % 2 == 0)
            self.set_fn(i, 6, i % 2 == 0)
        for cx, cy in ((3, 3), (s - 4, 3), (3, s - 4)):
            for dy in range(-4, 5):
                for dx in range(-4, 5):
                    x, y = cx + dx, cy + dy
                    if 0 <= x < s and 0 <= y < s:
                        d = max(abs(dx), abs(dy))
                        self.set_fn(x, y, d not in (2, 4))
        pos = self._align_positions()
        n = len(pos)
        for i in range(n):
            for j in range(n):
                if (i, j) in ((0, 0), (0, n - 1), (n - 1, 0)):
                    continue
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        self.set_fn(pos[i] + dx, pos[j] + dy, max(abs(dx), abs(dy)) != 1)
        self.draw_format(0)
        self._draw_version()

    def _align_positions(self) -> list[int]:
        if self.ver == 1:
            return []
        n = self.ver // 7 + 2
        step = (self.ver * 8 + n * 3 + 5) // (n * 4 - 4) * 2
        result = [self.size - 7 - i * step for i in range(n - 1)] + [6]
        return list(reversed(result))

    def draw_format(self, mask: int) -> None:
        data = FORMAT_ECL_BITS << 3 | mask
        rem = data
        for _ in range(10):
            rem = (rem << 1) ^ ((rem >> 9) * 0x537)
        bits = (data << 10 | rem) ^ 0x5412
        bit = lambda i: (bits >> i) & 1 != 0
        for i in range(6):
            self.set_fn(8, i, bit(i))
        self.set_fn(8, 7, bit(6))
        self.set_fn(8, 8, bit(7))
        self.set_fn(7, 8, bit(8))
        for i in range(9, 15):
            self.set_fn(14 - i, 8, bit(i))
        s = self.size
        for i in range(8):
            self.set_fn(s - 1 - i, 8, bit(i))
        for i in range(8, 15):
            self.set_fn(8, s - 15 + i, bit(i))
        self.set_fn(8, s - 8, True)

    def _draw_version(self) -> None:
        if self.ver < 7:
            return
        rem = self.ver
        for _ in range(12):
            rem = (rem << 1) ^ ((rem >> 11) * 0x1F25)
        bits = self.ver << 12 | rem
        for i in range(18):
            dark = (bits >> i) & 1 != 0
            a, b = self.size - 11 + i % 3, i // 3
            self.set_fn(a, b, dark)
            self.set_fn(b, a, dark)

    def draw_codewords(self, data: list[int]) -> None:
        i, s = 0, self.size
        right = s - 1
        while right >= 1:
            if right == 6:
                right = 5
            for vert in range(s):
                for j in range(2):
                    x = right - j
                    upward = (right + 1) & 2 == 0
                    y = s - 1 - vert if upward else vert
                    if not self.fn[y][x] and i < len(data) * 8:
                        self.mod[y][x] = (data[i >> 3] >> (7 - (i & 7))) & 1 != 0
                        i += 1
            right -= 2

    def apply_mask(self, mask: int) -> None:
        tests = [
            lambda x, y: (x + y) % 2 == 0, lambda x, y: y % 2 == 0, lambda x, y: x % 3 == 0,
            lambda x, y: (x + y) % 3 == 0, lambda x, y: (x // 3 + y // 2) % 2 == 0,
            lambda x, y: x * y % 2 + x * y % 3 == 0, lambda x, y: (x * y % 2 + x * y % 3) % 2 == 0,
            lambda x, y: ((x + y) % 2 + x * y % 3) % 2 == 0,
        ]
        t = tests[mask]
        for y in range(self.size):
            for x in range(self.size):
                if not self.fn[y][x] and t(x, y):
                    self.mod[y][x] = not self.mod[y][x]

    def penalty(self) -> int:
        s, m, result = self.size, self.mod, 0
        def runs(line):
            nonlocal result
            run, color, history = 0, False, [0] * 7
            def push(r):
                if history[0] == 0:
                    r += s
                history.pop()
                history.insert(0, r)
            def finder_like():
                n = history[1]
                core = n > 0 and history[2] == history[4] == history[5] == n and history[3] == n * 3
                return (1 if core and history[0] >= n * 4 and history[6] >= n else 0) + (1 if core and history[6] >= n * 4 and history[0] >= n else 0)
            for cell in line:
                if cell == color:
                    run += 1
                    if run == 5:
                        result += 3
                    elif run > 5:
                        result += 1
                else:
                    push(run)
                    if not color:
                        result += finder_like() * 40
                    color, run = cell, 1
            # terminate
            if color:
                push(run)
                run = 0
            run += s
            push(run)
            result += finder_like() * 40
        for y in range(s):
            runs(m[y])
        for x in range(s):
            runs([m[y][x] for y in range(s)])
        for y in range(s - 1):
            for x in range(s - 1):
                c = m[y][x]
                if c == m[y][x + 1] == m[y + 1][x] == m[y + 1][x + 1]:
                    result += 3
        dark = sum(sum(row) for row in m)
        total = s * s
        k = (abs(dark * 20 - total * 10) + total - 1) // total - 1
        return result + k * 10


def encode(text: str, mask: int | None = None) -> list[list[bool]]:
    """Return the QR module grid for text (True = dark)."""
    ver, data = _codewords(text.encode("utf-8"))
    best, best_score = None, None
    for msk in ([mask] if mask is not None else range(8)):
        grid = _Grid(ver)
        grid.draw_codewords(data)
        grid.apply_mask(msk)
        grid.draw_format(msk)
        score = grid.penalty()
        if best_score is None or score < best_score:
            best, best_score = grid, score
    return best.mod


def svg(text: str, alt: str = "", border: int = 4, mask: int | None = None) -> str:
    """A crisp SVG of the QR code, one unit per module, with a white quiet zone."""
    grid = encode(text, mask)
    n = len(grid) + border * 2
    cells = "".join(f"M{x + border},{y + border}h1v1h-1z" for y, row in enumerate(grid) for x, dark in enumerate(row) if dark)
    label = f' aria-label="{alt}"' if alt else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" width="900" height="900" role="img"{label} shape-rendering="crispEdges">'
            f'<rect width="{n}" height="{n}" fill="#ffffff"/><path d="{cells}" fill="#000000"/></svg>\n')
