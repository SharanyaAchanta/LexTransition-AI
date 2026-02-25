from __future__ import annotations

import argparse
import json
import sys
import os
import logging
logger = logging.getLogger(__name__)

from engine.mapping_logic import map_ipc_to_bns
from engine.bookmark_manager import (
    add_bookmark,
    view_bookmarks,
    edit_bookmark,
    delete_bookmark,
)
from engine.db import (
    import_mappings_from_csv,
    import_mappings_from_excel,
)
from engine.history_manager import (
    add_history,
    view_history,
    clear_history,
)

def _cmd_map(args: argparse.Namespace) -> int:
    result = map_ipc_to_bns(args.ipc_section)
    add_history(args.ipc_section, result)
    if not result:
        logger.info("No mapping found")
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _cmd_import(args: argparse.Namespace) -> int:
    if args.file.lower().endswith(".csv"):
        success_count, errors = import_mappings_from_csv(args.file)
    elif args.file.lower().endswith(".xlsx"):
        success_count, errors = import_mappings_from_excel(args.file)
    else:
        print("Only .csv or .xlsx files are supported")
        return 2
    print(json.dumps({"success_count": success_count, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if success_count > 0 and not errors else (1 if success_count > 0 else 2)


def _cmd_search(args: argparse.Namespace) -> int:
    from engine.rag_engine import index_pdfs, search_pdfs

    index_pdfs(args.dir)
    result = search_pdfs(args.query, top_k=args.top_k)
    if not result:
        print("No grounded citation found")
        return 1
    print(result)
    return 0


def _cmd_diagnostics(_: argparse.Namespace) -> int:
    diagnostics = {
        "use_embeddings": os.environ.get("LTA_USE_EMBEDDINGS", "0"),
        "ollama_url_set": bool(os.environ.get("LTA_OLLAMA_URL")),
        "mapping_db_override": os.environ.get("LTA_MAPPING_DB", ""),
    }
    print(json.dumps(diagnostics, ensure_ascii=False, indent=2))
    return 0
def _cmd_bookmark_add(args: argparse.Namespace) -> int:
    add_bookmark(args.section, args.title, args.notes)
    return 0


def _cmd_bookmark_list(_: argparse.Namespace) -> int:
    view_bookmarks()
    return 0


def _cmd_bookmark_edit(args: argparse.Namespace) -> int:
    edit_bookmark(args.id, args.notes)
    return 0


def _cmd_bookmark_delete(args: argparse.Namespace) -> int:
    delete_bookmark(args.id)
    return 0


def _cmd_history_list(_: argparse.Namespace) -> int:
    view_history()
    return 0


def _cmd_history_clear(_: argparse.Namespace) -> int:
    clear_history()
    return 0
  
def _cmd_bookmark_delete(args: argparse.Namespace) -> int:
    delete_bookmark(args.id)
    return 0



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LexTransition-AI CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    map_cmd = sub.add_parser("map", help="Map IPC section to BNS")
    map_cmd.add_argument("ipc_section")
    map_cmd.set_defaults(func=_cmd_map)

    import_cmd = sub.add_parser("import", help="Import mappings from CSV/Excel")
    import_cmd.add_argument("--file", required=True)
    import_cmd.set_defaults(func=_cmd_import)

    search_cmd = sub.add_parser("search", help="Search grounded citations in PDFs")
    search_cmd.add_argument("--query", required=True)
    search_cmd.add_argument("--dir", default="law_pdfs")
    search_cmd.add_argument("--top-k", type=int, default=3)
    search_cmd.set_defaults(func=_cmd_search)

    diag_cmd = sub.add_parser("diagnostics", help="Show runtime diagnostics")
    diag_cmd.set_defaults(func=_cmd_diagnostics)

    history_list = sub.add_parser("history-list", help="View search history")
    history_list.set_defaults(func=_cmd_history_list)

    history_clear = sub.add_parser("history-clear", help="Clear search history")
    history_clear.set_defaults(func=_cmd_history_clear)

        # Bookmark Commands
    bookmark_add = sub.add_parser("bookmark-add", help="Add a bookmark with notes")
    bookmark_add.add_argument("--section", required=True)
    bookmark_add.add_argument("--title", required=True)
    bookmark_add.add_argument("--notes", default="")
    bookmark_add.set_defaults(func=_cmd_bookmark_add)

    bookmark_list = sub.add_parser("bookmark-list", help="List all bookmarks")
    bookmark_list.set_defaults(func=_cmd_bookmark_list)

    bookmark_edit = sub.add_parser("bookmark-edit", help="Edit bookmark notes")
    bookmark_edit.add_argument("--id", required=True)
    bookmark_edit.add_argument("--notes", required=True)
    bookmark_edit.set_defaults(func=_cmd_bookmark_edit)

    bookmark_delete = sub.add_parser("bookmark-delete", help="Delete a bookmark")
    bookmark_delete.add_argument("--id", required=True)
    bookmark_delete.set_defaults(func=_cmd_bookmark_delete)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
