from django import template
register = template.Library()

@register.filter
def index(indexable, i):
    return indexable[i]

@register.filter
def format_seconds(sec):
   if sec == None:
       return 'No Eta'
   sec = int(sec)
   sec = sec % (24 * 3600)
   hour = sec // 3600
   sec %= 3600
   min = sec // 60
   sec %= 60
   return "%02d:%02d:%02d" % (hour, min, sec) 