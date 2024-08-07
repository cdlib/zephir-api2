from .extensions import db


class ZephirFiledata(db.Model):
    __tablename__ = "zephir_filedata"
    htid = db.Column("id", db.VARCHAR(38), primary_key=True)
    metadata_xml = db.Column("metadata", db.Text)
    metadata_json = db.Column(db.Text)