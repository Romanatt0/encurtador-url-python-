from utils.short_code import generate_short_id, ALPHABET, SHORT_ID_LENGTH


class TestGenerateShortId:
    def test_default_length(self):
        result = generate_short_id()
        assert len(result) == SHORT_ID_LENGTH

    def test_custom_length(self):
        result = generate_short_id(12)
        assert len(result) == 12

    def test_uses_valid_characters(self):
        result = generate_short_id()
        for char in result:
            assert char in ALPHABET

    def test_generates_different_ids(self):
        ids = {generate_short_id() for _ in range(100)}
        assert len(ids) == 100
