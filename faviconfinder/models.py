from django.db import models
from django.utils import timezone
from django.db import transaction
import pdb

class Favicon(models.Model):
	url = models.URLField(unique=True)
	fav_url = models.URLField(null=True, editable=False)
	created = models.DateTimeField('created on', editable=False)
	
	def __str__(self):
		return self.url

	@ transaction.atomic
	def save(self, *args, **kwargs):
		#pdb.set_trace()
		# concurrency concerns - avoid multiple entries with the same
		# url ... url is set to unique (above) but try to avoid
		# hitting that constraint

		entries = Favicon.objects.select_for_update().filter(url=self.url)
		if len(entries) > 0:
			existing_entry = entries[0]
			#update existing entry, return that
			existing_entry.fav_url = self.fav_url
			return existing_entry
		else:
			''' On save, update timestamp '''
			if not self.id:
				self.created = timezone.now()
		
		return super(Favicon, self).save(*args, **kwargs)
		
	def invalid_url():
		return "INVALID"
		