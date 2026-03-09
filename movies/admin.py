from django.contrib import admin
from .models import Movie, Review, UserWithMostComment
from .views import get_most_user_and_comment
class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']
class UserWithMostCommentAdmin(admin.ModelAdmin):
    change_list_template = "movies/mostcomment.html"
    def has_add_permission(self, request):
        return False
    def changelist_view(self, request, extra_context = None):
        theuser, thecount = get_most_user_and_comment()
        extra_context = extra_context or {}
        extra_context["the_user"] = theuser
        extra_context["the_count"] = thecount
        return super().changelist_view(request, extra_context = extra_context)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
admin.site.register(UserWithMostComment, UserWithMostCommentAdmin)
