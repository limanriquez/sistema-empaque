from django import template


register=template.Library()

@register.inclusion_tag('tags_templates/initial_loader.html',takes_context=True)
def initial_loader(context):
	return {}

@register.inclusion_tag('tags_templates/initial_loader_hide.html',takes_context=True)
def initial_loader_hide(context):
	return {}
	
@register.filter('get_value_from_dict')
def get_value_from_dict(dict_data, key):
	"""
	usage example {{ your_dict|get_value_from_dict:your_key }}
	"""
	if key:
		value = dict_data.get(key)
		if value is not None:
			return value
		else:
			return "" 
