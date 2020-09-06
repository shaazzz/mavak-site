from django.db import models
from django.contrib.auth.models import User


class Comment(models.Model):
    class Meta:
        ordering = ["-date"]

    private = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    text = models.TextField()
    answered = models.BooleanField(default=False)
    root = models.CharField(max_length=250)

    def get_message(self):
        line2 = ""
        last_line = "\n\nپاسخ داده نشده!"
        if self.answered:
            last_line = ""
        if self.parent is not None and self.parent != "":
            line2 = "in reply to:" + str(self.parent.id) + "\n"
        return str(self.id) + "\n" + line2 + \
               "mavak.shaazzz.ir/" + \
               str(self.root).replace("-", "\\-") + "\n" + str(self.sender.first_name) \
               + " " + str(self.sender.last_name) \
               + ":\n" + str(self.text) + last_line
