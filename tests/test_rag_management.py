from pathlib import Path

import pytest

from agent import rag


class FakeCollection:
    def __init__(self):
        self.rows = {}

    def count(self):
        return len(self.rows)

    def delete(self, where):
        self.rows = {k: v for k, v in self.rows.items() if v[2].get("source") != where["source"]}

    def add(self, documents, ids, metadatas):
        for row in zip(ids, documents, metadatas):
            self.rows[row[0]] = row


@pytest.fixture
def isolated_rag(tmp_path, monkeypatch):
    docs = tmp_path / "docs"
    docs.mkdir()
    hashes = tmp_path / "hashes.json"
    collection = FakeCollection()
    monkeypatch.setattr(rag, "DOCS_DIR", docs)
    monkeypatch.setattr(rag, "UPLOAD_DIR", docs)
    monkeypatch.setattr(rag, "HASH_FILE", hashes)
    monkeypatch.setattr(rag, "_collection", collection)
    monkeypatch.setattr(rag, "_file_hashes", {})
    monkeypatch.setattr(rag, "get_collection", lambda: collection)
    return docs, collection


def test_txt_incremental_duplicate_update_delete(isolated_rag):
    docs, collection = isolated_rag
    source = docs.parent / "sample.txt"
    source.write_text("第一版知识。", encoding="utf-8")
    first = rag.index_document(source)
    assert first["duplicate"] is False
    assert collection.count() == 1
    second = rag.index_document(source)
    assert second["duplicate"] is True
    assert collection.count() == 1
    source.write_text("第二版知识。\n\n新增一段。", encoding="utf-8")
    rag.index_document(source)
    assert collection.count() == 2
    assert rag.delete_document("sample.txt") == 2
    assert (docs / "sample.txt").exists()


def test_reject_unsupported_document(tmp_path):
    source = tmp_path / "bad.exe"
    source.write_bytes(b"no")
    with pytest.raises(ValueError):
        rag.parse_document(source)


def test_parse_text_pdf(tmp_path):
    """生成一个极小文本 PDF，验证真实 pypdf 提取和页码。"""
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length 42 >>\nstream\nBT /F1 12 Tf 40 100 Td (RAG PDF TEST) Tj ET\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    data = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(data))
        data.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(data)
    data.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    data.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode())
    data.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    pdf = tmp_path / "sample.pdf"
    pdf.write_bytes(data)
    units = rag.parse_document(pdf)
    assert units == [{"text": "RAG PDF TEST", "page": 1}]


def test_search_validation():
    with pytest.raises(ValueError):
        rag.search_documents("")
    with pytest.raises(ValueError):
        rag.search_documents("x", top_k=0)
