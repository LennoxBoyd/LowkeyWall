from django.contrib import admin
from .models import Confession, Comment, Quote, SupportPlan, Reply, Upvote

@admin.register(Confession)
class ConfessionAdmin(admin.ModelAdmin):
    list_display = ['topic', 'created_at', 'anonymous']
    search_fields = ['message']
    list_filter = ['topic', 'created_at']

admin.site.register(Comment)
admin.site.register(Quote)
admin.site.register(Reply)
admin.site.register(Upvote)

@admin.register(SupportPlan)
class SupportPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_usd']


