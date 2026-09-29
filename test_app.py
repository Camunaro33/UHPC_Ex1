from streamlit.testing.v1 import AppTest
import bfup_ex1 as core

def test_course_values():
    r = core.ex1_compute()
    assert abs(r["mR0"] - 123.6) < 0.2 and abs(r["x"] - 65.3) < 0.1 and abs(r["mR1"] - 271.4) < 0.5
    assert abs(r["eps_c"] + 2.11) < 0.01
    assert abs(r["sls_c"]["x"] - 80.5) < 0.2 and abs(r["sls_c"]["m"] - 134) < 0.5

def test_app_runs():
    at = AppTest.from_file("app.py", default_timeout=60).run()
    assert not at.exception
    at.checkbox[0].check().run()
    assert not at.exception
