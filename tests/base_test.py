import pytest
import selenium


class AbstractBaseTest:
    @pytest.mark.skip(reason="Abstract base test method")
    def test_base_method(self):
        assert True
