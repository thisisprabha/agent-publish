"""Tests for OKLch color generation."""


import pytest

from agent_publish.oklch import (
    generate_css,
    generate_palette,
    list_directions,
    oklch_to_srgb,
    rgb_to_oklch,
)

# ---------------------------------------------------------------------------
# Round-trip
# ---------------------------------------------------------------------------


def test_srgb_round_trip_base_colors():
    """RGB → OKLch → hex should land within a small tolerance."""
    test_colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (128, 128, 128),
        (200, 100, 50),
    ]
    for r, g, b in test_colors:
        L, C, H = rgb_to_oklch(r, g, b)
        hex_out = oklch_to_srgb(L, C, H)
        # strip # and parse back to check distance
        assert hex_out.startswith("#")
        hex_val = int(hex_out[1:], 16)
        ro = (hex_val >> 16) & 0xFF
        go = (hex_val >> 8) & 0xFF
        bo = hex_val & 0xFF
        tol = 5
        assert abs(ro - r) <= tol, f"R mismatch for ({r},{g},{b}): got {ro}"
        assert abs(go - g) <= tol, f"G mismatch for ({r},{g},{b}): got {go}"
        assert abs(bo - b) <= tol, f"B mismatch for ({r},{g},{b}): got {bo}"


def test_oklch_handles_low_lightness():
    """Near-black should produce #000000 or very close."""
    hex_out = oklch_to_srgb(0.0, 0.0, 0)
    assert hex_out == "#000000"


def test_oklch_handles_high_lightness():
    """Near-white should produce #ffffff or very close."""
    hex_out = oklch_to_srgb(1.0, 0.0, 0)
    assert hex_out == "#ffffff"


# ---------------------------------------------------------------------------
# Palette generation
# ---------------------------------------------------------------------------


def test_all_directions_generate_palette():
    """Every known direction produces light + dark dicts with 9 keys each."""
    for direction in list_directions():
        palette = generate_palette(direction)
        assert "light" in palette
        assert "dark" in palette
        for mode in ("light", "dark"):
            assert set(palette[mode]) == {
                "bg", "fg", "muted", "accent", "accent-2", "border", "surface", "code-bg"
            }
            for hex_val in palette[mode].values():
                assert hex_val.startswith("#")
                assert len(hex_val) == 7


def test_directions_are_known():
    """list_directions returns the 5 expected directions."""
    assert list_directions() == [
        "editorial",
        "modern-minimal",
        "warm-soft",
        "tech-utility",
        "brutalist",
    ]


def test_unknown_direction_raises():
    """generate_palette raises ValueError for unknown directions."""
    with pytest.raises(ValueError, match="Unknown direction"):
        generate_palette("not-a-direction")


# ---------------------------------------------------------------------------
# CSS generation
# ---------------------------------------------------------------------------


def test_generate_css_contains_root_vars():
    """CSS output must include :root variables and dark media query."""
    css = generate_css("editorial")
    assert css.startswith(":root{")
    assert "--bg:" in css
    assert "@media (prefers-color-scheme:dark)" in css
    assert "body{" in css


def test_generate_css_each_direction():
    """All directions produce non-empty CSS."""
    for direction in list_directions():
        css = generate_css(direction)
        assert len(css) > 500
        assert "--bg:" in css


# ---------------------------------------------------------------------------
# Dark-mode inversion sanity checks
# ---------------------------------------------------------------------------


def test_dark_lightness_is_inverted():
    """For a light background, dark bg should be dark."""
    palette = generate_palette("modern-minimal")
    dark_bg_hex = palette["dark"]["bg"]
    # dark bg should be near-black
    dark_val = int(dark_bg_hex[1:], 16)
    assert dark_val < 0x222222, f"Expected dark bg, got {dark_bg_hex}"
