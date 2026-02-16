"""Quick start: protect and restore in a few lines."""
from private_layer import protect, restore

def main():
    text = "Contact Jane at jane@example.com or +1 555 123 4567."
    result = protect(text)
    print("Masked:", result.masked_text)
    print("Mapping entries:", len(result.mapping))
    for e in result.mapping:
        print(f"  {e.placeholder} -> {e.label}")

    original = restore(result.masked_text, result.mapping)
    print("Restored:", original)
    assert original == text

if __name__ == "__main__":
    main()
