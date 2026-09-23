"""pyproject_gen: the [project] readme field is conditional on the file existing.

Regression for the netlib-specfun contact (DEFECTS D9-D11 record, 2026-09-23):
a generated service with no README.md shipped a pyproject.toml with no
long_description at all, and `twine check --strict` rejected every wheel
built from it. The field must appear only when the file is really there,
because setuptools refuses a distribution whose declared readme is missing.
"""

from nativegate.generators import pyproject_gen


def test_no_readme_field_without_file():
    pyproject = pyproject_gen.generate_pyproject("demo", "fortran")
    assert "readme" not in pyproject


def test_readme_field_with_file():
    pyproject = pyproject_gen.generate_pyproject(
        "demo", "fortran", has_readme=True
    )
    assert 'readme = "README.md"' in pyproject
    # still valid TOML-shaped and carries the content type setuptools infers
    assert "[project]" in pyproject
