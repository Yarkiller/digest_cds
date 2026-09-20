"""IssueRepository adapter — read digest_issues via injected service_role client."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from backend.domain.errors import PersistenceError
from backend.domain.issue import Issue, IssueItem


class _SupabaseClient(Protocol):
    def table(self, name: str) -> Any: ...


def _parse_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    text = str(value).replace("Z", "+00:00")
    return datetime.fromisoformat(text)


def _row_to_issue(row: dict[str, Any], items: tuple[IssueItem, ...]) -> Issue:
    return Issue(
        id=str(row["id"]),
        number=int(row["number"]),
        period_label=str(row["period_label"]),
        title=str(row["title"]),
        editor=None,
        published_at=_parse_dt(row["published_at"]),
        items=items,
    )


def _item_from_join(row: dict[str, Any]) -> IssueItem | None:
    material = row.get("materials")
    if not isinstance(material, dict):
        return None
    return IssueItem(
        slug=str(material["slug"]),
        title=str(material["title"]),
        position=int(row["position"]),
        format=str(material.get("format") or "статья"),
        reading_minutes=int(material.get("reading_minutes") or 0),
        dek=str(material["dek"]) if material.get("dek") else None,
    )


class SupabaseIssueRepository:
    """Read-only IssueRepository against digest_issues + items (service_role)."""

    def __init__(self, client: _SupabaseClient) -> None:
        self._client = client

    def get_latest_published(self) -> Issue | None:
        try:
            result = (
                self._client.table("digest_issues")
                .select("id,number,period_label,title,published_at")
                .not_.is_("published_at", "null")
                .order("published_at", desc=True)
                .limit(1)
                .execute()
            )
        except PersistenceError:
            raise
        except Exception as exc:  # noqa: BLE001 — map SDK failures at boundary
            raise PersistenceError(f"digest_issues get_latest_published failed: {exc}") from exc

        rows = getattr(result, "data", None) or []
        if not rows:
            return None
        return self._with_items(rows[0])

    def get_by_number(self, number: int) -> Issue | None:
        try:
            result = (
                self._client.table("digest_issues")
                .select("id,number,period_label,title,published_at")
                .eq("number", number)
                .not_.is_("published_at", "null")
                .limit(1)
                .execute()
            )
        except PersistenceError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise PersistenceError(f"digest_issues get_by_number failed: {exc}") from exc

        rows = getattr(result, "data", None) or []
        if not rows:
            return None
        return self._with_items(rows[0])

    def list_past_published(self) -> list[Issue]:
        current = self.get_latest_published()
        try:
            result = (
                self._client.table("digest_issues")
                .select("id,number,period_label,title,published_at")
                .not_.is_("published_at", "null")
                .order("published_at", desc=True)
                .execute()
            )
        except PersistenceError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise PersistenceError(f"digest_issues list_past_published failed: {exc}") from exc

        rows = getattr(result, "data", None) or []
        if current is not None:
            rows = [r for r in rows if str(r["id"]) != current.id]
        return [self._with_items(row) for row in rows]

    def _with_items(self, row: dict[str, Any]) -> Issue:
        issue_id = row["id"]
        try:
            items_result = (
                self._client.table("digest_issue_items")
                .select(
                    "position,material_id,"
                    "materials(slug,title,format,reading_minutes,dek)"
                )
                .eq("issue_id", issue_id)
                .order("position")
                .execute()
            )
        except PersistenceError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise PersistenceError(f"digest_issue_items load failed: {exc}") from exc

        item_rows = getattr(items_result, "data", None) or []
        items: list[IssueItem] = []
        for item_row in sorted(item_rows, key=lambda r: int(r.get("position") or 0)):
            parsed = _item_from_join(item_row)
            if parsed is not None:
                items.append(parsed)
        return _row_to_issue(row, tuple(items))
