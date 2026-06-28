from app.core.modules.catalog import CATEGORIES, MODULES, MODULE_BY_ID


def test_fifteen_modules():
    assert len(MODULES) == 15
    assert len(MODULE_BY_ID) == 15


def test_all_categories_reference_valid_modules():
    seen: set[str] = set()
    for _, ids in CATEGORIES:
        for mid in ids:
            assert mid in MODULE_BY_ID
            seen.add(mid)
    assert len(seen) == 15


def test_each_module_has_submodules():
    for mod in MODULES:
        assert len(mod.submodules) >= 3, mod.id
