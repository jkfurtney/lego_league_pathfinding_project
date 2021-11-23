import jinja2

from pathlib import Path
template = Path('template.html').read_text()

cases = [
    ("(Round 1)", "round_123321_10.json"),
    ("(Round 2)", "round_123321_20.json"),
    ("(Round 3)", "round_123321_40.json"),
    ("(Round 4)", "round_123321_50.json"),
    ("(Round 5)", "round_123321_60.json")]

for name, datafile in cases:
    parameters = {"round": name, "datafile": datafile}
    new_file = jinja2.Environment().from_string(template).render(parameters)
    with open(datafile[:-5]+".html", "w") as f:
        print(new_file, file=f)
