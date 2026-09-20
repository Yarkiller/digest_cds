"""Live composition: construct Supabase clients only here (never in use-cases)."""

from __future__ import annotations

from backend.composition.container import AppContainer
from backend.composition.settings import Settings
from backend.tests_support.in_memory import InMemoryKnowledgeChunkRepository
from supabase_integration import (
    SupabaseIssueRepository,
    SupabaseMaterialRepository,
    SupabasePingRecorder,
    SupabaseProfileRepository,
    SupabaseVotingCycleReader,
    create_publishable_client,
    create_service_role_client,
)


def build_live_container(settings: Settings) -> AppContainer:
    """Wire service_role adapters for profiles, pings, issues, materials, cycles."""
    if not settings.supabase_url or not settings.supabase_secret_key:
        raise ValueError(
            "live container requires SUPABASE_URL and SUPABASE_SECRET_KEY "
            "(construct clients only in composition/live.py — never expose via VITE_)"
        )

    # service_role: RLS bypass for content reads + activity_events / profiles (T-02-03)
    admin_client = create_service_role_client(
        settings.supabase_url,
        settings.supabase_secret_key,
    )
    # optional publishable client kept for future user-scoped reads; constructed in composition only
    if settings.supabase_publishable_key:
        create_publishable_client(
            settings.supabase_url,
            settings.supabase_publishable_key,
        )

    return AppContainer(
        materials=SupabaseMaterialRepository(admin_client),
        chunks=InMemoryKnowledgeChunkRepository(),
        profiles=SupabaseProfileRepository(admin_client),
        pings=SupabasePingRecorder(admin_client),
        issues=SupabaseIssueRepository(admin_client),
        voting_cycles=SupabaseVotingCycleReader(admin_client),
    )
