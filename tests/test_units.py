from pytest import fixture, mark, raises, skip

import use



watnu = use(use.Path("../src/main.py"))

def test_config():
   assert watnu.config