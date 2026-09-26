"""RED→GREEN: internal ArticleDraft (D-06) — title/dek/body only."""


def test_article_draft_constructs_article_fields_only() -> None:
    from data_collection.dto.article_draft import ArticleDraft

    draft = ArticleDraft(
        title="RAG for audit",
        dek="Как искать по регламентам СВА.",
        body_markdown="# Intro\n\nBody",
    )
    assert draft.title == "RAG for audit"
    assert draft.dek == "Как искать по регламентам СВА."
    assert draft.body_markdown == "# Intro\n\nBody"
    assert set(ArticleDraft.model_fields) == {"title", "dek", "body_markdown"}
