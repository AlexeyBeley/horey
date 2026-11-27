import os
import re
import cffi

ffi = cffi.FFI()

lib_dir = os.path.dirname(__file__)
so_path = os.path.join(lib_dir, "libmain.so")
h_path = os.path.join(lib_dir, "libmain.h")

# Read generated header
with open(h_path, "r") as f:
    content = f.read()

cdef_lines = [
    "typedef signed long long GoInt;",
    "typedef unsigned long long GoUint;",
    "typedef float GoFloat32;",
    "typedef double GoFloat64;",
]

# 2. Extract ONLY clean single-line 'extern ...;' function declarations
# (This skips `extern "C" {` and Go internal helpers)
extern_matches = re.findall(r"^extern\s+((?:Go\w+|int|char|void|\w+\s*\*)\s+\w+\([^\);]*\));", content, re.MULTILINE)

for decl in extern_matches:
    if not decl.startswith("_Go"):  # Skip Go internal string/slice helpers
        cdef_lines.append(f"extern {decl};")

clean_cdef = "\n".join(cdef_lines)

# Pass to CFFI

ffi.cdef(clean_cdef)

# Load the library
go_lib = ffi.dlopen(so_path)

# --- Call functions directly with AUTOMATIC typing ---

# Integers: Works directly without casting
result = go_lib.Add(15, 27)
print(f"Add Result: {result}")

name_bytes = "Horey".encode("utf-8")  # or simply b"Horey"
result_ptr = go_lib.Greet(name_bytes)

# Convert C char* response back to Python str
result_str = ffi.string(result_ptr).decode("utf-8")
print(result_str)
