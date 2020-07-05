from django.contrib import admin
from .models import Categories, Journal

# Register your models here.

#With this I can manage/browse Categories in django admin page
class CategoriesAdmin(admin.ModelAdmin):
    readonly_fields = ('login', 'category', 'category_count')

    def category_count(self, obj):
        return obj.journal_set.count()

admin.site.register(Categories, CategoriesAdmin)

'''
#With this, additionally, in each category I see its matching Journal posts
class JournalAdmin(admin.TabularInline):
    model = Journal
class CategoriesAdmin(admin.ModelAdmin):
    inlines = (JournalAdmin,)

admin.site.register(Categories, CategoriesAdmin)
'''