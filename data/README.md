# Local Data

Place authorized source files under `data/raw/` and locally generated partitions under `data/processed/`. These locations are ignored by Git. Create them locally as needed.

Follow the applicable PhysioNet credentialing, data-use, storage, and sharing requirements. Do not commit raw notes, derived note-level data, identifiers, notebook outputs containing note text, or generated note-level predictions. Keep synthetic fixtures in `tests/` instead of copying real examples into the repository.

Before processing data, record the resource/version, selected note type, target pairing, inclusion rules, and split strategy in the project documentation without including restricted content.
