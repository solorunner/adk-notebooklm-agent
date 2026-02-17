"""NotebookLM agent tools — re-exports all tool functions."""

from .auth import check_auth, start_auth, check_auth_token, import_cookies
from .notebooks import (
    list_notebooks,
    create_notebook,
    get_notebook,
    rename_notebook,
    delete_notebook,
    query_notebook,
)
from .sources import (
    list_sources,
    add_source_url,
    add_source_file,
    add_source_text,
    get_source,
    describe_source,
    delete_source,
)
from .notes import (
    list_notes,
    create_note,
    update_note,
    delete_note,
)
from .studio import (
    create_audio,
    create_video,
    create_mindmap,
    create_infographic,
    create_slides,
    create_data_table,
    create_report,
    create_quiz,
    create_flashcards,
    studio_status,
    delete_artifact,
)
from .download import download_artifact
from .sharing import (
    share_status,
    share_public,
    share_private,
    share_invite,
)
from .research import (
    start_research,
    research_status,
    import_research,
)

ALL_TOOLS = [
    check_auth,
    start_auth,
    check_auth_token,
    import_cookies,
    list_notebooks,
    create_notebook,
    get_notebook,
    rename_notebook,
    delete_notebook,
    query_notebook,
    list_sources,
    add_source_url,
    add_source_file,
    add_source_text,
    get_source,
    describe_source,
    delete_source,
    list_notes,
    create_note,
    update_note,
    delete_note,
    create_audio,
    create_video,
    create_mindmap,
    create_infographic,
    create_slides,
    create_data_table,
    create_report,
    create_quiz,
    create_flashcards,
    studio_status,
    delete_artifact,
    download_artifact,
    share_status,
    share_public,
    share_private,
    share_invite,
    start_research,
    research_status,
    import_research,
]
