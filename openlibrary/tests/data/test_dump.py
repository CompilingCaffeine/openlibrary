import json
import string

import pytest

from openlibrary.data.dump import pgdecode, print_dump


class TestPrintDump:
    def test_fixes_prefixes(self, capsys):
        records = [
            {
                "key": "/b/OL1M",
                "type": {"key": "/type/edition"},
                "revision": 1,
                "last_modified": {"value": "2019-01-01T00:00:00.000"},
            },
        ]

        print_dump(map(json.dumps, records))
        assert capsys.readouterr().out.strip() == "\t".join(
            [
                "/type/edition",
                "/books/OL1M",
                "1",
                "2019-01-01T00:00:00.000",
                json.dumps(
                    {
                        "key": "/books/OL1M",
                        "type": {"key": "/type/edition"},
                        "revision": 1,
                        "last_modified": {"value": "2019-01-01T00:00:00.000"},
                    }
                ),
            ]
        )

    @pytest.mark.parametrize(
        ("key", "type_key", "authors", "expected"),
        [
            (
                "/works/OL1W",
                "/type/work",
                [
                    {"author": {"key": "/authors/OL2A"}, "role": "editor"},
                    {"type": {"key": "/type/author_role"}},
                    {"author": {}},
                    {"author": {"key": "/authors/OL1A"}},
                ],
                [{"author": {"key": "/authors/OL2A"}, "role": "editor"}, {"author": {"key": "/authors/OL1A"}}],
            ),
            ("/works/OL1W", "/type/work", [{"type": {"key": "/type/author_role"}}], []),
            ("/books/OL1M", "/type/edition", [{"key": "/authors/OL1A"}], [{"key": "/authors/OL1A"}]),
        ],
    )
    def test_exported_authors(self, capsys, key, type_key, authors, expected):
        record = {
            "key": key,
            "type": {"key": type_key},
            "authors": authors,
            "revision": 1,
            "last_modified": {"value": "2019-01-01T00:00:00.000"},
        }
        print_dump([json.dumps(record)])
        document = json.loads(capsys.readouterr().out.split("\t", 4)[4])
        assert document["authors"] == expected

    def test_excludes_sensitive_pages(self, capsys):
        records = [
            {"key": "/people/foo"},
            {"key": "/user/foo"},
            {"key": "/admin/foo"},
        ]
        print_dump(map(json.dumps, records))
        assert capsys.readouterr().out == ""

    def test_excludes_obsolete_pages(self, capsys):
        records = [
            {"key": "/scan_record/foo"},
            {"key": "/old/what"},
        ]

        print_dump(map(json.dumps, records))
        assert capsys.readouterr().out == ""


class TestPgDecode:
    def test_pgdecode_substitute(self):
        assert pgdecode(r"\n\r\t\\") == "\n\r\t\\"

    def test_pgdecode_ascii_printable(self):

        assert pgdecode(string.printable) == string.printable
