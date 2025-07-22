from django.db import models
import random
from django.urls import reverse

# --- Choice Definitions ---

TOPIC_CHOICES = [
    ('Love', 'Love'),
    ('Career', 'Career'),
    ('Life', 'Life'),
    ('Family', 'Family'),
    ('School', 'School'),
    ('Other', 'Other'),
    ('Mental Health', 'Mental Health'),
    ('Friendship', 'Friendship'),
    ('Finance', 'Finance'),
    ('Addiction', 'Addiction'),
    ('Loneliness', 'Loneliness'),
    ('Relationships', 'Relationships'),
    ('Spirituality', 'Spirituality'),
    ('Success', 'Success'),
    ('Failure', 'Failure'),
    ('Secrets', 'Secrets'),
]

FEELING_CHOICES = [
    ('Happy', 'Happy'),
    ('Sad', 'Sad'),
    ('Angry', 'Angry'),
    ('Confused', 'Confused'),
    ('Anxious', 'Anxious'),
    # Add more if you want
]

PLAN_CHOICES = [
    ('basic', 'Supporter'),
    ('premium', 'Contributor'),
    ('ultimate', 'Patron'),
]

# --- Models ---

class Quote(models.Model):
    text = models.TextField()
    author = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.author}: {self.text[:50]}"

class Confession(models.Model):
    topic = models.CharField(max_length=100, choices=TOPIC_CHOICES)
    message = models.TextField(max_length=2000)
    feeling = models.CharField(max_length=20, choices=FEELING_CHOICES)
    anonymous = models.BooleanField(default=True)
    ai_response_requested = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    display_name = models.CharField(max_length=50, blank=True)
    upvoted_ips = models.JSONField(default=list, blank=True)
    session_owner = models.CharField(max_length=40, blank=True, null=True)
    is_featured = models.BooleanField(default=False)

    @property
    def upvote_count(self):
        return self.upvotes.count()

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = f"Anonymous #{random.randint(100, 999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.topic} ({self.display_name})"




class Comment(models.Model):
    confession = models.ForeignKey(Confession, on_delete=models.CASCADE)
    text = models.TextField()
    is_author = models.BooleanField(default=False)  # ✅ MUST be here
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.confession.id} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"



class Reply(models.Model):
    confession = models.ForeignKey(Confession, on_delete=models.CASCADE, related_name='replies')
    parent_comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_author = models.BooleanField(default=False)

    def __str__(self):
        return f"Reply to Confession {self.confession.id}"


    def get_reply_url(self):
        return reverse('post_reply', kwargs={
            'confession_id': self.confession.id,
            'parent_id': self.id
        })



class Upvote(models.Model):
    confession = models.ForeignKey(Confession, on_delete=models.CASCADE, related_name='upvotes')
    session_key = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('confession', 'session_key')

    def __str__(self):
        return f"Upvote for Confession {self.confession.id} by Session {self.session_key}"

class SupportPlan(models.Model):
    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    price_usd = models.DecimalField(max_digits=6, decimal_places=2)
    perks = models.TextField(help_text="Comma-separated list of perks")

    def perk_list(self):
        return [perk.strip() for perk in self.perks.split(',')]

    def __str__(self):
        return self.get_name_display()

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

    


    











