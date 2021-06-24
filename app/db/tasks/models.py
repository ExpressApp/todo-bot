"""Main models for storing task list bot data."""
from tortoise import fields
from tortoise.models import Model


class TaskModel(Model):
    id = fields.IntField(pk=True)
    title = fields.TextField()
    description = fields.TextField(null=True)
    assignee = fields.UUIDField(null=True)
    attachment = fields.ForeignKeyField("tasks.AttachmentModel", null=True)

    class Meta:
        table = "tasks"


class AttachmentModel(Model):
    id = fields.UUIDField(pk=True)
    filename = fields.TextField()

    class Meta:
        table = "tasks_attachments_meta"
