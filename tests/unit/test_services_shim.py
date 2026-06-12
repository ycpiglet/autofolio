"""app/services 도메인 모듈 임포트 계약 검증.

각 서비스 모듈의 __all__ 에 선언된 모든 이름이 app.ui.backend 의 동일 객체를
가리키는지(identity test), 그리고 backend 의 모든 공개 함수·상수가 정확히
하나의 서비스 모듈 __all__ 에 포함되는지(completeness test)를 파생적으로
검증한다. 목록을 하드코딩하지 않으므로 backend 에 함수가 추가되거나 삭제되면
이 테스트가 자동으로 잡아낸다.
"""
from __future__ import annotations

import importlib
import inspect

import pytest

import app.ui.backend as backend

# 검사 대상 서비스 모듈 이름 목록
_SERVICE_MODULES = [
    "app.services.context",
    "app.services.system",
    "app.services.portfolio",
    "app.services.market",
    "app.services.trading",
    "app.services.analysis",
    "app.services.alerts",
]


def _load_services() -> list[object]:
    return [importlib.import_module(name) for name in _SERVICE_MODULES]


# ---------------------------------------------------------------------------
# Identity test — every name in each module's __all__ must be the same object
# as the corresponding name in backend.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("module_name", _SERVICE_MODULES)
def test_services_all_identity(module_name: str) -> None:
    """For every name in module.__all__ that also exists in backend, assert it is the same object.

    Service-native names (not present in backend) are intentionally skipped — they represent
    new service-layer abstractions that have no backend counterpart yet.
    """
    module = importlib.import_module(module_name)
    assert hasattr(module, "__all__"), f"{module_name} is missing __all__"
    for name in module.__all__:
        if not hasattr(backend, name):
            # Service-native symbol — not a backend re-export; identity check not applicable.
            continue
        assert getattr(module, name) is getattr(backend, name), (
            f"{module_name}.{name} is not the same object as backend.{name}"
        )


# ---------------------------------------------------------------------------
# Completeness test — every public function defined in backend, plus every
# public UPPER_CASE constant, must appear in exactly one service module's __all__.
# ---------------------------------------------------------------------------

def _backend_public_functions() -> set[str]:
    """Top-level functions whose __module__ is app.ui.backend (not underscore-prefixed)."""
    return {
        name
        for name, obj in inspect.getmembers(backend, inspect.isfunction)
        if obj.__module__ == "app.ui.backend" and not name.startswith("_")
    }


def _backend_public_constants() -> set[str]:
    """Module-level UPPER_CASE names (no leading underscore) that are not functions/classes/modules."""
    return {
        name
        for name in vars(backend)
        if name.isupper()
        and not name.startswith("_")
        and not inspect.isfunction(getattr(backend, name))
        and not inspect.isclass(getattr(backend, name))
        and not inspect.ismodule(getattr(backend, name))
    }


def test_services_completeness_no_orphans() -> None:
    """Every public backend function and UPPER_CASE constant appears in at least one
    service module's __all__ (no forgotten exports)."""
    services = _load_services()
    all_exported: set[str] = set()
    for mod in services:
        all_exported.update(getattr(mod, "__all__", []))

    expected = _backend_public_functions() | _backend_public_constants()
    missing = expected - all_exported
    assert not missing, (
        "The following backend public names are not exported by any services module "
        f"(add them to the appropriate __all__):\n  " + "\n  ".join(sorted(missing))
    )


def test_services_completeness_no_duplicates() -> None:
    """No name appears in more than one service module's __all__ (avoids split ownership)."""
    services = _load_services()
    seen: dict[str, str] = {}
    duplicates: dict[str, list[str]] = {}
    for mod in services:
        for name in getattr(mod, "__all__", []):
            if name in seen:
                duplicates.setdefault(name, [seen[name]]).append(mod.__name__)
            else:
                seen[name] = mod.__name__
    assert not duplicates, (
        "The following names appear in multiple service modules' __all__:\n  "
        + "\n  ".join(f"{k}: {v}" for k, v in sorted(duplicates.items()))
    )
