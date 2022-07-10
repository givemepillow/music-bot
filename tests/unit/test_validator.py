import pytest

from app.core.tools.validator import validate_link


@pytest.mark.parametrize(
    "link, expected_result",
    [
        ('https://vk.com/id1', True),
        ('http://vk.com/id1', True),
        ('vk.com/id1', True),
        ('id1', True),
        ('vk.com', False),
        ('vk.com/', False),
        ('google.com', False),
        ('google.com/lilnikky', False),
        ('hi.there', True)
    ]
)
@pytest.mark.asyncio
async def test_validate_link(link, expected_result):
    result = await validate_link(link)
    assert result == expected_result
