from django.db import models


class DifyModel(models.Model):
    query = models.TextField(
        verbose_name="質問内容",
        max_length=300,
    )
    answer = models.CharField(
        verbose_name="回答",
        max_length=2500
    )
    conversation_id = models.CharField(
        max_length=300,
    )
    created_at = models.DateTimeField(
        verbose_name="日時",
        auto_now_add=True
    )
    def __str__(self):
        return f"{self.query} - {self.conversation_id}"