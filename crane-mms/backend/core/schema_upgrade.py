from sqlalchemy import inspect, text


EQUIPMENT_COLUMNS = {
    "manufacturer": "ALTER TABLE equipments ADD COLUMN manufacturer VARCHAR(100)",
    "applied_template_id": "ALTER TABLE equipments ADD COLUMN applied_template_id INTEGER",
    "applied_template_version": "ALTER TABLE equipments ADD COLUMN applied_template_version INTEGER",
    "submit_as_template_candidate": "ALTER TABLE equipments ADD COLUMN submit_as_template_candidate BOOLEAN DEFAULT 0",
    "inspection_items_json": "ALTER TABLE equipments ADD COLUMN inspection_items_json TEXT",
}


def ensure_runtime_schema(engine):
    inspector = inspect(engine)
    if "equipments" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("equipments")}
    missing_statements = [sql for column, sql in EQUIPMENT_COLUMNS.items() if column not in existing_columns]
    if not missing_statements:
        return

    with engine.begin() as connection:
        for statement in missing_statements:
            connection.execute(text(statement))
