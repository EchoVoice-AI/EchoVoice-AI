from app.store import MemoryStore


def test_memory_store_set_get_delete():
    store = MemoryStore()

    # set and get
    store.set("foo", 123)
    assert store.get("foo") == 123

    # default for missing
    assert store.get("missing", "def") == "def"

    # delete
    store.delete("foo")
    assert store.get("foo") is None
