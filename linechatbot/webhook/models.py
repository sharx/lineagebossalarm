from django.db import models

# Create your models here.

#create a model for the boss list
class Boss(models.Model):
    boss_name = models.CharField(max_length=100)
    respond_duration = models.IntegerField(blank=True, null=True)
    slug = models.CharField(max_length=200,blank=True, null=True)
    def __str__(self):
        return self.boss_name

#create a model for the line group properties
class LineGroup(models.Model):
    group_id = models.CharField(max_length=100)

    def __str__(self):
        return self.group_id

#create a model for the kill record of the boss
class KillRecord(models.Model):
    boss = models.ForeignKey(Boss, on_delete=models.CASCADE)
    line_group = models.ForeignKey(LineGroup, on_delete=models.CASCADE)
    responds_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s_%s_%s"%(self.line_group.group_id, self.boss.boss_name, str(self.responds_time) )
    
class TextRecord(models.Model):
    line_group = models.ForeignKey(LineGroup, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    inbound_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s_%s_%s"%(self.line_group.group_id, self.text, str(self.inbound_datetime) )