"""
Dataclasses for BREP analytical surface primitives and material information.

BREP primitives represent the analytical surfaces extracted from STEP files
when using `include_brep=True` in `step_to_glb()`.

Material dataclasses represent the physical and visual material properties
extracted when using `include_materials=True` in `step_to_glb()`.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union


@dataclass(frozen=True)
class Plane:
    """A planar surface."""

    # Index of this face in the BREP shape
    face_index: int
    # Extent in local X direction (meters)
    extent_x: Tuple[float, float]
    # Extent in local Y direction (meters)
    extent_y: Tuple[float, float]
    # A point on the plane
    origin: Tuple[float, float, float]
    # Unit normal vector
    normal: Tuple[float, float, float]
    # Unit X direction in the plane
    x_dir: Tuple[float, float, float]


@dataclass(frozen=True)
class Cylinder:
    """A cylindrical surface."""

    # Index of this face in the BREP shape
    face_index: int
    # Angular extent around axis (radians)
    extent_angle: Tuple[float, float]
    # Height extent along axis (meters)
    extent_height: Tuple[float, float]
    # Point on axis
    origin: Tuple[float, float, float]
    # Unit axis direction
    axis: Tuple[float, float, float]
    # Cylinder radius in meters
    radius: float


@dataclass(frozen=True)
class Cone:
    """A conical surface."""

    # Index of this face in the BREP shape
    face_index: int
    # Angular extent around axis (radians)
    extent_angle: Tuple[float, float]
    # Distance extent from apex (meters)
    extent_distance: Tuple[float, float]
    # Apex point of the cone
    apex: Tuple[float, float, float]
    # Unit axis direction from apex
    axis: Tuple[float, float, float]
    # Semi-angle at apex in radians
    semi_angle: float
    # Reference radius at the origin plane in meters
    ref_radius: float


@dataclass(frozen=True)
class Sphere:
    """A spherical surface."""

    # Index of this face in the BREP shape
    face_index: int
    # Longitude extent (radians)
    extent_longitude: Tuple[float, float]
    # Latitude extent (radians)
    extent_latitude: Tuple[float, float]
    # Center point
    center: Tuple[float, float, float]
    # Sphere radius in meters
    radius: float


@dataclass(frozen=True)
class Torus:
    """A toroidal surface."""

    # Index of this face in the BREP shape
    face_index: int
    # Angle extent around main axis (radians)
    extent_major_angle: Tuple[float, float]
    # Angle extent around tube (radians)
    extent_minor_angle: Tuple[float, float]
    # Center point
    center: Tuple[float, float, float]
    # Unit axis direction (normal to torus plane)
    axis: Tuple[float, float, float]
    # Distance from center to tube center in meters
    major_radius: float
    # Tube radius in meters
    minor_radius: float


# Union type for any primitive
BrepPrimitive = Union[Plane, Cylinder, Cone, Sphere, Torus]


# ============================================================================
# Material Dataclasses
# ============================================================================


@dataclass(frozen=True)
class PbrProperties:
    """PBR (physically-based rendering) material properties."""

    # Base color as RGBA, values 0-1
    base_color: Tuple[float, float, float, float]
    # Metallic factor 0-1
    metallic: float
    # Roughness factor 0-1
    roughness: float
    # Index of refraction
    refraction_index: float
    # Emissive factor as RGB
    emissive_factor: Tuple[float, float, float]


@dataclass(frozen=True)
class CommonProperties:
    """Legacy (Phong) material properties."""

    ambient_color: Tuple[float, float, float]
    diffuse_color: Tuple[float, float, float]
    specular_color: Tuple[float, float, float]
    emissive_color: Tuple[float, float, float]
    # Specular exponent
    shininess: float
    # 0 = fully opaque, 1 = fully transparent
    transparency: float


@dataclass(frozen=True)
class PhysicalMaterial:
    """Physical material properties (name, density) from STEP AP214 material data."""

    name: Optional[str]
    description: Optional[str]
    # Density as stored in the STEP file (typically g/mm³)
    density: Optional[float]
    density_name: Optional[str]
    density_value_type: Optional[str]


@dataclass(frozen=True)
class VisualMaterial:
    """Visual material properties (colors, PBR) from STEP visual material data."""

    name: Optional[str]
    # Base color as RGBA, values 0-1
    base_color: Tuple[float, float, float, float]
    # Alpha cutoff threshold
    alpha_cutoff: float
    # PBR properties, if present
    pbr: Optional[PbrProperties]
    # Legacy Phong properties, if present
    common: Optional[CommonProperties]


# Union type for any material
Material = Union[PhysicalMaterial, VisualMaterial]

__all__ = [
    "Plane",
    "Cylinder",
    "Cone",
    "Sphere",
    "Torus",
    "BrepPrimitive",
    "PbrProperties",
    "CommonProperties",
    "PhysicalMaterial",
    "VisualMaterial",
    "Material",
    "parse_primitive",
    "parse_brep_faces",
    "parse_material",
    "parse_materials",
]


def parse_primitive(data: dict, face_index: int = 0) -> Optional[BrepPrimitive]:
    """
    Parse a primitive dict from GLTF extension into a typed dataclass.

    Parameters
    ----------
    data : dict or None
        A single primitive dict from the TM_brep_faces extension,
        or None if the face was filtered out
    face_index : int
        The index of this face in the faces array (used as fallback
        if face_index is not in the data)

    Returns
    -------
    BrepPrimitive or None
        The parsed primitive, or None if type is not recognized or data is None.
    """
    if data is None:
        return None

    ptype = data.get("type")
    if ptype is None:
        return None

    # Use face_index from data if present, otherwise use parameter
    idx = data.get("face_index", face_index)

    if ptype == "plane":
        return Plane(
            face_index=idx,
            extent_x=tuple(data["extent_x"]),
            extent_y=tuple(data["extent_y"]),
            origin=tuple(data["origin"]),
            normal=tuple(data["normal"]),
            x_dir=tuple(data["x_dir"]),
        )
    elif ptype == "cylinder":
        return Cylinder(
            face_index=idx,
            extent_angle=tuple(data["extent_angle"]),
            extent_height=tuple(data["extent_height"]),
            origin=tuple(data["origin"]),
            axis=tuple(data["axis"]),
            radius=data["radius"],
        )
    elif ptype == "cone":
        return Cone(
            face_index=idx,
            extent_angle=tuple(data["extent_angle"]),
            extent_distance=tuple(data["extent_distance"]),
            apex=tuple(data["apex"]),
            axis=tuple(data["axis"]),
            semi_angle=data["semi_angle"],
            ref_radius=data["ref_radius"],
        )
    elif ptype == "sphere":
        return Sphere(
            face_index=idx,
            extent_longitude=tuple(data["extent_longitude"]),
            extent_latitude=tuple(data["extent_latitude"]),
            center=tuple(data["center"]),
            radius=data["radius"],
        )
    elif ptype == "torus":
        return Torus(
            face_index=idx,
            extent_major_angle=tuple(data["extent_major_angle"]),
            extent_minor_angle=tuple(data["extent_minor_angle"]),
            center=tuple(data["center"]),
            axis=tuple(data["axis"]),
            major_radius=data["major_radius"],
            minor_radius=data["minor_radius"],
        )

    return None


def parse_brep_faces(brep_faces: List[dict]) -> List[Optional[BrepPrimitive]]:
    """
    Parse all brep_faces from mesh metadata into typed dataclasses.

    Parameters
    ----------
    brep_faces : list of dict
        The faces list from the TM_brep_faces extension

    Returns
    -------
    list of BrepPrimitive or None
        List of parsed primitives, with None for non-analytical faces.
        Maintains the same indexing as the input list.
    """
    return [parse_primitive(face, face_index=i) for i, face in enumerate(brep_faces)]


def parse_material(data: Optional[Dict]) -> Optional[Material]:
    """
    Parse a single material dict from GLB metadata into a typed dataclass.

    Discriminates between PhysicalMaterial (has ``density`` key) and
    VisualMaterial (has ``base_color`` key).  Returns ``None`` for
    unrecognised or empty entries so callers can use the same index-safe
    pattern as :func:`parse_brep_faces`.

    Parameters
    ----------
    data : dict or None
        A single entry from ``mesh.metadata["cascadio"]["materials"]``.

    Returns
    -------
    PhysicalMaterial, VisualMaterial, or None
    """
    if not data:
        return None

    # Physical material: has density or is clearly a physical entry
    if "density" in data or ("name" in data and "base_color" not in data):
        return PhysicalMaterial(
            name=data.get("name"),
            description=data.get("description"),
            density=data.get("density"),
            density_name=data.get("density_name"),
            density_value_type=data.get("density_value_type"),
        )

    # Visual material: has base_color
    if "base_color" in data:
        pbr = None
        if "pbr" in data:
            p = data["pbr"]
            pbr = PbrProperties(
                base_color=tuple(p["base_color"]),
                metallic=p["metallic"],
                roughness=p["roughness"],
                refraction_index=p["refraction_index"],
                emissive_factor=tuple(p["emissive_factor"]),
            )

        common = None
        if "common" in data:
            c = data["common"]
            common = CommonProperties(
                ambient_color=tuple(c["ambient_color"]),
                diffuse_color=tuple(c["diffuse_color"]),
                specular_color=tuple(c["specular_color"]),
                emissive_color=tuple(c["emissive_color"]),
                shininess=c["shininess"],
                transparency=c["transparency"],
            )

        return VisualMaterial(
            name=data.get("name"),
            base_color=tuple(data["base_color"]),
            alpha_cutoff=data.get("alpha_cutoff", 0.5),
            pbr=pbr,
            common=common,
        )

    return None


def parse_materials(materials: List[Optional[Dict]]) -> List[Optional[Material]]:
    """
    Parse all material dicts from GLB metadata into typed dataclasses.

    Parameters
    ----------
    materials : list of dict
        The ``materials`` list from ``mesh.metadata["cascadio"]``.

    Returns
    -------
    list of Material or None
        Parsed materials in the same order as the input list.
        Entries that cannot be parsed are ``None``.
    """
    return [parse_material(m) for m in materials]

