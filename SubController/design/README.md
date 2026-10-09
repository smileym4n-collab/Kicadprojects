# Current design: revision B, final schematic review

Use **[final-review/ENGINEERING-REVIEW.md](final-review/ENGINEERING-REVIEW.md)**, **[final-review/schematic.pdf](final-review/schematic.pdf)**, **[final-review/BOM.md](final-review/BOM.md)** and **[FIRMWARE-REQUIREMENTS.md](FIRMWARE-REQUIREMENTS.md)**.

The live root `.kicad_sch` and eight child sheets are the reviewed revision. The PCB has deliberately NOT been updated, laid out or approved. Open the project afresh before inspecting it; do not save a stale schematic editor over these files.

`historical-before-final-review/`, `checks/`, `render/`, `backups/` and `source-data/` contain earlier records; they are not current fabrication deliverables. Old CSV BOMs and response plots were moved to the historical folder to prevent accidental use.

`tools/build_schematic.py`, `make_bom.py` and earlier scripts describe historical designs. Do not run them on the reviewed schematic. The scoped edit record is `tools/final_review_edit.py`; it starts from the preserved baseline and would overwrite subsequent manual edits. The final validation reads KiCad's exported netlist through `tools/verify_netlist.py` and `final_review_calculate.py`. The Markdown/JSON BOM generator is `tools/final_review_bom.py`.

Original project/PCB/source backup: `final-review/before-final-review.zip`. The `.kicad_pcb`, `.kicad_pro` and `.kicad_prl` were preserved byte-for-byte. No inventory reservations or purchases were made.
