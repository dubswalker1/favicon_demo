from django.forms import ModelForm
from .models import Favicon

class FaviconForm(ModelForm):
	class Meta:
		model = Favicon
		#only allow edit of url field
		fields = ['url']

	# override save, make sure we don't enter duplicate urls
	def save(self, *args, **kwargs):
		existingModel = Favicon.objects.filter(url=self.Meta.model.url)
		if existingModel:
			self.Meta.model = existingModel
		return super(FaviconForm, self).save(*args, **kwargs)