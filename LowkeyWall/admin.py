from django.contrib import admin
from .models import Confession, Comment, Quote, SupportPlan, Reply, Upvote

@admin.register(Confession)
class ConfessionAdmin(admin.ModelAdmin):
    list_display = ('topic', 'created_at', 'upvote_count_display', 'is_featured')
    list_filter = ('topic', 'is_featured', 'created_at')
    search_fields = ('topic', 'message')

    def upvote_count_display(self, obj):
        return obj.upvote_count  # ✅ Use `.upvote_count` (the @property)

    upvote_count_display.short_description = 'Upvotes'

admin.site.register(Comment)
admin.site.register(Quote)
admin.site.register(Reply)
admin.site.register(Upvote)

@admin.register(SupportPlan)
class SupportPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_usd']







