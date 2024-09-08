from streamlit.testing.v1 import AppTest

at = AppTest.from_file("templates/streamlit_basic/main.py")
at.run()
assert not at.exception
