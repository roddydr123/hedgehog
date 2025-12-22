import numpy as np
import trimesh
import re


def stl_same_geometry(path_a: str, path_b: str, tol: float = 1e-6) -> bool:
    """
    Returns True if two STL files contain the same geometry, ignoring
    triangle ordering and floating-point noise.
    """

    mesh_a = trimesh.load_mesh(path_a)
    mesh_b = trimesh.load_mesh(path_b)

    # Ensure triangular (STL normally is)
    if not mesh_a.is_watertight:
        mesh_a = mesh_a.copy()
    if not mesh_b.is_watertight:
        mesh_b = mesh_b.copy()

    tris_a = mesh_a.triangles  # (N, 3, 3)
    tris_b = mesh_b.triangles  # (M, 3, 3)

    if tris_a.shape[0] != tris_b.shape[0]:
        return False

    def normalize(triangles):
        # sort vertices within each triangle
        sorted_verts = np.sort(triangles, axis=1)

        # quantize using tolerance to avoid FP noise
        quantized = np.round(sorted_verts / tol).astype(np.int64)

        # flatten to hashable rows
        return quantized.reshape(-1, 9)

    fa = normalize(tris_a)
    fb = normalize(tris_b)

    return set(map(tuple, fa)) == set(map(tuple, fb))


def util_test_files_identical_line_by_line(filea, fileb):
    with open(filea, "r") as a, open(fileb, "r") as b:
        for line_num, (la, lb) in enumerate(zip(a, b), start=1):
            assert la == lb, f"Mismatch on line {line_num}"

        # Check that neither file has extra lines
        assert list(a) == list(b) == []


def files_equal_to_3dp(file1, file2, ndp=3):
    """
    Compare two text files, treating all floating-point numbers
    as equal if they match when rounded to ndp decimal places.
    Returns True if equal, False otherwise.
    """

    float_re = re.compile(r"-?\d+\.\d+")

    def normalize(text):
        return float_re.sub(
            lambda m: f"{float(m.group()):.{ndp}f}",
            text
        )

    with open(file1, "r") as f:
        text1 = normalize(f.read())

    with open(file2, "r") as f:
        text2 = normalize(f.read())

    return text1 == text2
