import pytest
from faker import Faker

from uc.converter import Quantity


def test_linear_forward_and_inverse(unit_registry):
    faker = Faker()

    for _ in range(10):
        meters = faker.pyfloat(left_digits=2, right_digits=3, positive=True)
        print(f'{meters=}')

        m_init = Quantity(meters, "m")
        mm = unit_registry.convert(m_init, "mm")
        m_back = unit_registry.convert(mm, "m")
        assert m_back.value == pytest.approx(meters, rel=1e-12)
