import use
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from pytest import fixture, mark, raises, skip

stay = use(
    use.URL("https://raw.githubusercontent.com/amogorkon/stay/master/src/stay/stay.py"),
    hash_algo=use.Hash.sha256,
    hash_value="47e11e8de6b07f24c95233fba1e7281c385b049f771f74c5647a837b51bd7ff4",
    import_as="stay",
)

q = use(use.Path("../src/q.py"))

first_start = use(use.Path("../src/first_start.py"))
config = use(use.Path("../src/config.py")).Config()


def test_config():
    assert config.first_start is True
