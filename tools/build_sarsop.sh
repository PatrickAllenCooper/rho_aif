#!/usr/bin/env bash
# Build the APPL SARSOP solver (pomdpsol) from source, with patches for
# modern compilers and Apple Silicon. Produces tools/sarsop/src/pomdpsol.
#
# Patches applied (upstream targets Linux/Cygwin with old gcc):
#   1. Drop -msse2/-mfpmath=sse (unsupported on arm64).
#   2. SparseCol iterators: libc++ vector iterators cannot be constructed
#      from raw pointers; use raw const pointers instead.
#   3. Fix chained-comparison asserts (0 <= c < n) rejected by clang.
#   4. Allow implicit function declarations in the old C parser sources.
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d sarsop ]; then
    git clone --depth 1 https://github.com/AdaCompNUS/sarsop.git
fi
cd sarsop/src

# 1. SSE flags
sed -i.bak 's/-msse2//g; s/-mfpmath=sse//g' Makefile
# 4. Implicit declarations in C89-era parser code
sed -i.bak2 's/^CFLAGS        = -g -w -O3/CFLAGS        = -g -w -O3 -Wno-implicit-function-declaration -Wno-error=implicit-function-declaration/' Makefile

# 2. SparseCol iterator type
sed -i.bak 's|typedef vector<SparseVector_Entry>::const_iterator iterator;|typedef const SparseVector_Entry* iterator;|' MathLib/SparseMatrix.h
python3 - <<'PY'
s = open("MathLib/SparseMatrix.cpp").read()
s = s.replace(
    "vector<SparseVector_Entry>::const_iterator col_start = data.begin() + cols_start[ci];",
    "const SparseVector_Entry* col_start = data.data() + cols_start[ci];",
).replace(
    "vector<SparseVector_Entry>::const_iterator col_end = data.begin() + colEnd(ci);",
    "const SparseVector_Entry* col_end = data.data() + colEnd(ci);",
)
open("MathLib/SparseMatrix.cpp", "w").write(s)

s = open("MathLib/MathLib.cpp").read()
s = s.replace(
    "vector<SparseVector_Entry>::const_iterator  Ai;\n\n\t\tvector<SparseVector_Entry>::iterator  ri;",
    "SparseCol::iterator  Ai;\n\n\t\tvector<SparseVector_Entry>::iterator  ri;",
)
s = s.replace(
    "vector<SparseVector_Entry>::const_iterator  Ai, col_end;",
    "SparseCol::iterator  Ai, col_end;",
)
open("MathLib/MathLib.cpp", "w").write(s)
PY

# 3. Chained comparison asserts
sed -i.bak2 's/assert( 0 <= \([a-z_]*\) < \([a-zA-Z0-9_()]*\) )/assert( 0 <= \1 \&\& \1 < \2 )/g' MathLib/MathLib.cpp

make pomdpsol
echo "Built: $(pwd)/pomdpsol"
